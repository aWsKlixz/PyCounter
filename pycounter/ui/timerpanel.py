from PyQt5.QtWidgets import (
    QLabel, QHBoxLayout,
    QPushButton
)
from PyQt5.QtGui import QIcon
from datetime import timedelta

from ui.basewidget import BaseWidget
from config import AppConfig
from core.db import Mind
from core.activitymanager import ActivityManager


class TimerPanel(BaseWidget):
    """
    A widget that functions as a timer with visual output, alerts, and tray notifications.

    Attributes:
        information_shown (bool): Tracks if the information alert has been shown.
        warning_shown (bool): Tracks if the warning alert has been shown.
        critical_shown (bool): Tracks if the critical alert has been shown.
        lbl_time (QLabel): Displays the current time in the timer.
        btn_play_pause (QPushButton): Button for playing or pausing the timer.
        btn_reset (QPushButton): Button to reset the timer.
    """

    lbl_time: QLabel
    btn_play_pause: QPushButton
    btn_reset: QPushButton

    def __init__(
            self, 
            config: AppConfig, 
            mind: Mind,
            mgr: ActivityManager,
            parent=None
        ):
        """
        Initializes the timer widget and sets up connections to the activity manager.

        Args:
            config (AppConfig): The application configuration object.
            mind (Mind): The shared state object for managing the time and project information.
            mgr (ActivityManager): The activity manager that handles the timer's start, stop, and reset functionality.
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(config=config, mind=mind, activity_manager=mgr, parent=parent)

        # Reset alert flags to prevent repeated notifications
        self.information_shown = False
        self.warning_shown = False
        self.critical_shown = False
        
        # Build and layout the UI elements
        self.init_ui()

        # Connect the tick signal from the activity manager to update the button state
        self.activity_manager.tick.connect(
            lambda: self.update_button_handler(self.btn_play_pause)
        )

    def init_ui(self):
        """
        Initializes and arranges the UI elements for the timer panel.
        Sets up the timer label, play/pause button, and reset button.
        """
        # Create a horizontal layout for the timer panel
        layout = QHBoxLayout()

        # Initialize and configure the timer label
        self.lbl_time = QLabel("0:00:00", self)
        # Connect the tick signal to update the timer display
        self.activity_manager.tick.connect(self.update_label_handler)

        # Initialize the play/pause button
        self.btn_play_pause = QPushButton('Start', self)
        self._set_icon(self.btn_play_pause, 'Play')
        self.btn_play_pause.clicked.connect(
            lambda: self.play_pause_handler(self.btn_play_pause)
        )

        # Initialize the reset button
        self.btn_reset = QPushButton('Reset', self)
        self._set_icon(self.btn_reset, 'Reset')
        self.btn_reset.clicked.connect(
            lambda: self.reset_click_handler(self.btn_play_pause)
        )

        # Add all elements to the layout
        layout.addWidget(self.lbl_time)
        layout.addWidget(self.btn_play_pause)
        layout.addWidget(self.btn_reset)
        
        # Set the layout for the widget
        self.setLayout(layout)

    def update_button_handler(self, button: QPushButton):
        """
        Updates the play/pause button state based on the activity manager's running state.

        Args:
            button (QPushButton): The button to update (either play/pause).
        """
        if self.activity_manager.running:
            self._set_icon(button, 'Pause')
            button.setText("Pause")
        else:
            self._set_icon(button, 'Play')
            button.setText('Resume')

    def play_pause_handler(self, button: QPushButton):
        """
        Handles the play/pause button click event, toggling the state of the activity manager.

        Args:
            button (QPushButton): The button that triggered the event.
        """
        self.activity_manager.toggle_play_pause()
        
        # Update the button icon and text based on the current state
        if self.activity_manager.running:
            self._set_icon(button, 'Pause')
            button.setText("Pause")
        else:
            self._set_icon(button, 'Play')
            button.setText('Resume')

        # Update the mind with the current timer state
        self.mind.update(self.activity_manager.total_elapsed)
    
    def reset_click_handler(self, button: QPushButton):
        """
        Resets the timer and updates the button state to "Start".
        Clears the timer display and resets the total elapsed time.

        Args:
            button (QPushButton): The button that triggered the reset action.
        """
        self.activity_manager.reset()
        # Reset the label to display 00:00:00
        self.lbl_time.setText("00:00:00")
        # Update the play/pause button to show "Start"
        button.setIcon(QIcon(str(self.config.assets.Play)))
        button.setText("Start")
        # Update the mind with the reset timer value
        self.mind.update(timedelta(seconds=0.0))

    def update_label_handler(self):
        """
        Updates the timer display label with the current elapsed time from the activity manager.
        """
        # Display the current elapsed time in the label
        self.lbl_time.setText(str(self.activity_manager.total_elapsed).split('.')[0])
