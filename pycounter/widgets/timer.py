from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QSystemTrayIcon, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
from datetime import datetime, timedelta

from widgets.basewidget import BaseWidget
from config import AppConfig

class TimerWidget(BaseWidget):

    information_shown = False
    warning_shown = False
    critical_shown = False

    def __init__(self, config: AppConfig, parent=None):
        super().__init__(config=config, parent=parent)

        self.information_shown = False
        self.warning_shown = False
        self.critical_shown = False

        self.lbl_time = QLabel("00:00:00", self)
        self.lbl_time.setStyleSheet("font-size: 24px;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)

        self.start_time: datetime | None = None  # None at first
        self.elapsed: timedelta = timedelta()
        self.running = False

        # tray icon
        self.tray_icon = QSystemTrayIcon(QIcon(str(self.config.assets.Icon)), self)
        # self.tray_icon.setToolTip("PyCounter - Keep an eye on your time!")
        self.tray_icon.setVisible(True)

        self.init_ui()

        self.tray_icon.showMessage("PyCounter", "Timer Laoded!", QSystemTrayIcon.Information, 5000)

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.lbl_time)
        self.setLayout(layout)

    def update_time(self):
        if self.running and self.start_time:
            now = datetime.now()
            self.elapsed = now - self.start_time
            self.lbl_time.setText(str(self.elapsed).split('.')[0])  # HH:MM:SS
            self.check_for_alerts()

    def toggle(self, button: QPushButton):
        if self.running:
            # Pause the timer
            self.timer.stop()
            self.elapsed = datetime.now() - self.start_time
            self.start_time = None
            button.setIcon(QIcon(str(self.config.assets.Play)))
            button.setText("Resume")
        else:
            # Resume the timer
            self.start_time = datetime.now() - self.elapsed
            self.timer.start(1000)
            button.setIcon(QIcon(str(self.config.assets.Pause)))
            button.setText("Pause")
        self.running = not self.running

    def reset(self, button: QPushButton):
        self.timer.stop()
        self.start_time = None
        self.elapsed = timedelta()
        self.lbl_time.setText("00:00:00")
        self.running = False
        button.setIcon(QIcon(str(self.config.assets.Play)))
        button.setText("Start")
        self.information_shown = False
        self.warning_shown = False
        self.critical_shown = False

    def check_for_alerts(self):
        if self.elapsed >= timedelta(**self.config.notifications.information) and self.information_shown == False:
            self.tray_icon.setVisible(True)
            self.show_alert("Finish now!", QSystemTrayIcon.Information)
            self.information_shown = True

        if self.elapsed >= timedelta(**self.config.notifications.warning) and self.warning_shown == False:
            self.tray_icon.setVisible(True)
            self.show_alert("Tomorrow is a new day!", QSystemTrayIcon.Warning)
            self.warning_shown = True

        if self.elapsed >= timedelta(**self.config.notifications.critical) and self.critical_shown == False:
            self.tray_icon.setVisible(True)
            self.show_alert("GO HOME NOW!", QSystemTrayIcon.Critical)
            self.critical_shown = True

    def show_alert(self, message: str, icon: QSystemTrayIcon = QSystemTrayIcon.Information):
        self.tray_icon.showMessage("Alert", message, icon, 10000)