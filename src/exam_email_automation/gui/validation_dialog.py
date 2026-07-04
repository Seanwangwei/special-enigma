from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QScrollArea, QWidget
)
from PySide6.QtCore import Qt
from typing import Optional


class ValidationResultsDialog(QDialog):
    """Dialog showing validation errors and summary."""

    def __init__(self, parent, validation_errors: dict):
        """
        Args:
            parent: Parent widget
            validation_errors: Dict with keys like 'missing_emails', 'duplicate_ids', 'invalid_templates'
                               Values are lists of error details.
        """
        super().__init__(parent)
        self.validation_errors = validation_errors
        self.setWindowTitle("Validation Results")
        self.setGeometry(200, 200, 600, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Summary section
        summary_text = self._build_summary()
        summary_label = QLabel(summary_text)
        summary_label.setStyleSheet("font-weight: bold; color: #d32f2f;")
        layout.addWidget(QLabel("Validation Errors:"))
        layout.addWidget(summary_label)

        layout.addSpacing(10)

        # Detailed errors
        layout.addWidget(QLabel("Details:"))
        details_text = self._build_details()
        details_edit = QTextEdit()
        details_edit.setPlainText(details_text)
        details_edit.setReadOnly(True)
        layout.addWidget(details_edit)

        # Buttons
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _build_summary(self) -> str:
        """Build summary line like '4 students missing email, 2 duplicated IDs'."""
        summary_parts = []

        missing_emails = self.validation_errors.get("missing_emails", [])
        if missing_emails:
            summary_parts.append(f"{len(missing_emails)} students missing email")

        duplicate_ids = self.validation_errors.get("duplicate_ids", [])
        if duplicate_ids:
            summary_parts.append(f"{len(duplicate_ids)} duplicated IDs")

        invalid_templates = self.validation_errors.get("invalid_templates", [])
        if invalid_templates:
            summary_parts.append(f"{len(invalid_templates)} invalid template")

        invalid_columns = self.validation_errors.get("invalid_columns", [])
        if invalid_columns:
            summary_parts.append(f"{len(invalid_columns)} invalid columns")

        return ", ".join(summary_parts) if summary_parts else "No errors"

    def _build_details(self) -> str:
        """Build detailed error list."""
        lines = []

        missing_emails = self.validation_errors.get("missing_emails", [])
        if missing_emails:
            lines.append(f"Missing Email ({len(missing_emails)}):")
            for detail in missing_emails[:10]:  # Show first 10
                lines.append(f"  - {detail}")
            if len(missing_emails) > 10:
                lines.append(f"  ... and {len(missing_emails) - 10} more")
            lines.append("")

        duplicate_ids = self.validation_errors.get("duplicate_ids", [])
        if duplicate_ids:
            lines.append(f"Duplicated IDs ({len(duplicate_ids)}):")
            for detail in duplicate_ids[:10]:
                lines.append(f"  - {detail}")
            if len(duplicate_ids) > 10:
                lines.append(f"  ... and {len(duplicate_ids) - 10} more")
            lines.append("")

        invalid_templates = self.validation_errors.get("invalid_templates", [])
        if invalid_templates:
            lines.append(f"Invalid Template ({len(invalid_templates)}):")
            for detail in invalid_templates[:10]:
                lines.append(f"  - {detail}")
            if len(invalid_templates) > 10:
                lines.append(f"  ... and {len(invalid_templates) - 10} more")
            lines.append("")

        invalid_columns = self.validation_errors.get("invalid_columns", [])
        if invalid_columns:
            lines.append(f"Invalid Columns ({len(invalid_columns)}):")
            for col in invalid_columns:
                lines.append(f"  - {col}")

        return "\n".join(lines) if lines else "No errors found"
