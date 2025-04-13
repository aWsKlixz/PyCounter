# PyCounter - A Simple Timer and Counter Application

**PyCounter** is a Python-based timer and counter application that runs in the background and helps you manage your time effectively. It provides a system tray icon, notifications for different time thresholds, and the ability to pause, resume, and reset your timer. In addition, you can push current order-/project-numbers to the counter to track your work on it.
To get an overview of your working hours, you can create an excel view in total or by month.

## Features

- **System Tray Integration**: Runs as a background application with a system tray icon.
- **Start, Pause, and Reset Timer**: Control the timer using buttons to start, pause, or reset.
- **Timer Alerts**: Show notifications based on elapsed time with different levels of urgency (Information, Warning, Critical).
- **Configurable Alerts**: Set custom time thresholds for each type of alert (information, warning, critical).
- **Responsive UI**: Display the elapsed time in a clear and easy-to-read format.
- **Project Tracking**: Track your project activity.
- **Work Overview**: Get an overview of your work in total or by month

## Requirements

- Python >=3.11
- PyQt5
- Pydantic
- YAML
- TinyDB
- numpy
- Pandas
- openpyxl

You can install the required packages using `pip`:

```bash
pip install requirements.txt -r
```

## Install with pyinstaller

```bash
pyinstaller --onefile --add-data "pycounter/assets/*:pycounter/assets" --add-data "pycounter/config.yaml:." pycounter/main.py
```


## Testing
To test the app, you can create a fake-database by excuting the script at tests/fake_db.py

