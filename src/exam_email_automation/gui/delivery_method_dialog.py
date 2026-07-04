from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QRadioButton,
    QButtonGroup, QComboBox, QGroupBox
)
from PySide6.QtCore import Qt


class DeliveryMethodDialog(QDialog):
    """Dialog for selecting delivery method (Outlook or SMTP) and mailbox."""

    def __init__(self, parent, available_mailboxes: list = None):
        """
        Args:
            parent: Parent widget
            available_mailboxes: List of available Outlook mailbox emails/names
        """
        super().__init__(parent)
        self.available_mailboxes = available_mailboxes or ["Default Account"]
        self.setWindowTitle("Delivery Method")
        self.setGeometry(200, 200, 500, 300)

        # Results
        self.selected_method = "outlook"  # "outlook" or "smtp"
        self.selected_mailbox = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Delivery Method (Outlook / SMTP)
        method_group = QGroupBox("Delivery Method")
        method_layout = QVBoxLayout()

        self.method_buttons = QButtonGroup()
        
        outlook_btn = QRadioButton("Outlook (Desktop)")
        outlook_btn.setChecked(True)
        self.method_buttons.addButton(outlook_btn, 0)
        method_layout.addWidget(outlook_btn)

        smtp_btn = QRadioButton("SMTP (Email Server)")
        self.method_buttons.addButton(smtp_btn, 1)
        method_layout.addWidget(smtp_btn)

        method_group.setLayout(method_layout)
        layout.addWidget(method_group)

        # Mailbox selection (Outlook only)
        mailbox_group = QGroupBox("Outlook Account")
        mailbox_layout = QVBoxLayout()

        mailbox_label = QLabel("From:")
        self.mailbox_combo = QComboBox()
        self.mailbox_combo.addItems(self.available_mailboxes)
        
        mailbox_layout.addWidget(mailbox_label)
        mailbox_layout.addWidget(self.mailbox_combo)
        mailbox_group.setLayout(mailbox_layout)
        layout.addWidget(mailbox_group)

        # Wire up method changes
        outlook_btn.toggled.connect(self._on_outlook_selected)
        smtp_btn.toggled.connect(self._on_smtp_selected)

        # Buttons
        button_layout = QHBoxLayout()
        cancel_btn = QPushButton("Back")
        cancel_btn.clicked.connect(self.reject)
        continue_btn = QPushButton("Continue")
        continue_btn.clicked.connect(self._on_continue)

        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(continue_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _on_outlook_selected(self, checked):
        if checked:
            self.selected_method = "outlook"
            self.mailbox_combo.setEnabled(True)

    def _on_smtp_selected(self, checked):
        if checked:
            self.selected_method = "smtp"
            self.mailbox_combo.setEnabled(False)

    def _on_continue(self):
        self.selected_mailbox = self.mailbox_combo.currentText() if self.selected_method == "outlook" else None
        self.accept()

    def get_selected_method(self) -> str:
        """Returns 'outlook' or 'smtp'"""
        return self.selected_method

    def get_selected_mailbox(self) -> str:
        """Returns mailbox name/email, or None if not applicable"""
        return self.selected_mailbox
