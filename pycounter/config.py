import sys
import yaml
from pydantic_settings import BaseSettings
from typing import List, Dict, Literal
from pathlib import Path

class WindowConfig(BaseSettings):
    """
    Configuration settings related to the application window.
    """
    width: int = 450
    height: int = 200


class NotificationConfig(BaseSettings):
    """
    Configuration for notification timing levels.
    
    Each dictionary specifies a time duration (e.g., in hours) for a given level.
    """
    information: Dict[str, int] = {
        'hours': 1
    }
    warning: Dict[str, int] = {
        'hours': 2
    }
    critical: Dict[str, int] = {
        'hours': 3
    }


class AssetConfig(BaseSettings):
    """
    Configuration for application assets (icons, stylesheets, etc.).
    Automatically resolves paths depending on whether the app is frozen (e.g., with PyInstaller).
    """
    root: str = "pycounter/assets"

    @property
    def Root(self) -> Path:
        """
        Returns the root path for assets depending on the execution context.
        """
        if getattr(sys, 'frozen', False):
            # If the application is bundled (e.g., using PyInstaller)
            r = Path(sys._MEIPASS).joinpath(self.root)
        else:
            # If the application is running in a normal Python environment
            r = Path(self.root)
        return r

    # Icon file names and computed paths
    icon: str = "icon.svg"
    @property
    def Icon(self) -> Path:
        return self.Root.joinpath(self.icon)

    play: str = "play.svg"
    @property
    def Play(self) -> Path:
        return self.Root.joinpath(self.play)

    pause: str = "pause.svg"
    @property
    def Pause(self) -> Path:
        return self.Root.joinpath(self.pause)

    reset: str = "reset.svg"
    @property
    def Reset(self) -> Path:
        return self.Root.joinpath(self.reset)

    push: str = "push.svg"
    @property
    def Push(self) -> Path:
        return self.Root.joinpath(self.push)

    quit: str = "quit.svg"
    @property
    def Quit(self) -> Path:
        return self.Root.joinpath(self.quit)

    stylesheet: str = "style.qss"
    @property
    def Stylesheet(self) -> Path:
        return self.Root.joinpath(self.stylesheet)


class Data(BaseSettings):
    """
    Configuration for data sources and temporary file handling.
    """
    database: str = 'test'  # MongoDB or similar database name
    collection: str = 'herecomestheuser'  # Default collection/table name
    defaultorder: str = "1234"  # Default order ID (useful for debugging or pre-loads)
    tempfolder: str = '.'  # Directory for storing temporary data/files


class AppConfig(BaseSettings):
    """
    Aggregated configuration for the entire application.
    
    Includes settings for the window, notifications, assets, and data handling.
    """
    window: WindowConfig = WindowConfig()
    notifications: NotificationConfig = NotificationConfig()
    assets: AssetConfig = AssetConfig()
    mind: Data = Data()


def yaml_config_loader(file_path: str) -> AppConfig:
    """
    Loads application configuration from a YAML file.

    Args:
        file_path (str): Path to the YAML configuration file.

    Returns:
        AppConfig: A fully initialized AppConfig object with all nested fields populated.
    """
    with open(file_path, 'r') as file:
        config_data = yaml.safe_load(file)
    return AppConfig(**config_data)
