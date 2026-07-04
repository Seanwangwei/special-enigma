"""Validation results dialog — shows column/email/duplicate errors with color-coded details."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QFrame,
)


class ValidationResultsDialog(QDialog):
    """Dialog showing validation errors with a red warning card and two actions."""

    def __init__(self, parent, validation_errors: dict) -> None:
        super().__init__(parent)
        self.validation_errors = validation_errors
        self.setWindowTitle("Validation Results")
        self.setMinimumSize(460, 380)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Title
        title = QLabel("⚠ Validation Issues Found")
        title.setStyleSheet("font-size: 16px; font-weight: 600; color: #1e293b; border: none; background: transparent;")
        layout.addWidget(title)

        # Error summary card (red)
        error_count = self._count_errors()
        error_card = QFrame()
        error_card.setStyleSheet(
            "QFrame { background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 12px; }"
        )
        error_card_layout = QVBoxLayout(error_card)
        error_card_layout.setContentsMargins(12, 12, 12, 12)
        error_summary = QLabel(f"{error_count} validation issue(s) detected")
        error_summary.setStyleSheet("font-weight: 600; color: #dc2626; font-size: 13px; border: none; background: transparent;")
        error_hint = QLabel("The email cannot be generated correctly until these are resolved.")
        error_hint.setStyleSheet("font-size: 11px; color: #dc2626; border: none; background: transparent;")
        error_card_layout.addWidget(error_summary)
        error_card_layout.addWidget(error_hint)
        layout.addWidget(error_card)

        # Details section
        details_label = QLabel("Details")
        details_label.setStyleSheet("font-weight: 600; font-size: 13px; color: #1e293b; border: none; background: transparent;")
        layout.addWidget(details_label)

        details_text = self._build_details()
        details_edit = QTextEdit()
        details_edit.setHtml(details_text)
        details_edit.setReadOnly(True)
        details_edit.setMinimumHeight(120)
        details_edit.setStyleSheet(
            "QTextEdit { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px; font-size: 12px; }"
        )
        layout.addWidget(details_edit)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        continue_btn = QPushButton("Continue Anyway")
        continue_btn.setProperty("cssClass", "ghost")
        continue_btn.clicked.connect(self.accept)
        fix_btn = QPushButton("Go Back && Fix")
        fix_btn.setProperty("cssClass", "primary")
        fix_btn.clicked.connect(self.reject)
        button_layout.addWidget(continue_btn)
        button_layout.addWidget(fix_btn)
        layout.addLayout(button_layout)

    def _count_errors(self) -> int:
        return sum(len(v) for v in self.validation_errors.values())

    def _build_details(self) -> str:
        parts: list[str] = []

        missing = self.validation_errors.get("missing_emails", [])
        if missing:
            parts.append(
                '<p><span style="color:#dc2626;font-weight:600;">✗ Missing emails:</span> '
                f'{", ".join(missing[:10])}'
                f'{"..." if len(missing) > 10 else ""}</p>'
            )

        dupes = self.validation_errors.get("duplicate_ids", [])
        if dupes:
            parts.append(
                '<p><span style="color:#d97706;font-weight:600;">⚠ Duplicate IDs:</span> '
                f'{", ".join(dupes[:10])}'
                f'{"..." if len(dupes) > 10 else ""}</p>'
            )

        invalid_tmpl = self.validation_errors.get("invalid_templates", [])
        if invalid_tmpl:
            parts.append(
                '<p><span style="color:#dc2626;font-weight:600;">✗ Invalid templates:</span> '
                f'{", ".join(invalid_tmpl[:10])}</p>'
            )

        invalid_cols = self.validation_errors.get("invalid_columns", [])
        if invalid_cols:
            parts.append(
                '<p><span style="color:#d97706;font-weight:600;">⚠ Invalid columns:</span> '
                f'{", ".join(invalid_cols[:10])}</p>'
            )

        if not parts:
            return "<p>No errors found.</p>"
        return "".join(parts)
