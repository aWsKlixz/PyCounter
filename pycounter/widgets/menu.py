from PyQt5.QtWidgets import QMenu, QApplication, QAction

from pycounter.widgets.basewidget import BaseWidget


class AppMenu(QMenu):
    """
    A context menu for the application, containing options for generating reports
    and quitting the application.

    Attributes:
        parent_base_widget (BaseWidget): The parent widget that holds shared application state.
    """

    parent_base_widget: BaseWidget

    def __init__(self, parent: BaseWidget):
        """
        Initialize the AppMenu with its parent widget.

        Args:
            parent (BaseWidget): The parent widget, usually the main window, 
                                 giving access to the shared 'mind' logic.
        """
        self.parent_base_widget = parent
        super().__init__(parent)

        self.init_ui()

    def init_ui(self):
        """
        Initializes and populates the menu with actions and submenus.
        """
        # Create a "Reports" submenu
        report_menu = QMenu("Reports", self)

        # Add "Create total report" action
        total_report = QAction("Create total report!", self)
        total_report.triggered.connect(self.on_create_total_report_click)

        # Add "Create monthly report" action
        monthly_report = QAction("Create monthly report!", self)
        monthly_report.triggered.connect(self.on_create_monthly_report_click)

        # Add both actions to the Reports submenu
        report_menu.addActions([total_report, monthly_report])

        # Create a quit action
        quit_action = QAction('Exit!', self)
        quit_action.setShortcut('Ctrl+Q')  # Optional: Add a shortcut for convenience
        quit_action.triggered.connect(self.on_exit_click)

        # Add all menu items to the root menu
        self.addMenu(report_menu)
        self.addSeparator()
        self.addAction(quit_action)

    def on_create_total_report_click(self):
        """
        Callback for the 'Create total report' action.
        Generates a report covering the entire activity duration.
        """
        self.parent_base_widget.mind.report(
            format='hours',
            interval='total',
            open_report=True
        )

    def on_create_monthly_report_click(self):
        """
        Callback for the 'Create monthly report' action.
        Generates a report for the current or previous month.
        """
        self.parent_base_widget.mind.report(
            format='hours',
            interval='month',
            open_report=True
        )

    def on_exit_click(self):
        """
        Callback for the 'Exit' action. Closes the entire application.
        """
        QApplication.instance().quit()
