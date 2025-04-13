import json
import numpy as np
import pandas as pd
from typing import Literal
from datetime import timedelta, date, datetime
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer

from pycounter.config import AppConfig

class PrettyJSONStorage(JSONStorage):
    def _write(self, data):
        self._handle.seek(0)
        self._handle.write(json.dumps(data, indent=2))
        self._handle.truncate()

class Mind:

    config: AppConfig 

    day_format: str = '%Y%m%d'

    current_order: str = ""
    order_start_time: datetime = datetime.now()

    @property
    def day_id(self):
        return date.today().strftime(self.day_format)

    def __init__(self, config: AppConfig):
        self.config = config
        serialization = SerializationMiddleware()
        serialization.register_serializer(DateTimeSerializer(), 'TinyDate')
        self.db = TinyDB(self.config.mind.database + '.json', indent=2)
        self.collection = self.db.table(self.config.mind.collection)
        self.day_activity = Query()

    def get_current_activity(self):
        activity = self.collection.search(self.day_activity.day == self.day_id)
        if len(activity) > 0:
            return activity[0]
        else:
            return None
        
    def get_current_elapsed_time(self):
        current_activity = self.get_current_activity()
        if current_activity:
            current_activity = current_activity[0]
            elapsed_seconds = current_activity.get('elapsed', 0.0)
            return timedelta(seconds=elapsed_seconds)
        else:
            return timedelta(seconds=0)

    def update(self, elapsed: timedelta):

        transformed_elapsed = elapsed.total_seconds()

        day_activity = self.get_current_activity()

        def add_timedelta(activity):
            activity['elapsed'] = transformed_elapsed

        if day_activity:
            self.collection.update(
                add_timedelta, self.day_activity.day == self.day_id
            )
        else:
            self.collection.insert({
                'day': self.day_id,
                'elapsed': transformed_elapsed
            })
    
    def push(self):
        
        activity = self.get_current_activity()
        
        activity_orders = activity.get('orders', {})

        elapsed_order = datetime.now() - self.order_start_time

        if self.current_order in activity_orders:
            activity_orders[self.current_order] += elapsed_order.total_seconds()
        else:
            activity_orders[self.current_order] = elapsed_order.total_seconds()
        
        self.collection.update(
            {'orders': activity_orders},
            self.day_activity.day == self.day_id
        )
    
    def build_data(self, format: Literal['hours', 'perc'] = 'hours'):

        # build column for each document
        # <day, total elapsed, orders:> 
        columns = set()
        rows = set()
        for document in self.collection.all():
            day_id = document.get('day', None)
            if day_id:
                
                columns.add(day_id)
                orders = document.get('orders', None)
                if isinstance(orders, dict):
                    rows.update(list(orders.keys()))

        columns = list(columns)
        rows = list(rows)
        rows.append('total elapsed')
        data = np.zeros((len(rows), len(columns)))

        for document in self.collection.all():
            day_id = document.get('day', None)
            if day_id:
                col_idx = columns.index(day_id)

                total_elapsed = document.get('elapsed', 0.0) / (60 * 60)# convert to hours
                    
                data[-1, col_idx] = round(total_elapsed, 1)

                orders = document.get('orders', {})
                if isinstance(orders, dict):
                    for order, order_elapsed in orders.items():
                        row_idx = rows.index(order)
                        formatted_order_elapsed = order_elapsed / (60 * 60)
                        if format == 'perc':
                            formatted_order_elapsed = (formatted_order_elapsed / total_elapsed) * 1e2 
                        data[row_idx, col_idx] = round(formatted_order_elapsed, 1)
        
        # format columns for printing
        formatted_columns = [datetime.strptime(col, self.day_format).strftime('%d-%m-%Y') for col in columns]
        data = pd.DataFrame(
            data=data, columns=formatted_columns, index=rows
        )

        return data
        
    def report(
            self, 
            format: Literal['hours', 'perc'] = 'hours',
            interval: Literal['total', 'month'] = 'total'
        ):
        
        data = self.build_data(format=format)

        if interval == 'month':
            current_month = datetime.now().month
            def filter_columns_by_current_month(col_name):
                column_date = datetime.strptime(col_name, '%d-%m-%Y')
                return column_date.month == current_month
            data = data.loc[:, data.columns.to_series().apply(filter_columns_by_current_month)]

        data.to_excel('report.xlsx')


