from typing import Literal
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QGridLayout, QMainWindow,
    QPushButton, QVBoxLayout, QLabel, QLineEdit
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QSize

from pycounter.config import AppConfig
from pycounter.widgets.basewidget import BaseWidget
from pycounter.widgets.timer import TimerWidget
from pycounter.widgets.activities import ActivityPanel


class CounterApp(QMainWindow, BaseWidget):
    """
    Main GUI class for the time tracking application.

    This app displays a timer and an activity tracking panel.
    It supports starting, pausing, resetting time, and automatically
    updates tracked activity when the application closes.
    """

    tracker_panel: ActivityPanel

    def __init__(self, config: AppConfig = AppConfig()):
        """
        Initialize the main application window.

        Args:
            config (AppConfig): Configuration object for window size, assets, etc.
        """
        super().__init__(config=config)
        self.config = config
        self.setWindowIcon(QIcon(str(self.config.assets.Icon)))  # Set window icon

        self._init_ui()

        # Ensure app state is saved before quitting
        self.app = QApplication.instance()
        self.app.aboutToQuit.connect(self.on_exit)

    def _init_ui(self):
        """
        Set up the entire user interface, including window settings,
        main layout, timer widget, and activity panel.
        """
        self.setWindowTitle("Counter App - Keep an eye on your Time!")

        # Configure window dimensions
        width, height = self.config.window.width, self.config.window.height
        self.setGeometry(100, 100, width, height)
        self.setFixedSize(width, height)
        self._move_window_to_bottom_right(width, height)

        # Create central layout and populate it
        central_widget = QWidget(self)
        central_layout = QVBoxLayout()

        # Timer and control buttons
        counter_frame = self._create_counter_frame()

        # Activity tracker panel
        self.tracker_panel = ActivityPanel(self.config, central_widget)

        # Add widgets to layout
        central_layout.addWidget(counter_frame)
        central_layout.addWidget(self.tracker_panel)

        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

    def _move_window_to_bottom_right(self, w: int, h: int):
        """
        Move the window to the bottom-right corner of the primary screen.

        Args:
            w (int): Width of the window.
            h (int): Height of the window.
        """
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        x = screen_geometry.width() - w
        y = screen_geometry.height() - h
        self.move(x, y)

    def _create_counter_frame(self) -> QWidget:
        """
        Create the upper section of the window containing the timer and control buttons.

        Returns:
            QWidget: Frame widget containing the timer and buttons.
        """
        frame = QWidget(self)
        layout = QHBoxLayout()

        # Timer widget on the left
        self.timer_widget = TimerWidget(config=self.config, parent=frame)
        layout.addWidget(self.timer_widget)

        # Control buttons on the right
        button_panel = self._create_button_panel()
        layout.addWidget(button_panel)

        frame.setLayout(layout)
        return frame

    def _create_button_panel(self) -> QWidget:
        """
        Create the control buttons for the timer (Start/Pause and Reset).

        Returns:
            QWidget: Frame widget containing the control buttons.
        """
        button_frame = QWidget(self)
        layout = QGridLayout()

        # Start/Pause Button
        self.play_pause_button = QPushButton("Start", self)
        self._set_icon(self.play_pause_button, 'Play')
        self.play_pause_button.clicked.connect(
            lambda: self.timer_widget.toggle(self.play_pause_button)
        )
        layout.addWidget(self.play_pause_button, 0, 0)

        # Reset Button
        self.reset_button = QPushButton("Reset", self)
        self._set_icon(self.reset_button, 'Reset')
        self.reset_button.clicked.connect(
            lambda: self.timer_widget.reset(self.play_pause_button)
        )
        layout.addWidget(self.reset_button, 0, 1)

        button_frame.setLayout(layout)
        return button_frame

    def on_exit(self):
        """
        Perform final operations before exiting the app.

        Ensures that the timer is paused and tracked time is pushed to storage.
        """
        self.play_pause_button.click()  # Ensure timer is paused/stopped
        self.tracker_panel.btn_push.click()           # Manually trigger push action
