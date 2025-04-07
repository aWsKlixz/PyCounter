from abc import ABC

from PyQt5.QtWidgets import QWidget

from config import AppConfig

class BaseWidget(QWidget):
    config: AppConfig
    def __init__(self, config: AppConfig, parent=None):
        self.config = config
        super().__init__(parent)
        