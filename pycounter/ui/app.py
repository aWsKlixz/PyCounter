from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow,
    QVBoxLayout, QSystemTrayIcon
)
from PyQt5.QtGui import QIcon

from config import AppConfig

from core.db import Mind
from core.activitymanager import ActivityManager

from ui.timerpanel import TimerPanel
from ui.activities import ActivityPanel
from ui.tray import TrayCounter

class CounterApp(QMainWindow):
    """
    Main GUI class for the time tracking application.

    This app displays a timer and an activity tracking panel.
    It supports starting, pausing, resetting time, and automatically
    updates tracked activity when the application closes.
    """

    # ui properties
    timer_panel: TimerPanel
    tracker_panel: ActivityPanel
    tray_icon: TrayCounter
    central_widget: QWidget

    # logic and db
    mind: Mind
    activity_manager: ActivityManager



    @property
    def base_widget_arguments(self):
        return [self.config, self.mind, self.activity_manager]

    def __init__(self, config: AppConfig = AppConfig()):
        """
        Initialize the main application window.

        Args:
            config (AppConfig): Configuration object for window size, assets, etc.
        """
        super().__init__()

        # setup the "backend"
        self.config = config
        self.mind = Mind(self.config)
        self.activity_manager = ActivityManager(self.config, self)

        self.setWindowIcon(QIcon(str(self.config.assets.Icon)))  # Set window icon

        self._init_ui()

        self.tray_icon = TrayCounter(
            QIcon(
                str(self.config.assets.Icon)
            ), 
            mgr=self.activity_manager, 
            parent=self
        )

        # Ensure app state is saved before quitting
        self.app = QApplication.instance()
        self.app.aboutToQuit.connect(self.on_exit)

        self.tray_icon.showMessage("PyCounter", "Timer Loaded!", QSystemTrayIcon.Information, 5000)

    def _init_ui(self):
        """
        Set up the entire user interface, including window settings,
        main layout, timer widget, and activity panel.
        """
        self.setWindowTitle("PyCounter - Keep an eye on your Time!")

        # Configure window dimensions
        width, height = self.config.window.width, self.config.window.height
        self.setGeometry(100, 100, width, height)
        self.setFixedSize(width, height)
        self._move_window_to_bottom_right(width, height)

        # Create central layout and populate it
        self.central_widget = QWidget(self)
        central_layout = QVBoxLayout()

        # Timer and control buttons
        self.timer_panel = TimerPanel(*self.base_widget_arguments, self)

        # Activity tracker panel
        self.tracker_panel = ActivityPanel(*self.base_widget_arguments, self.central_widget)

        # assemble
        # Add widgets to layout
        central_layout.addWidget(self.timer_panel)
        central_layout.addWidget(self.tracker_panel)

        self.central_widget.setLayout(central_layout)
        self.setCentralWidget(self.central_widget)

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

    def on_exit(self):
        """
        Perform final operations before exiting the app.

        Ensures that the timer is paused and tracked time is pushed to storage.
        """
        self.timer_panel.btn_reset.click()      # Ensure timer is paused/stopped
        self.tracker_panel.btn_push.click()     # Manually trigger push action
