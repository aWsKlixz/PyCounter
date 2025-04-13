from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QSystemTrayIcon,
    QPushButton, QMenu, QAction
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
from datetime import datetime, timedelta

from pycounter.widgets.basewidget import BaseWidget
from pycounter.widgets.menu import AppMenu
from pycounter.config import AppConfig


class TimerWidget(BaseWidget):
    """
    A widget that functions as a timer with visual output, alerts, and tray notifications.

    Attributes:
        information_shown (bool): Tracks if the information alert has been shown.
        warning_shown (bool): Tracks if the warning alert has been shown.
        critical_shown (bool): Tracks if the critical alert has been shown.
    """

    information_shown = False
    warning_shown = False
    critical_shown = False

    def __init__(self, config: AppConfig, parent=None):
        """
        Initialize the timer widget and system tray icon.

        Args:
            config (AppConfig): The application configuration.
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(config=config, parent=parent)

        # Reset alert flags
        self.information_shown = False
        self.warning_shown = False
        self.critical_shown = False

        # Time tracking
        self.lbl_time = QLabel("00:00:00", self)
        self.start_time: datetime | None = None
        self.elapsed: timedelta = timedelta()
        self.running = False

        # Timer for updating display
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)

        # System tray icon setup
        self.tray_icon = QSystemTrayIcon(QIcon(str(self.config.assets.Icon)), self)
        self.tray_icon.setToolTip("PyCounter - Keep an eye on your time!")
        self.tray_icon.setVisible(True)

        # Attach context menu to tray icon
        menu = AppMenu(self)
        self.tray_icon.setContextMenu(menu)

        # Build UI layout
        self.init_ui()

        # Welcome notification
        self.tray_icon.showMessage("PyCounter", "Timer Loaded!", QSystemTrayIcon.Information, 5000)

    def init_ui(self):
        """Initialize and arrange UI elements."""
        layout = QVBoxLayout()
        layout.addWidget(self.lbl_time)
        self.setLayout(layout)

    def update_time(self):
        """
        Update the label with the current elapsed time
        and check for notifications.
        """
        if self.running and self.start_time:
            now = datetime.now()
            self.elapsed = now - self.start_time
            self.lbl_time.setText(str(self.elapsed).split('.')[0])  # Format: HH:MM:SS
            self.check_for_alerts()

    def toggle(self, button: QPushButton):
        """
        Start or pause the timer depending on its current state.

        Args:
            button (QPushButton): The button triggering the toggle.
        """
        if self.running:
            # Pause the timer
            self.timer.stop()
            self.elapsed = datetime.now() - self.start_time
            self.start_time = None
            button.setIcon(QIcon(str(self.config.assets.Play)))
            button.setText("Resume")

            # Save session to the database
            self.mind.update(self.elapsed)
        else:
            # Resume the timer
            self.start_time = datetime.now() - self.elapsed
            self.timer.start(1000)
            button.setIcon(QIcon(str(self.config.assets.Pause)))
            button.setText("Pause")

        self.running = not self.running

    def reset(self, button: QPushButton):
        """
        Reset the timer to 0 and clear all states.

        Args:
            button (QPushButton): The button triggering the reset.
        """
        self.timer.stop()
        self.start_time = None
        self.elapsed = timedelta()
        self.lbl_time.setText("00:00:00")
        self.running = False

        # Reset button visuals
        button.setIcon(QIcon(str(self.config.assets.Play)))
        button.setText("Start")

        # Reset all alert states
        self.information_shown = False
        self.warning_shown = False
        self.critical_shown = False

        # Update the database with zeroed time
        self.mind.update(timedelta(seconds=0.0))

    def check_for_alerts(self):
        """
        Show desktop notifications based on elapsed time
        and configured alert thresholds.
        """
        if self.elapsed >= timedelta(**self.config.notifications.information) and not self.information_shown:
            self.show_alert("Finish now!", QSystemTrayIcon.Information)
            self.information_shown = True

        if self.elapsed >= timedelta(**self.config.notifications.warning) and not self.warning_shown:
            self.show_alert("Tomorrow is a new day!", QSystemTrayIcon.Warning)
            self.warning_shown = True

        if self.elapsed >= timedelta(**self.config.notifications.critical) and not self.critical_shown:
            self.show_alert("GO HOME NOW!", QSystemTrayIcon.Critical)
            self.critical_shown = True

    def show_alert(self, message: str, icon: QSystemTrayIcon = QSystemTrayIcon.Information):
        """
        Display a system tray notification.

        Args:
            message (str): The message to show in the notification.
            icon (QSystemTrayIcon.MessageIcon): The type of notification icon.
        """
        self.tray_icon.showMessage("Alert", message, icon, 10000)
