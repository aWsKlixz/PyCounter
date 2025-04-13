import sys
import yaml
from pydantic_settings import BaseSettings
from typing import List, Dict, Literal
from pathlib import Path

class WindowConfig(BaseSettings):
    width: int = 450
    height: int = 200

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
    
    icon: str = "icon.svg"
    @property
    def Icon(self) -> str:
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
    def Quit(self):
        return self.Root.joinpath(self.quit)
    
    stylesheet: str = "style.qss"
    @property
    def Stylesheet(self):
        return self.Root.joinpath(self.stylesheet)

class Data(BaseSettings):
    database: str = 'test'
    collection: str =  'herecomestheuser'
    defaultorder: str = "1234"
    


class AppConfig(BaseSettings):
    window: WindowConfig = WindowConfig()
    notifications: NotificationConfig = NotificationConfig()
    assets: AssetConfig = AssetConfig()
    mind: Data = Data()


def yaml_config_loader(file_path: str) -> AppConfig:
    with open(file_path, 'r') as file:
        config_data = yaml.safe_load(file)
    return AppConfig(**config_data)