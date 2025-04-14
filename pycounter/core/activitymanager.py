from PyQt5.QtCore import QTimer, QObject, pyqtSignal
from datetime import timedelta, datetime
from config import AppConfig

class ActivityManager(QObject):
    
    config: AppConfig

    # information
    information_shown = False
    warning_shown = False
    critical_shown = False

    timer: QTimer
    start_time: datetime = datetime.now()
    total_elapsed: timedelta = timedelta(seconds=0)
    running: bool = False

    tick: pyqtSignal = pyqtSignal()

    def __init__(self, config: AppConfig, parent: QObject):
        
        super().__init__()

        self.config = config

        self.information_shown = False
        self.warning_shown = False
        self.critical_shown = False

        self.total_elapsed = timedelta(seconds=0)
        self.start_time = datetime.now()

        self.timer = QTimer(parent)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.tick.emit)
        self.tick.connect(self.update_time)

        self.running = False

    def update_time(self):
        now = datetime.now()
        self.total_elapsed = now - self.start_time
    
    def toggle_play_pause(self):
        """
        Start or pause the timer depending on its current state.

        Args:
            button (QPushButton): The button triggering the toggle.
        """
        if self.running:
            # Pause the timer
            self.timer.stop()
            self.total_elapsed = datetime.now() - self.start_time
            self.start_time = None

        else:
            # Resume the timer
            self.start_time = datetime.now() - self.total_elapsed
            self.timer.start(1000)

        self.running = not self.running
    
    def reset(self):
        """
        Reset the timer to 0 and clear all states.

        Args:
            button (QPushButton): The button triggering the reset.
        """
        self.timer.stop()
        self.start_time = None
        self.total_elapsed = timedelta()
        
        self.running = False
        # Reset all alert states
        self.information_shown = False
        self.warning_shown = False
        self.critical_shown = False

    def check_for_alerts(self):
        """
        Show desktop notifications based on elapsed time
        and configured alert thresholds.
        """
        if self.total_elapsed >= timedelta(**self.config.notifications.information) and not self.information_shown:
           self.information_shown = True
           return ("Finish now!", 'Information')
            
        if self.total_elapsed >= timedelta(**self.config.notifications.warning) and not self.warning_shown:
            self.warning_shown = True
            return ("Tomorrow is a new day!", 'Warning')
            
        if self.total_elapsed >= timedelta(**self.config.notifications.critical) and not self.critical_shown:
            self.critical_shown = True
            return ("GO HOME NOW!", 'Critical')
            