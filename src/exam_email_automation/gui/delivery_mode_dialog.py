from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QRadioButton,
    QButtonGroup, QGroupBox
)
from PySide6.QtCore import Qt


class DeliveryModeDialog(QDialog):
    """Dialog for selecting delivery mode (Preview Only, Create Drafts, Send Immediately)."""

    def __init__(self, parent, default_mode: str = "create_drafts"):
        """
        Args:
            parent: Parent widget
            default_mode: "preview_only", "create_drafts", or "send_immediately"
        """
        super().__init__(parent)
        self.setWindowTitle("Delivery Mode")
        self.setGeometry(200, 200, 500, 350)

        self.selected_mode = default_mode

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("How would you like to process the emails?"))
        layout.addSpacing(10)

        # Mode selection
        mode_group = QGroupBox("Delivery Mode")
        mode_layout = QVBoxLayout()

        self.mode_buttons = QButtonGroup()

        preview_btn = QRadioButton("Preview Only\n(Generate HTML previews without sending)")
        preview_btn.setChecked(self.selected_mode == "preview_only")
        self.mode_buttons.addButton(preview_btn, 0)
        mode_layout.addWidget(preview_btn)

        draft_btn = QRadioButton("Create Outlook Drafts (Default)\n(Create unsent draft emails in Outlook for review)")
        draft_btn.setChecked(self.selected_mode == "create_drafts")
        self.mode_buttons.addButton(draft_btn, 1)
        mode_layout.addWidget(draft_btn)

        send_btn = QRadioButton("Send Immediately\n(Send emails directly to students)")
        send_btn.setChecked(self.selected_mode == "send_immediately")
        self.mode_buttons.addButton(send_btn, 2)
        mode_layout.addWidget(send_btn)

        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # Wire up changes
        preview_btn.toggled.connect(lambda checked: self._on_mode_changed(checked, "preview_only"))
        draft_btn.toggled.connect(lambda checked: self._on_mode_changed(checked, "create_drafts"))
        send_btn.toggled.connect(lambda checked: self._on_mode_changed(checked, "send_immediately"))

        layout.addSpacing(20)

        # Buttons
        button_layout = QHBoxLayout()
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.reject)
        continue_btn = QPushButton("Continue")
        continue_btn.clicked.connect(self.accept)

        button_layout.addStretch()
        button_layout.addWidget(back_btn)
        button_layout.addWidget(continue_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _on_mode_changed(self, checked: bool, mode: str):
        if checked:
            self.selected_mode = mode

    def get_selected_mode(self) -> str:
        """Returns 'preview_only', 'create_drafts', or 'send_immediately'"""
        return self.selected_mode
