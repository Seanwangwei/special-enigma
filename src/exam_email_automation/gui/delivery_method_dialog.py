"""Delivery method dialog — Outlook vs SMTP with step indicator and radio cards."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QRadioButton,
    QButtonGroup, QComboBox, QFrame, QWidget,
)

from exam_email_automation.gui.widgets import StepIndicator


class DeliveryMethodDialog(QDialog):
    """Step 1/3 of the send wizard: choose Outlook or SMTP."""

    def __init__(self, parent, available_mailboxes: list | None = None) -> None:
        super().__init__(parent)
        self.available_mailboxes = available_mailboxes or ["Default Account"]
        self.setWindowTitle("Delivery Method")
        self.setMinimumSize(460, 380)

        self.selected_method = "outlook"
        self.selected_mailbox: str | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Step indicator
        self.steps = StepIndicator(["Method", "Mode", "Confirm"])
        self.steps.set_current_step(0)
        layout.addWidget(self.steps)

        # Title
        title = QLabel("Choose Delivery Method")
        title.setStyleSheet("font-size: 16px; font-weight: 600; color: #1e293b; border: none; background: transparent;")
        layout.addWidget(title)

        # Radio options in a styled container
        options_frame = QFrame()
        options_frame.setStyleSheet("QFrame { background: transparent; border: none; }")
        options_layout = QVBoxLayout(options_frame)
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.setSpacing(8)

        self.method_group = QButtonGroup(self)

        self.outlook_radio = QRadioButton("Outlook (Desktop)")
        self.outlook_radio.setChecked(True)
        self.outlook_radio.setToolTip("Send via Microsoft Outlook — drafts or immediate send")
        self.method_group.addButton(self.outlook_radio, 0)
        options_layout.addWidget(self._wrap_radio(self.outlook_radio, "Send via Microsoft Outlook — drafts or immediate send"))

        self.smtp_radio = QRadioButton("SMTP (Email Server)")
        self.smtp_radio.setToolTip("Send via configured SMTP server using app credentials")
        self.method_group.addButton(self.smtp_radio, 1)
        options_layout.addWidget(self._wrap_radio(self.smtp_radio, "Send via configured SMTP server using app credentials"))

        layout.addWidget(options_frame)

        # Outlook account section
        mailbox_frame = QFrame()
        mailbox_frame.setStyleSheet(
            "QFrame { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; }"
        )
        mailbox_layout = QVBoxLayout(mailbox_frame)
        mailbox_layout.setContentsMargins(12, 10, 12, 10)
        mailbox_header = QLabel("OUTLOOK ACCOUNT")
        mailbox_header.setStyleSheet("font-size: 11px; font-weight: 600; color: #64748b; border: none; background: transparent;")
        mailbox_layout.addWidget(mailbox_header)

        from_row = QHBoxLayout()
        from_label = QLabel("From:")
        from_label.setStyleSheet("font-size: 13px; color: #64748b; border: none; background: transparent;")
        self.mailbox_combo = QComboBox()
        self.mailbox_combo.addItems(self.available_mailboxes)
        from_row.addWidget(from_label)
        from_row.addWidget(self.mailbox_combo, 1)
        mailbox_layout.addLayout(from_row)

        self.mailbox_section = mailbox_frame
        layout.addWidget(self.mailbox_section)

        # Wire up method changes
        self.outlook_radio.toggled.connect(self._on_outlook_selected)
        self.smtp_radio.toggled.connect(self._on_smtp_selected)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        back_btn = QPushButton("Back")
        back_btn.setProperty("cssClass", "ghost")
        back_btn.clicked.connect(self.reject)
        continue_btn = QPushButton("Continue")
        continue_btn.setProperty("cssClass", "primary")
        continue_btn.clicked.connect(self._on_continue)
        button_layout.addWidget(back_btn)
        button_layout.addStretch()
        button_layout.addWidget(continue_btn)
        layout.addLayout(button_layout)

    def _wrap_radio(self, radio: QRadioButton, description: str) -> QFrame:
        """Wrap a radio button in a card-style frame with description."""
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px; }"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(10, 8, 10, 8)
        card_layout.setSpacing(2)
        card_layout.addWidget(radio)
        desc = QLabel(description)
        desc.setStyleSheet("font-size: 11px; color: #94a3b8; border: none; background: transparent; margin-left: 24px;")
        card_layout.addWidget(desc)
        return card

    def _on_outlook_selected(self, checked: bool) -> None:
        if checked:
            self.selected_method = "outlook"
            self.mailbox_section.setVisible(True)

    def _on_smtp_selected(self, checked: bool) -> None:
        if checked:
            self.selected_method = "smtp"
            self.mailbox_section.setVisible(False)

    def _on_continue(self) -> None:
        self.selected_mailbox = self.mailbox_combo.currentText() if self.selected_method == "outlook" else None
        self.accept()

    def get_selected_method(self) -> str:
        return self.selected_method

    def get_selected_mailbox(self) -> str | None:
        return self.selected_mailbox
