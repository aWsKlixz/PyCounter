from abc import ABC
from typing import Literal
from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

from pycounter.config import AppConfig
from pycounter.db import Mind

class BaseWidget(QWidget):
    """
    A base widget class that other UI components can inherit from.

    Provides:
    - Access to application configuration (`config`)
    - Access to the shared state or data logic (`mind`)
    - Utility method to set standardized icons on buttons
    """

    config: AppConfig  # Application configuration, including paths and visual assets
    mind: Mind         # Shared logic/state object (e.g. handles timing, data pushing)

    def __init__(self, config: AppConfig, parent=None):
        """
        Initializes the base widget with shared configuration and state.

        Args:
            config (AppConfig): The full application configuration object.
            parent: Optional parent QWidget.
        """
        self.config = config
        self.mind = Mind(config=self.config)  # Instantiate shared data/state logic
        super().__init__(parent)

    def _set_icon(
        self,
        button: QPushButton,
        icon: Literal['Icon', 'Pause', 'Play', 'Reset', 'Quit', 'Push']
    ):
        """
        Applies a standardized icon from the assets to a QPushButton.

        Args:
            button (QPushButton): The button to apply the icon to.
            icon (Literal): The name of the icon asset to use, must match a key in `config.assets`.

        Example:
            self._set_icon(self.btn_start, 'Play')
        """
        # Retrieve icon path from config based on the literal string
        icon_path = getattr(self.config.assets, icon, None)

        if icon_path:
            button.setIcon(QIcon(str(icon_path)))      # Set the icon image
            button.setIconSize(QSize(32, 32))          # Set a standard size for consistency
