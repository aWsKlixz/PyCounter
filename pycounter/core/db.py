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


class PrettyJSONStorage(JSONStorage):
    """
    Custom TinyDB storage that pretty-prints JSON files with indentation.
    Useful for easier manual reading and debugging.
    """
    def _write(self, data):
        self._handle.seek(0)
        self._handle.write(json.dumps(data, indent=2))
        self._handle.truncate()


class Mind:
    """
    A class to track daily activities and order-specific work durations.

    This class stores per-day total work time and tracks how much time is spent on each order,
    storing all data in a local TinyDB database.
    """

    config: AppConfig
    day_format: str = '%Y%m%d'
    current_order: str = ""
    order_start_time: datetime = datetime.now()

    @property
    def day_id(self) -> str:
        """
        Returns the current date formatted as a string (default: YYYYMMDD).
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
        serialization = SerializationMiddleware()
        serialization.register_serializer(DateTimeSerializer(), 'TinyDate')

        # Initialize TinyDB and the specific table for storing daily data
        self.db = TinyDB(self.config.mind.Database, indent=2)
        self.collection = self.db.table(self.config.mind.collection)
        self.day_activity = Query()

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
            self.collection.update(
                lambda a: a.update({'elapsed': transformed_elapsed}),
                self.day_activity.day == self.day_id
            )
        else:
            self.collection.insert({
                'day': self.day_id,
                'elapsed': transformed_elapsed
            })

    def push(self):
        """
        Push the current order's duration to the activity record.
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
        columns = set()
        rows = set()

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
                total_elapsed = doc.get('elapsed', 0.0) / 3600  # in hours
                data[-1, col_idx] = round(total_elapsed, 1)

                orders = doc.get('orders', {})
                for order, seconds in orders.items():
                    row_idx = rows.index(order)
                    value = seconds / 3600
                    if format == 'perc' and total_elapsed > 0:
                        value = (value / total_elapsed) * 100
                    data[row_idx, col_idx] = round(value, 1)

        formatted_columns = [
            datetime.strptime(col, self.day_format).strftime('%d-%m-%Y')
            for col in columns
        ]

        return pd.DataFrame(data=data, columns=formatted_columns, index=rows)

    def report(
        self,
        format: Literal['hours', 'perc'] = 'hours',
        interval: Literal['total', 'month'] = 'total',
        file: str | None = None,
        open_report: bool = False
    ):
        """
        Generates an Excel report of recorded time usage.

        Args:
            format (str): 'hours' for time in hours or 'perc' for percentage view.
            interval (str): 'total' for all-time or 'month' for current month only.
            file (str, optional): Output file path. Temporary if None.
            open_report (bool): If True, opens the Excel file after creation.
        """
        data = self.build_data(format=format)

        if interval == 'month':
            current_month = datetime.now().month
            data = data.loc[:, data.columns.to_series().apply(
                lambda d: datetime.strptime(d, '%d-%m-%Y').month == current_month
            )]

        if file is None:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                file = tmp.name

        data.to_excel(file)

        if open_report:
            webbrowser.open(f'file://{file}')
