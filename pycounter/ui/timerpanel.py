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
        Initialize the timer widget and system tray icon.

        Args:
            config (AppConfig): The application configuration.
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(config=config, mind=mind, activity_manager=mgr, parent=parent)

        # Reset alert flags
        self.information_shown = False
        self.warning_shown = False
        self.critical_shown = False
        
        # Build UI layout
        self.init_ui()

        # Welcome notification

    def init_ui(self):
        """Initialize and arrange UI elements."""
        # set the layout
        layout = QHBoxLayout()
        # init the timer label
        self.lbl_time = QLabel("0:00:00", self)
        self.activity_manager.tick.connect(self.update_label_handler)

        # init buttons
        # play pause button
        self.btn_play_pause = QPushButton('Start', self)
        self._set_icon(self.btn_play_pause, 'Play')
        self.btn_play_pause.clicked.connect(
            lambda: self.play_pause_handler(self.btn_play_pause)
        )

        # reset button
        self.btn_reset = QPushButton('Reset', self)
        self._set_icon(self.btn_reset, 'Reset')
        self.btn_reset.clicked.connect(
            lambda: self.reset_click_handler(self.btn_play_pause)
        )

        # assemble the layout
        layout.addWidget(self.lbl_time)
        layout.addWidget(self.btn_play_pause)
        layout.addWidget(self.btn_reset)
        self.setLayout(layout)

    def play_pause_handler(self, button: QPushButton):
        self.activity_manager.toggle_play_pause()
        if self.activity_manager.running:
            self._set_icon(button, 'Pause')
            button.setText("Pause")
        else:
            self._set_icon(button, 'Play')
            button.setText('Resume')
        self.mind.update(self.activity_manager.total_elapsed)
    
    def reset_click_handler(self, button: QPushButton):
        self.activity_manager.reset()
        self.lbl_time.setText("00:00:00")
        button.setIcon(QIcon(str(self.config.assets.Play)))
        button.setText("Start")
        self.mind.update(timedelta(seconds=0.0))

    def update_label_handler(self):
        self.lbl_time.setText(str(self.activity_manager.total_elapsed).split('.')[0])
