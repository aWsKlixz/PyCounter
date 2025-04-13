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


class CounterApp(QMainWindow, BaseWidget):

    

    def __init__(self, config: AppConfig = AppConfig()):
        super().__init__(config=config)
        self.config = config
        self.setWindowIcon(QIcon(str(self.config.assets.Icon)))
        self._init_ui()

        self.app = QApplication.instance()
        self.app.aboutToQuit.connect(self.on_exit)
    
    def _btn_push_click_handler(self):
        
        self.mind.current_order = self.inp.text()
        self.mind.order_start_time = datetime.now() 

    def _btn_quit_click_handler(self):
        self.mind.push()
        self.inp.setText('')
            
    def _init_ui(self):
        # Set window title, size, and position
        self.setWindowTitle("Counter App - Keep an eye on your Time!")
        width, height = self.config.window.width, self.config.window.height
        self.setGeometry(100, 100, width, height)
        self.setFixedSize(width, height)
        self._move_window_to_bottom_right(width, height)

        # Main layout setup
        central_widget = QWidget(self)
        central_layout = QVBoxLayout()

        # Create the counter frame (timer + buttons)
        counter_frame = self._create_counter_frame()

        # Tracker frame
        tracker_frame = self._create_activity_panel()

        central_layout.addWidget(counter_frame)
        central_layout.addWidget(tracker_frame)

        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

    def _move_window_to_bottom_right(self, w: int, h: int):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        x = screen_geometry.width() - w
        y = screen_geometry.height() - h
        self.move(x, y)

    def _create_counter_frame(self) -> QWidget:
        frame = QWidget(self)
        layout = QHBoxLayout()

        # Timer widget
        self.timer_widget = TimerWidget(config=self.config, parent=frame)
        layout.addWidget(self.timer_widget)

        # Control buttons (Start/Reset)
        button_panel = self._create_button_panel()
        layout.addWidget(button_panel)

        frame.setLayout(layout)
        return frame

    def _create_button_panel(self) -> QWidget:
        button_frame = QWidget(self)
        layout = QGridLayout()

        # Start/Pause button
        self.play_pause_button = QPushButton("Start", self)
        self._set_icon(self.play_pause_button, 'Play')
        self.play_pause_button.clicked.connect(
            lambda: self.timer_widget.toggle(self.play_pause_button)
        )
        layout.addWidget(self.play_pause_button, 0, 0)

        # Reset button
        self.reset_button = QPushButton("Reset", self)
        self._set_icon(self.reset_button, 'Reset')
        self.reset_button.clicked.connect(
            lambda: self.timer_widget.reset(self.play_pause_button)
        )
        layout.addWidget(self.reset_button, 0, 1)

        button_frame.setLayout(layout)
        return button_frame

    def _create_activity_panel(self):
        
        frame = QWidget(self)

        layout = QHBoxLayout()

        lbl = QLabel("Order", self)
        self.inp = QLineEdit(self)
        self.btn_push = QPushButton("Push", self)
        self._set_icon(self.btn_push, 'Push')
        self.btn_push.clicked.connect(self._btn_push_click_handler)

        self.btn_quit = QPushButton("Quit", self)
        self._set_icon(self.btn_quit, 'Quit')
        self.btn_quit.clicked.connect(self._btn_quit_click_handler)

        layout.addWidget(lbl)
        layout.addWidget(self.inp)
        layout.addWidget(self.btn_push)
        layout.addWidget(self.btn_quit)

        frame.setLayout(layout)

        return frame
    
    def _set_icon(self, button: QPushButton, icon: Literal['Icon', 'Pause', 'Play', 'Reset', 'Quit', 'Push']):
        icon_path = getattr(self.config.assets, icon, None)
        if icon_path:
            button.setIcon(QIcon(str(icon_path)))
            button.setIconSize(QSize(32, 32))

    def on_exit(self):
        self.play_pause_button.click()
        self.btn_push.click()