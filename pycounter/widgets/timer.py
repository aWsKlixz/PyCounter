from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QSystemTrayIcon
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
from datetime import datetime, timedelta

class TimerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.lbl_time = QLabel("00:00:00", self)
        self.lbl_time.setStyleSheet("font-size: 24px;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)

        self.start_time: datetime | None = None  # None at first
        self.elapsed: timedelta = timedelta()
        self.running = False

        # tray icon
        self.tray_icon = QSystemTrayIcon(QIcon('alert.png'), self)
        self.tray_icon.setVisible(True)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.lbl_time)
        self.setLayout(layout)

    def update_time(self):
        if self.running and self.start_time:
            now = datetime.now()
            self.elapsed = now - self.start_time
            self.lbl_time.setText(str(self.elapsed).split('.')[0])  # HH:MM:SS

    def toggle(self):
        if self.running:
            # Pause the timer
            self.timer.stop()
            self.elapsed = datetime.now() - self.start_time
            self.start_time = None
        else:
            # Resume the timer
            self.start_time = datetime.now() - self.elapsed
            self.timer.start(1000)
        self.running = not self.running

    def reset(self):
        self.timer.stop()
        self.start_time = None
        self.elapsed = timedelta()
        self.lbl_time.setText("00:00:00")
        self.running = False

    def check_for_alerts(self):
        if self.elapsed >= timedelta(hours=7):
            pass

    def show_alert(self, message: str):
        pass