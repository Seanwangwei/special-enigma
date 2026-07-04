"""Results dialog — post-send summary with tabbed records and clipboard copy."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit,
    QTabWidget, QWidget, QFrame,
)
from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont

from exam_email_automation.gui.widgets import BadgeLabel


class ResultsDialog(QDialog):
    """Post-processing results with tabbed view and success/error breakdown."""

    def __init__(self, parent, records: list[dict], delivery_mode: str) -> None:
        super().__init__(parent)
        self.records = records
        self.delivery_mode = delivery_mode
        self.setWindowTitle("Processing Results")
        self.setMinimumSize(640, 500)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Success header
        header_row = QHBoxLayout()
        header_row.setSpacing(12)

        check_circle = QLabel("✓")
        check_circle.setFixedSize(40, 40)
        check_circle.setAlignment(0x0004)
        check_circle.setStyleSheet(
            "font-size: 20px; color: #16a34a; background-color: #f0fdf4; "
            "border-radius: 20px; border: none; font-weight: bold;"
        )
        header_row.addWidget(check_circle)

        header_text_col = QVBoxLayout()
        header_text_col.setSpacing(2)

        header_title = QLabel("Processing Complete")
        header_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #1e293b; border: none; background: transparent;")
        header_text_col.addWidget(header_title)

        sent_count = self._count_status("Sent", "Draft Created", "Preview Generated", "Sent (SMTP)")
        failed_count = self._count_status("Failed")

        badges_row = QHBoxLayout()
        badges_row.setSpacing(6)
        sent_badge = BadgeLabel(f"{sent_count} sent", variant="success")
        failed_badge = BadgeLabel(f"{failed_count} failed", variant="error")
        badges_row.addWidget(sent_badge)
        badges_row.addWidget(failed_badge)
        badges_row.addStretch()
        header_text_col.addLayout(badges_row)

        header_row.addLayout(header_text_col)
        header_row.addStretch()
        layout.addLayout(header_row)

        # Tabs
        tabs = QTabWidget()

        # All Records tab
        all_tab = QWidget()
        all_layout = QVBoxLayout(all_tab)
        all_layout.setContentsMargins(8, 8, 8, 8)
        all_text = self._build_all_records()
        all_edit = QTextEdit()
        all_edit.setFont(QFont("SF Mono, Consolas, monospace", 11))
        all_edit.setPlainText(all_text)
        all_edit.setReadOnly(True)
        all_edit.setStyleSheet(
            "QTextEdit { background-color: #f8fafc; border: 1px solid #e2e8f0; "
            "border-radius: 6px; padding: 10px; font-size: 12px; }"
        )
        all_layout.addWidget(all_edit)
        tabs.addTab(all_tab, "All Records")

        # Errors tab
        errors_tab = QWidget()
        errors_layout = QVBoxLayout(errors_tab)
        errors_layout.setContentsMargins(8, 8, 8, 8)
        errors_text = self._build_errors()
        errors_edit = QTextEdit()
        errors_edit.setFont(QFont("SF Mono, Consolas, monospace", 11))
        errors_edit.setPlainText(errors_text)
        errors_edit.setReadOnly(True)
        errors_edit.setStyleSheet(
            "QTextEdit { background-color: #fef2f2; border: 1px solid #fecaca; "
            "border-radius: 6px; padding: 10px; font-size: 12px; color: #dc2626; }"
        )
        errors_layout.addWidget(errors_edit)
        error_count = self._count_status("Failed")
        tab_label = f"Errors ({error_count})" if error_count else "Errors"
        tabs.addTab(errors_tab, tab_label)

        layout.addWidget(tabs)

        # Buttons
        button_layout = QHBoxLayout()
        copy_btn = QPushButton("📋 Copy to Clipboard")
        copy_btn.setProperty("cssClass", "secondary")
        copy_btn.clicked.connect(self._copy_to_clipboard)
        close_btn = QPushButton("Close")
        close_btn.setProperty("cssClass", "primary")
        close_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(copy_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

    def _count_status(self, *statuses: str) -> int:
        return sum(1 for r in self.records if r.get("Status") in statuses)

    def _build_all_records(self) -> str:
        lines = ["Time       | Student ID | Email                              | Status | Error"]
        lines.append("─" * 90)
        for record in self.records:
            status = record.get("Status", "Unknown")
            error = record.get("Error", "")
            error_str = error if error else "—"
            line = (
                f"{record.get('Time', ''):10} | "
                f"{record.get('Student ID', ''):10} | "
                f"{record.get('Email', ''):34} | "
                f"{status:6} | "
                f"{error_str}"
            )
            lines.append(line)
        return "\n".join(lines)

    def _build_errors(self) -> str:
        errors = [r for r in self.records if r.get("Status") == "Failed"]
        if not errors:
            return "No errors!"

        lines = ["Student ID | Email                              | Error"]
        lines.append("─" * 70)
        for record in errors:
            line = (
                f"{record.get('Student ID', ''):10} | "
                f"{record.get('Email', ''):34} | "
                f"{record.get('Error', '')}"
            )
            lines.append(line)
        return "\n".join(lines)

    def _copy_to_clipboard(self) -> None:
        from PySide6.QtWidgets import QApplication

        text = self._build_all_records()
        QApplication.clipboard().setText(text)
        btn = self.sender()
        if btn is not None and isinstance(btn, QPushButton):
            original = btn.text()
            btn.setText("✓ Copied!")
            QTimer.singleShot(1500, lambda b=btn, t=original: b.setText(t) if not b.isDestroyed() else None)
