import unittest
from pathlib import Path
from pycounter.config import yaml_config_loader
from pycounter.core.db import Mind
import pandas as pd

class TestPyCounter(unittest.TestCase):

    def test_yaml_config_loader(self):
        from pycounter.config import AppConfig
        config_path = Path("pycounter/config.yaml")
        config = yaml_config_loader(str(config_path))

        self.assertIsInstance(config, AppConfig)
       

    def test_mind_build_data(self):
        config = yaml_config_loader("pycounter/config.yaml")
        mind = Mind(config=config)
        data = mind.build_data()

        self.assertIsInstance(data, pd.DataFrame)
        self.assertGreaterEqual(len(data), 0)

    def test_export_to_excel(self):
        config = yaml_config_loader("pycounter/config.yaml")
        mind = Mind(config=config)

        mind.report(format="perc", interval="month")

if __name__ == "__main__":
    unittest.main()
