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
                lambda a: a.update({'elapsed': transformed_elapsed}),
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
                if isinstance((orders := doc.get('orders')), dict):
                    rows.update(orders.keys())

        rows = list(rows)
        rows.append('total elapsed')
        columns = list(columns)

        data = np.zeros((len(rows), len(columns)))

        # Populate the matrix with hours or percentages
        for doc in self.collection.all():
            if (day := doc.get('day')):
                col_idx = columns.index(day)
                total_elapsed = doc.get_
