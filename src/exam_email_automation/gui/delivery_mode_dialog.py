"""Delivery mode dialog — Preview / Drafts / Send with step indicator and radio cards."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QRadioButton,
    QButtonGroup, QFrame,
)

from exam_email_automation.gui.widgets import StepIndicator


class DeliveryModeDialog(QDialog):
    """Step 2/3 of the send wizard: choose delivery mode."""

    def __init__(self, parent, default_mode: str = "create_drafts") -> None:
        super().__init__(parent)
        self.setWindowTitle("Delivery Mode")
        self.setMinimumSize(460, 400)

        self.selected_mode = default_mode
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Step indicator
        self.steps = StepIndicator(["Method", "Mode", "Confirm"])
        self.steps.set_current_step(1)
        self.steps.mark_done(0)
        layout.addWidget(self.steps)

        # Title
        title = QLabel("How would you like to process the emails?")
        title.setStyleSheet("font-size: 16px; font-weight: 600; color: #1e293b; border: none; background: transparent;")
        layout.addWidget(title)

        # Mode options
        options_frame = QFrame()
        options_frame.setStyleSheet("QFrame { background: transparent; border: none; }")
        options_layout = QVBoxLayout(options_frame)
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.setSpacing(8)

        self.mode_group = QButtonGroup(self)

        # Preview Only
        self.preview_radio = QRadioButton("🔍 Preview Only")
        self.preview_radio.setChecked(self.selected_mode == "preview_only")
        self.mode_group.addButton(self.preview_radio, 0)
        options_layout.addWidget(self._wrap_radio(
            self.preview_radio,
            "Generate HTML previews without sending any emails",
        ))

        # Create Drafts (default)
        self.draft_radio = QRadioButton("📝 Create Outlook Drafts (Default)")
        self.draft_radio.setChecked(self.selected_mode == "create_drafts")
        self.mode_group.addButton(self.draft_radio, 1)
        options_layout.addWidget(self._wrap_radio(
            self.draft_radio,
            "Create unsent draft emails in Outlook for review before sending",
        ))

        # Send Immediately
        self.send_radio = QRadioButton("📨 Send Immediately")
        self.send_radio.setChecked(self.selected_mode == "send_immediately")
        self.mode_group.addButton(self.send_radio, 2)
        options_layout.addWidget(self._wrap_radio(
            self.send_radio,
            "Send emails directly to students without further confirmation",
        ))

        layout.addWidget(options_frame)

        # Wire up changes
        self.preview_radio.toggled.connect(lambda checked: self._on_mode_changed(checked, "preview_only"))
        self.draft_radio.toggled.connect(lambda checked: self._on_mode_changed(checked, "create_drafts"))
        self.send_radio.toggled.connect(lambda checked: self._on_mode_changed(checked, "send_immediately"))

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        back_btn = QPushButton("Back")
        back_btn.setProperty("cssClass", "ghost")
        back_btn.clicked.connect(self.reject)
        continue_btn = QPushButton("Continue")
        continue_btn.setProperty("cssClass", "primary")
        continue_btn.clicked.connect(self.accept)
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

    def _on_mode_changed(self, checked: bool, mode: str) -> None:
        if checked:
            self.selected_mode = mode

    def get_selected_mode(self) -> str:
        return self.selected_mode
