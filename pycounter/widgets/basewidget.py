from abc import ABC

from PyQt5.QtWidgets import QWidget

from config import AppConfig
from db import Mind

class BaseWidget(QWidget):
    config: AppConfig
    mind: Mind
    def __init__(self, config: AppConfig, parent=None):
        self.config = config
        self.mind = Mind(config=self.config)
        super().__init__(parent)
        