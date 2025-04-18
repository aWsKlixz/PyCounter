from datetime import datetime
from typing import Optional

from PyQt5.QtWidgets import QCompleter, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, QStringListModel, QSortFilterProxyModel, QRegExp

from config import AppConfig
from ui.basewidget import BaseWidget
from core.db import Mind
from core.activitymanager import ActivityManager

class RegexFilterProxyModel(QSortFilterProxyModel):
    """
    A proxy model that uses regex filtering to match substrings in a case-insensitive way.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)

    def filterAcceptsRow(self, source_row, source_parent):
        """
        Override to filter rows based on a regex match on the data in the first column.
        """
        index = self.sourceModel().index(source_row, 0, source_parent)
        data = self.sourceModel().data(index, Qt.DisplayRole)
        pattern = self.filterRegExp().pattern()
        return QRegExp(pattern, Qt.CaseInsensitive).indexIn(data) != -1


class RegexCompleter(QCompleter):
    """
    A QCompleter that uses a proxy model with regex filtering for dynamic suggestion matching.
    """
    def __init__(self, items, parent=None):
        # Create string model from provided items
        self.model = QStringListModel(items)

        # Use custom proxy model for regex-based filtering
        self.proxy_model = RegexFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)

        # Initialize the QCompleter with the proxy model
        super().__init__(self.proxy_model, parent)
        self.setCompletionMode(QCompleter.PopupCompletion)
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setFilterMode(Qt.MatchContains)

    def updateModelFilter(self, text):
        """
        Update the regex pattern for filtering based on user input.
        """
        regex = QRegExp(text, Qt.CaseInsensitive)
        self.proxy_model.setFilterRegExp(regex)


class FocusLineEdit(QLineEdit):
    """
    A QLineEdit with a regex-based completer that activates suggestions on text edit.
    """
    def __init__(self, suggestions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.completer_ = RegexCompleter(suggestions, self)
        self.setCompleter(self.completer_)
        self.textEdited.connect(self.completer_.updateModelFilter)

    def focusInEvent(self, event):
        """
        Ensure the completer updates on focus-in event.
        """
        super().focusInEvent(event)
        # Optionally show suggestions immediately on focus:
        self.completer().complete()


class ActivityPanel(BaseWidget):
    """
    A panel widget that allows the user to enter a project name and track its activity
    by starting (Record) and stopping (Push) with a single button.

    Attributes:
        lbl_project (QLabel): Label describing the input field.
        inp_project (FocusLineEdit): Custom input field with dynamic suggestions.
        btn_activity_handler (QPushButton): Button that toggles recording state.
        mind (Mind): Shared state container with time and activity info.
        activity_manager (ActivityManager): Controls the task timer.
    """

    lbl_project: QLabel
    inp_project: QLineEdit
    completer: QCompleter
    btn_activity_handler: QPushButton
    mind: Mind
    is_recording: bool = False

    def __init__(
        self,
        config: AppConfig,
        mind: Mind,
        mgr: ActivityManager,
        parent: Optional[BaseWidget] = None
    ):
        """
        Initializes the activity panel.

        Args:
            config (AppConfig): Application configuration.
            mind (Mind): Shared state object.
            mgr (ActivityManager): Manager to control start/stop.
            parent (Optional[BaseWidget]): Parent widget.
        """
        super().__init__(config=config, mind=mind, activity_manager=mgr, parent=parent)
        self.is_recording = False
        self.init_ui()

    def init_ui(self):
        """
        Set up and layout the UI components horizontally.
        """
        self.lbl_project = QLabel("Project", self)

        # Get previous activity suggestions from database
        suggestions = self.mind.get_activity_suggestions()
        self.inp_project = FocusLineEdit(suggestions, self)

        # Create the start/stop button
        self.btn_activity_handler = QPushButton("Record", self)
        self._set_icon(self.btn_activity_handler, 'Record')
        self.btn_activity_handler.clicked.connect(self._btn_actitvity_toggle_handler)

        # Layout the components
        layout = QHBoxLayout()
        layout.addWidget(self.lbl_project)
        layout.addWidget(self.inp_project)
        layout.addWidget(self.btn_activity_handler)
        self.setLayout(layout)

    def _btn_actitvity_toggle_handler(self):
        """
        Handles toggle behavior of the activity button between 'Record' and 'Push'.
        """
        if self.is_recording:
            # Stop recording: push data, reset input, update button
            self.mind.push()
            self.inp_project.setText('')
            self.btn_activity_handler.setText('Record')
            self._set_icon(self.btn_activity_handler, 'Record')
        else:
            # Start recording: validate input, start timer, update shared state
            project_name = self.inp_project.text().strip()
            if not project_name:
                # Optional: show warning popup or error message
                return

            if not self.activity_manager.running:
                self.activity_manager.start_timer()

            self.mind.current_order = project_name
            self.mind.order_start_time = datetime.now()
            self.btn_activity_handler.setText("Push")
            self._set_icon(self.btn_activity_handler, 'Push')

        # Toggle recording state
        self.is_recording = not self.is_recording
