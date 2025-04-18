# **PyCounter - Keep an Eye on Your Time, Boost Your Productivity!**

**PyCounter** is your go-to Python-based time and activity tracker designed to help you stay on top of your workday. Whether you’re working on a project, managing tasks, or simply want to keep track of your hours, PyCounter makes it easy and efficient.

With its simple interface and essential features, PyCounter is the perfect tool for freelancers, professionals, and anyone looking to optimize their time management. Keep track of your progress, set custom alerts, and gain insights into your productivity — all while enjoying a smooth and seamless experience.

## **Why Choose PyCounter?**
- **Stay in Control of Your Time**: Start, pause, and reset the timer with just a click.
- **Customizable Alerts**: Get notified when you reach key time milestones with information, warning, and critical alerts. Tailor the alerts to fit your needs.
- **Simple, Clear, and Responsive UI**: Track your time easily with a clean and user-friendly interface that adapts to your workflow.
- **Monitor Project Progress**: Keep a close eye on your ongoing projects and understand where your time is spent.
- **Insightful Work Overview**: Review your work in total or by month, helping you make informed decisions about your time usage.
- **Seamless System Tray Integration**: Let PyCounter run quietly in the background, available whenever you need it without interrupting your work.

## **Key Features**
- **Start, Pause, and Reset Timer**: Convenient controls to manage your time with ease.
- **Timer Alerts with Different Urgency Levels**: Information, warning, and critical alerts based on your configurable time thresholds.
- **Configurable Alert Thresholds**: Adjust the time at which alerts trigger to suit your workflow and preferences.
- **Track Project Activity**: Keep tabs on how much time you’re spending on each project.
- **Work Summary**: View detailed breakdowns of your work over time, by day or by month.
- **Background Mode**: Minimize to the system tray and continue tracking without distractions.

## **Requirements**
Ensure you have the following installed:
- Python >= 3.11
- PyQt5
- Pydantic
- YAML
- TinyDB
- numpy
- Pandas
- openpyxl
- pyinstaller

To install the required packages, run:
```bash
pip install -r requirements.txt
```

## **Configuring**
PyCounter is easy to configure and customize for your workflow. It uses a `YAML`-based configuration system powered by Pydantic for validation and flexibility.

### Default Configuration

By default, PyCounter sets up everything you need to get started:
- Window size and layout
- Notification time levels (info/warning/critical)
- Asset paths (icons, stylesheets)
- Local JSON database for project data

When running in **debug mode**, configurations are stored in the source directory.  
In production, PyCounter automatically creates and uses a dedicated folder at `~/.pycounter`.

### Config File (YAML)

You can override the default settings by providing a custom YAML configuration file.  
Here's an example:

```yaml
debug: false

window:
  width: 600
  height: 300

notifications:
  information:
    hours: 1
  warning:
    hours: 2
  critical:
    hours: 4

mind:
  database: "my_tracking_db"
  collection: "user"
  defaultorder: "0000"
```

## **Installing**

To turn PyCounter into a standalone executable
```bash
pyinstaller --onefile --noconsole --add-data "pycounter/assets/*:pycounter/assets" --add-data "pycounter/config.yaml:." pycounter/main.py

```

## **Testing** 
You can test PyCounter by running the script at ```tests/fake_db.py``` to create a fake database.