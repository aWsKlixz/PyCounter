import os
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from pycounter.app import CounterApp
from pycounter.config import yaml_config_loader

def main():

    # Set up the application
    # Load the configuration
    if getattr(sys, 'frozen', False):
        config_path = os.path.join(sys._MEIPASS, 'config.yaml')
    else:
        config_path = 'pycounter/config.yaml'
    app_config = yaml_config_loader(config_path)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(app_config.assets.Icon)))
    app.setStyleSheet(app_config.assets.Stylesheet.open('r').read())

    window = CounterApp(config=app_config)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()