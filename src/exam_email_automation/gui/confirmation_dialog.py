"""Confirmation dialog — Step 3/3 of the send wizard with stats summary and delivery info."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
)

from exam_email_automation.gui.widgets import StepIndicator


class ConfirmationDialog(QDialog):
    """Step 3/3 of the send wizard: review summary and confirm."""

    def __init__(self, parent, summary: dict) -> None:
        super().__init__(parent)
        self.summary = summary
        self.setWindowTitle("Ready to Process")
        self.setMinimumSize(460, 420)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Step indicator
        self.steps = StepIndicator(["Method", "Mode", "Confirm"])
        self.steps.set_current_step(2)
        self.steps.mark_done(0)
        self.steps.mark_done(1)
        layout.addWidget(self.steps)

        # Title
        title = QLabel("Ready to Process")
        title.setStyleSheet("font-size: 16px; font-weight: 600; color: #1e293b; border: none; background: transparent;")
        layout.addWidget(title)

        # Stats card
        stats_card = QFrame()
        stats_card.setStyleSheet(
            "QFrame { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; }"
        )
        stats_layout = QVBoxLayout(stats_card)
        stats_layout.setContentsMargins(16, 14, 16, 14)
        stats_layout.setSpacing(4)

        stats_header = QLabel("SUMMARY")
        stats_header.setStyleSheet("font-size: 11px; font-weight: 600; color: #94a3b8; border: none; background: transparent;")
        stats_header.setAlignment(0x0004)  # AlignCenter
        stats_layout.addWidget(stats_header)

        divider = QLabel("━━━━━━━━━━━━━━━━━━━━━━")
        divider.setStyleSheet("font-family: monospace; font-size: 12px; color: #cbd5e1; border: none; background: transparent;")
        divider.setAlignment(0x0004)
        stats_layout.addWidget(divider)

        total = self.summary.get("total_students", 0)
        students_label = QLabel(f"Students:  {total}")
        students_label.setStyleSheet("font-family: SF Mono, Consolas, monospace; font-size: 13px; color: #1e293b; font-weight: 700; border: none; background: transparent;")
        students_label.setAlignment(0x0004)
        stats_layout.addWidget(students_label)

        stats_layout.addSpacing(6)

        passes = self.summary.get("pass_emails", 0)
        pass_label = QLabel(f"PASS emails:    {passes}")
        pass_label.setStyleSheet("font-family: SF Mono, Consolas, monospace; font-size: 13px; color: #16a34a; font-weight: 600; border: none; background: transparent;")
        pass_label.setAlignment(0x0004)
        stats_layout.addWidget(pass_label)

        fails = self.summary.get("fail_emails", 0)
        fail_label = QLabel(f"FAIL emails:    {fails}")
        fail_label.setStyleSheet("font-family: SF Mono, Consolas, monospace; font-size: 13px; color: #dc2626; font-weight: 600; border: none; background: transparent;")
        fail_label.setAlignment(0x0004)
        stats_layout.addWidget(fail_label)

        ecs = self.summary.get("ec_emails", 0)
        ec_label = QLabel(f"EC emails:      {ecs}")
        ec_label.setStyleSheet("font-family: SF Mono, Consolas, monospace; font-size: 13px; color: #d97706; font-weight: 600; border: none; background: transparent;")
        ec_label.setAlignment(0x0004)
        stats_layout.addWidget(ec_label)

        divider2 = QLabel("━━━━━━━━━━━━━━━━━━━━━━")
        divider2.setStyleSheet("font-family: monospace; font-size: 12px; color: #cbd5e1; border: none; background: transparent;")
        divider2.setAlignment(0x0004)
        stats_layout.addWidget(divider2)

        layout.addWidget(stats_card)

        # Delivery info card (blue accent)
        delivery_card = QFrame()
        delivery_card.setStyleSheet(
            "QFrame { background-color: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 12px; }"
        )
        delivery_layout = QVBoxLayout(delivery_card)
        delivery_layout.setContentsMargins(12, 10, 12, 10)
        delivery_layout.setSpacing(2)

        delivery_title = QLabel("Delivery")
        delivery_title.setStyleSheet("font-weight: 600; color: #2563eb; font-size: 13px; border: none; background: transparent;")
        delivery_layout.addWidget(delivery_title)

        method = self.summary.get("delivery_method", "outlook")
        mode = self.summary.get("delivery_mode", "create_drafts")
        method_display = "Outlook (Desktop)" if method == "outlook" else "SMTP"
        mode_map = {
            "preview_only": "Preview Only",
            "create_drafts": "Create Drafts",
            "send_immediately": "Send Immediately",
        }
        mode_display = mode_map.get(mode, mode)

        delivery_detail = QLabel(f"{method_display} · {mode_display}")
        delivery_detail.setStyleSheet("font-size: 12px; color: #64748b; border: none; background: transparent;")
        delivery_layout.addWidget(delivery_detail)

        layout.addWidget(delivery_card)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        back_btn = QPushButton("Back")
        back_btn.setProperty("cssClass", "ghost")
        back_btn.clicked.connect(self.reject)
        process_btn = QPushButton(f"📨 Process {total} Emails")
        process_btn.setProperty("cssClass", "primary")
        process_btn.setProperty("cssClass", "lg")
        process_btn.clicked.connect(self.accept)
        button_layout.addWidget(back_btn)
        button_layout.addStretch()
        button_layout.addWidget(process_btn)
        layout.addLayout(button_layout)
