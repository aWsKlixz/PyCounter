from datetime import datetime
from typing import Optional

from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QHBoxLayout

from config import AppConfig
from ui.basewidget import BaseWidget

from core.db import Mind
from core.activitymanager import ActivityManager

class ActivityPanel(BaseWidget):
    """
    A panel widget that allows the user to enter a project name and perform
    actions to start ('Push') and stop ('Pull') a task.

    Attributes:
        lbl_project (QLabel): Label for the project name input field.
        inp_project (QLineEdit): Text input field for entering the project name.
        btn_push (QPushButton): Button to begin tracking an activity.
        btn_pull (QPushButton): Button to stop tracking and push the data.
        mind (MindBase): Shared state object for storing project and time info.
    """

    lbl_project: QLabel
    inp_project: QLineEdit
    btn_push: QPushButton
    btn_pull: QPushButton
    mind: Mind

    def __init__(
            self, 
            config: AppConfig, 
            mind: Mind,
            mgr: ActivityManager,
            parent: Optional[BaseWidget] = None):
        """
        Initializes the activity panel with configuration and parent widget.

        Args:
            config: Configuration object loaded from the app.
            parent (Optional[BaseWidget]): Parent widget.
        """
        super().__init__(config=config, mind=mind, activity_manager=mgr, parent=parent)
        self.init_ui()

    def init_ui(self):
        """
        Initializes and lays out UI elements in a horizontal layout.
        """
        self.lbl_project = QLabel("Project", self)

        self.inp_project = QLineEdit(self)

        self.btn_push = QPushButton("Record", self)
        self._set_icon(self.btn_push, 'Push')
        self.btn_push.clicked.connect(self._btn_push_click_handler)

        self.btn_pull = QPushButton("Push", self)
        self._set_icon(self.btn_pull, 'Quit')  # Consider changing 'Quit' to 'Pull' icon in assets
        self.btn_pull.clicked.connect(self._btn_pull_click_handler)

        layout = QHBoxLayout()
        layout.addWidget(self.lbl_project)
        layout.addWidget(self.inp_project)
        layout.addWidget(self.btn_push)
        layout.addWidget(self.btn_pull)

        self.setLayout(layout)

    def _btn_push_click_handler(self):
        """
        Handles the Push button click event.

        Sets the current project order in the mind object and records the start time.
        """
        project_name = self.inp_project.text().strip()
        if not project_name:
            # TODO: optionally add a popup or visual indicator for empty input
            return

        self.mind.current_order = project_name
        self.mind.order_start_time = datetime.now()

    def _btn_pull_click_handler(self):
        """
        Handles the Pull button click event.

        Triggers a push of the current task state and clears the project input.
        """
        self.mind.push()
        self.inp_project.setText('')
