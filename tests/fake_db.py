import json
import random
from pathlib import Path
from datetime import date, timedelta
from pycounter.config import yaml_config_loader

def generate_fake_db(num_records=10, num_orders=5):
    app_config = yaml_config_loader('pycounter/config.yaml')
    data = {}
    data[app_config.mind.collection] = {}
    ref_day = date.today()
    random_orders = [str(random.randint(1_000_000, 9_999_999)) for _ in range(num_orders)]

    for i in range(num_records):
        num_day_orders = random.randint(1, num_orders)
        random_order_indices = [random.randint(0, num_orders - 1) for _ in range(num_day_orders)]

        day_orders = [random_orders[oid] for oid in random_order_indices]
        day_orders.insert(0, app_config.mind.defaultorder)


        day_elapsed = timedelta(hours=random.uniform(6, 10)).total_seconds()

        orders_elapsed = [random.random() for _ in range(num_day_orders)]
        total_sum = sum(orders_elapsed)
        normalized = [(e / total_sum) * day_elapsed for e in orders_elapsed]

        orders_data = dict(zip(day_orders, normalized))

        current_day = ref_day + timedelta(days=i)

        day_record = {
            "day": date.strftime(current_day, '%Y%m%d'),
            "elapsed": day_elapsed,
            "orders": orders_data
        }

        data[app_config.mind.collection][str(i)] = day_record
    
    json.dump(
        data, 
        Path(app_config.mind.database).with_suffix('.json').open('w'), 
        indent=2
    )

if __name__ == '__main__':
    generate_fake_db(num_records=20, num_orders=5)
