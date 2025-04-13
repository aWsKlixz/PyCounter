import os
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from pycounter.app import CounterApp
from pycounter.config import yaml_config_loader

def main():
    """
    Entry point of the PyCounter application.

    This function performs the following:
    - Loads the configuration from a YAML file (handling both frozen and dev environments)
    - Initializes the Qt application
    - Sets the window icon and application stylesheet
    - Launches the main application window
    """

    # Determine the path to the configuration file based on the environment
    # If running as a frozen app (e.g., via PyInstaller), use the embedded resource path
    if getattr(sys, 'frozen', False):
        config_path = os.path.join(sys._MEIPASS, 'config.yaml')  # PyInstaller temp path
    else:
        config_path = 'pycounter/config.yaml'  # Default path during development

    # Load configuration using a custom YAML loader
    app_config = yaml_config_loader(config_path)

    # Initialize the Qt application
    app = QApplication(sys.argv)

    # Set application window icon
    app.setWindowIcon(QIcon(str(app_config.assets.Icon)))

    # Apply custom stylesheet from configuration
    with app_config.assets.Stylesheet.open('r') as stylesheet_file:
        app.setStyleSheet(stylesheet_file.read())

    # Create and display the main window
    window = CounterApp(config=app_config)
    window.show()

    # Execute the application's event loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    # Only run main if this script is executed directly
    main()
