import json
import numpy as np
import pandas as pd
import tempfile
import webbrowser
from typing import Literal
from datetime import timedelta, date, datetime
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer

from config import AppConfig


class Mind:
    """
    A class to track daily activities and order-specific work durations.

    This class stores per-day total work time and tracks how much time is spent on each order,
    storing all data in a local TinyDB database.
    """

    config: AppConfig
    day_format: str = '%Y%m%d'  # Format for storing the day as YYYYMMDD
    current_order: str = ""  # Tracks the current active order
    order_start_time: datetime = datetime.now()  # The timestamp when the current order starts

    @property
    def day_id(self) -> str:
        """
        Returns the current date formatted as a string (default: YYYYMMDD).

        Returns:
            str: The current date as a string in the format YYYYMMDD.
        """
        return date.today().strftime(self.day_format)

    def __init__(self, config: AppConfig):
        """
        Initialize the Mind instance with a given AppConfig.
        Sets up the TinyDB with datetime serialization.

        Args:
            config (AppConfig): Application configuration with DB details.
        """
        self.config = config
        # Setup serialization middleware for TinyDB to handle datetime serialization
        serialization = SerializationMiddleware()
        serialization.register_serializer(DateTimeSerializer(), 'TinyDate')

        # Initialize TinyDB with the specified database and collection
        self.db = TinyDB(self.config.mind.Database, indent=2)
        self.collection = self.db.table(self.config.mind.collection)
        self.day_activity = Query()  # For querying activities by day

    def get_activity_suggestions(self):
        """
        Retrieves all unique activity names (orders) from the stored database.

        Returns:
            set: A set containing all unique activity (order) names from the stored data.
        """
        all_activities = set()
        docs = self.collection.all()
        # Collect all activity names from the stored documents
        for doc in docs:
            day_activities = doc.get('orders', {})
            all_activities.update(day_activities.keys())
        return all_activities

    def get_current_activity(self) -> dict | None:
        """
        Retrieves the current day's activity from the database.

        Returns:
            dict | None: The activity entry if it exists, else None.
        """
        activity = self.collection.search(self.day_activity.day == self.day_id)
        return activity[0] if activity else None

    def get_current_elapsed_time(self) -> timedelta:
        """
        Get the total elapsed time for the current day.

        Returns:
            timedelta: The time elapsed today.
        """
        activity = self.get_current_activity()
        elapsed_seconds = activity.get('elapsed', 0.0) if activity else 0.0
        return timedelta(seconds=elapsed_seconds)

    def update(self, elapsed: timedelta):
        """
        Update or insert the elapsed time for the current day.

        Args:
            elapsed (timedelta): The new total elapsed time to store.
        """
        transformed_elapsed = elapsed.total_seconds()
        day_activity = self.get_current_activity()

        if day_activity:
            # Update the elapsed time in the current day's record
            self.collection.update(
                lambda a: a.update({'elapsed': transformed_elapsed}), # type: ignore
                self.day_activity.day == self.day_id
            )
        else:
            # Insert a new record for the current day with the elapsed time
            self.collection.insert({
                'day': self.day_id,
                'elapsed': transformed_elapsed
            })

    def push(self):
        """
        Push the current order's duration to the activity record.

        This method updates the time spent on the current order and stores it
        in the database under the 'orders' field.
        """
        activity = self.get_current_activity()

        if self.current_order and activity:
            activity_orders = activity.get('orders', {})
            elapsed_order = datetime.now() - self.order_start_time

            # Update or insert elapsed time for the current order
            activity_orders[self.current_order] = activity_orders.get(
                self.current_order, 0
            ) + elapsed_order.total_seconds()

            self.collection.update(
                {'orders': activity_orders},
                self.day_activity.day == self.day_id
            )

    def build_data(self, format: Literal['hours', 'perc'] = 'hours') -> pd.DataFrame:
        """
        Builds a pandas DataFrame summarizing all stored activities.

        Args:
            format (str): Either 'hours' to show hours worked or 'perc' to show % per order.

        Returns:
            pd.DataFrame: A table where columns are dates and rows are order names and total elapsed.
        """
        columns = set()  # Stores all unique day IDs
        rows = set()     # Stores all unique order names

        # Collect all day IDs and all unique order names
        for doc in self.collection.all():
            if (day := doc.get('day')):
                columns.add(day)
                if isinstance((orders := doc.get('orders', None)), dict):
                    rows.update(orders.keys())

        rows = list(rows)
        rows.append(self.config.mind.defaultorder)
        rows.append('total elapsed')
        columns = list(columns)
        
        data = np.zeros((len(rows), len(columns)))

        # Populate the matrix with hours or percentages
        for document in self.collection.all():
             day_id = document.get('day', None)
             if day_id:
                col_idx = columns.index(day_id)
 
                total_elapsed = document.get('elapsed', 0.0) / (60 * 60)       # convert to hours
                
               

                orders = document.get('orders', {})
                if isinstance(orders, dict):
                    if np.isclose(total_elapsed, 0.0):
                        total_elapsed = np.sum(list(orders.values()))
                    for order, order_elapsed in orders.items():
                        row_idx = rows.index(order)
                        formatted_order_elapsed = order_elapsed / (60 * 60)    # convert to hours
                        if format == 'perc':
          
                            data[-1, col_idx] = round(total_elapsed, 1)
                            formatted_order_elapsed = (formatted_order_elapsed / total_elapsed) * 1e2 

                        data[row_idx, col_idx] = round(formatted_order_elapsed, 1)

        # fill by default order
        data[-2, :] = np.round(data[-1, :] - np.sum(data[:-2], axis=0),1) if format == 'hours' else np.round(100 - np.sum(data[:-2], axis=0), 1)
        # build the colum with total worked per order
        # data[:, -1] = np.sum(data, axis=1)

        # format columns for printing
        formatted_columns = [
            datetime.strptime(col, self.day_format).strftime('%d-%m-%Y')
            for col in columns
        ]
         
        data = pd.DataFrame(
             data=data, columns=formatted_columns, index=rows
        )
          
        return data
    
    def report(
            self,
            format: Literal['hours', 'perc'] = 'hours',
            interval: Literal['total', 'month'] = 'total',
            file: str | None = None,
            open_report: bool = True
    ):
        """
        Generates a report of the activities stored in the database.

        Args:
            format (str): Either 'hours' to show hours worked or 'perc' to show % per order.
            interval (str): Either 'total' for all time or 'month' for the current month.
            open_report (bool): If True, opens the report in a web browser.
        """
        data = self.build_data(format=format)
        
        if interval == 'month':
            # Filter the DataFrame to only include the current month
            current_month = datetime.now().month
            def filter_columns_by_current_month(column_name):
                column_date = datetime.strptime(column_name, '%d-%m-%Y')
                return column_date.month == current_month
            data = data.loc[:, data.columns.to_series().apply(filter_columns_by_current_month)]

        if file is None:
            # Create a temporary file to store the report
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                file = tmp_file.name
        
        # rearange the columns to be in the order of the day
        data = data[sorted(data.columns, key=lambda day: pd.to_datetime(day, format='%d-%m-%Y'))]
        # Save the DataFrame to an Excel file
        data.to_excel(file)

        if open_report:
            # Open the report in the default web browser
            webbrowser.open(f'file://{file}')