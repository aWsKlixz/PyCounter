import sys
import yaml
from pydantic_settings import BaseSettings
from typing import List, Dict, Literal
from pathlib import Path

class WindowConfig(BaseSettings):
    width: int = 450
    height: int = 150

class NotificationConfig(BaseSettings):
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
    root: str = "pycounter/assets"
    @property
    def Root(self) -> Path:
        if getattr(sys, 'frozen', False):
            # If the application is frozen (e.g., using PyInstaller)
            r = Path(sys._MEIPASS).joinpath(self.root)
        else:
            # If the application is running in a normal Python environment
            r = Path(self.root)
        return r
    
    icon: str = "icon.png"
    @property
    def Icon(self) -> str:
        return self.Root.joinpath(self.icon)
    
    play: str = "play.svg"
    @property
    def Play(self) -> str:
        return self.Root.joinpath(self.play)
    
    pause: str = "pause.svg"
    @property
    def Pause(self) -> str:
        return self.Root.joinpath(self.pause)
    
    reset: str = "reset.svg"
    @property
    def Reset(self) -> str:
        return self.Root.joinpath(self.reset)


class AppConfig(BaseSettings):
    window: WindowConfig = WindowConfig()
    notifications: NotificationConfig = NotificationConfig()
    assets: AssetConfig = AssetConfig()


def yaml_config_loader(file_path: str) -> AppConfig:
    with open(file_path, 'r') as file:
        config_data = yaml.safe_load(file)
    return AppConfig(**config_data)