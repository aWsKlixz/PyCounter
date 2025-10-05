from PyQt5.QtCore import QTimer, QObject, pyqtSignal
from datetime import timedelta, datetime
from config import AppConfig

class ActivityManager(QObject):
    """
    A class to manage the activity timer and alert system.

    This class tracks the elapsed time for an activity, manages a timer that updates every second,
    and provides alerts when the elapsed time exceeds certain thresholds.
    """

    config: AppConfig

    # Flags to track the state of each alert (information, warning, critical)
    information_shown = False
    warning_shown = False
    critical_shown = False

    # Timer instance and elapsed time tracking
    timer: QTimer
    start_time: datetime = datetime.now()
    total_elapsed: timedelta = timedelta(seconds=0)
    last_update: datetime = datetime.now()
    running: bool = False

    # Signal emitted on every timer tick to update elapsed time
    tick: pyqtSignal = pyqtSignal()

    def __init__(self, config: AppConfig, parent: QObject):
        """
        Initialize the ActivityManager instance.

        Args:
            config (AppConfig): The application configuration that contains notification thresholds.
            parent (QObject): The parent object for the timer.
        """
        super().__init__()

        self.config = config

        # Initialize alert flags
        self.information_shown = False
        self.warning_shown = False
        self.critical_shown = False

        # Initialize elapsed time tracking
        self.total_elapsed = timedelta(seconds=0)
        self.start_time = datetime.now()
        self.last_update = datetime.now()

        # Initialize and configure the timer
        self.timer = QTimer(parent)
        self.timer.setInterval(1_000)  # 1000 ms = 1 second
        self.timer.timeout.connect(self.tick.emit)  # Emit signal every time the timer times out
        self.tick.connect(self.update_time)  # Connect the tick signal to the update_time method

        self.running = False

    def update_time(self, delta: timedelta | None = None):
        """
        Update the total elapsed time by calculating the difference
        between the current time and the start time.
        """
        if not delta:
            new_time = self.total_elapsed + (datetime.now() - self.last_update)
        else:
            new_time = self.total_elapsed + delta 
        self.total_elapsed = new_time
        self.last_update = datetime.now()
    
    def start_timer(self):
        """
        Start the timer if it is not already running.
        Resets the start time and begins updating the elapsed time every second.
        """
        if not self.running:
            self.start_time = datetime.now() - self.total_elapsed  # Adjust the start time based on any previous elapsed time
            self.timer.start(1_000)  # Start the timer with 1-second interval
            self.running = True
    
    def toggle_play_pause(self):
        """
        Toggle the timer between playing and pausing states.

        When paused, it stops the timer and keeps track of the elapsed time.
        When resumed, it restarts the timer from the paused state.
        """
        if self.running:
            # Pause the timer
            self.timer.stop()
            self.total_elapsed = datetime.now() - self.start_time  # Store the elapsed time at pause
            self.start_time = None # type: ignore
            self.running = not self.running
        else:
            # Resume the timer
            self.start_timer()
    
    def reset(self):
        """
        Reset the timer and clear all states to their initial values.

        Stops the timer, resets the elapsed time, and clears all alert flags.
        """
        self.timer.stop()
        self.start_time = None # type: ignore
        self.total_elapsed = timedelta()

        self.running = False
        # Reset all alert flags
        self.information_shown = False
        self.warning_shown = False
        self.critical_shown = False

    def check_for_alerts(self):
        """
        Check if the elapsed time has reached any configured alert thresholds.

        Returns:
            tuple: A tuple containing the alert message and the alert type
                   (information, warning, or critical) if an alert should be shown.
                   None if no alert is triggered.
        """
        # Check if elapsed time has exceeded the information threshold
        if self.total_elapsed >= timedelta(**self.config.notifications.information) and not self.information_shown:
            self.information_shown = True
            return ("Finish now!", 'Information')

        # Check if elapsed time has exceeded the warning threshold
        if self.total_elapsed >= timedelta(**self.config.notifications.warning) and not self.warning_shown:
            self.warning_shown = True
            return ("Tomorrow is a new day!", 'Warning')

        # Check if elapsed time has exceeded the critical threshold
        if self.total_elapsed >= timedelta(**self.config.notifications.critical) and not self.critical_shown:
            self.critical_shown = True
            return ("GO HOME NOW!", 'Critical')

        return None  # No alert if none of the thresholds are exceeded
