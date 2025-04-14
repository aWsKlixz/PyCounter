from PyQt5.QtWidgets import QSystemTrayIcon
from PyQt5.QtGui import QIcon

from ui.menu import AppMenu
from core.activitymanager import ActivityManager

class TrayCounter(QSystemTrayIcon):

    activity_manager: ActivityManager
    
    def __init__(self, icon: QIcon, mgr: ActivityManager, parent):
        super().__init__(icon=icon, parent=parent)
        self.activity_manager = mgr
        self.init_ui()
        self.setVisible(True)

    def init_ui(self):
        self.setToolTip("PyCounter - Keep an eye on your time!")

        menu = AppMenu(self.parent())
        self.setContextMenu(menu)

        self.activity_manager.tick.connect(self.check_alert_handler)
    
    def check_alert_handler(self):
        check = self.activity_manager.check_for_alerts()
        if check:
            msg, level = check
            self.show_alert(msg, getattr(QSystemTrayIcon, level, QSystemTrayIcon.Information))


    def show_alert(self, message: str, icon: QSystemTrayIcon = QSystemTrayIcon.Information):
        """
        Display a system tray notification.

        Args:
            message (str): The message to show in the notification.
            icon (QSystemTrayIcon.MessageIcon): The type of notification icon.
        """
        self.showMessage("Alert", message, icon, 10000)
