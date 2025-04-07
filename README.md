# PyCounter - A Simple Timer and Counter Application

**PyCounter** is a Python-based timer and counter application that runs in the background and helps you manage your time effectively. It provides a system tray icon, notifications for different time thresholds, and the ability to pause, resume, and reset your timer.

## Features

- **System Tray Integration**: Runs as a background application with a system tray icon.
- **Start, Pause, and Reset Timer**: Control the timer using buttons to start, pause, or reset.
- **Timer Alerts**: Show notifications based on elapsed time with different levels of urgency (Information, Warning, Critical).
- **Configurable Alerts**: Set custom time thresholds for each type of alert (information, warning, critical).
- **Responsive UI**: Display the elapsed time in a clear and easy-to-read format.

## Requirements

- Python 3.x
- PyQt5
- Pydantic
- YAML

You can install the required packages using `pip`:

```bash
pip install PyQt5 pydantic pyyaml
```

## Install with pyinstaller

```bash
pyinstaller --onefile --add-data "pycounter/assets/*:pycounter/assets" --add-data "pycounter/config.yaml:." pycounter/main.py
```


