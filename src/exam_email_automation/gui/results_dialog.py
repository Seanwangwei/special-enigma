from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QTabWidget, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor


class ResultsDialog(QDialog):
    """Dialog showing processing results."""

    def __init__(self, parent, records: list, delivery_mode: str):
        """
        Args:
            parent: Parent widget
            records: List of dicts with keys: Time, Student ID, Email, Template, Status, Error
            delivery_mode: "preview_only", "create_drafts", or "send_immediately"
        """
        super().__init__(parent)
        self.records = records
        self.delivery_mode = delivery_mode
        self.setWindowTitle("Processing Results")
        self.setGeometry(150, 150, 700, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Summary section
        summary_text = self._build_summary()
        summary_label = QLabel(summary_text)
        summary_font = QFont()
        summary_font.setPointSize(12)
        summary_font.setBold(True)
        summary_label.setFont(summary_font)
        layout.addWidget(summary_label)

        layout.addSpacing(10)

        # Tab for detailed records
        tabs = QTabWidget()

        # All records tab
        all_text = self._build_all_records()
        all_edit = QTextEdit()
        all_edit.setPlainText(all_text)
        all_edit.setReadOnly(True)
        tabs.addTab(all_edit, "All Records")

        # Errors tab
        errors_text = self._build_errors()
        errors_edit = QTextEdit()
        errors_edit.setPlainText(errors_text)
        errors_edit.setReadOnly(True)
        errors_edit.setStyleSheet("color: #d32f2f;")
        tabs.addTab(errors_edit, "Errors")

        layout.addWidget(tabs)

        # Close button
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)

        # Copy log button (future feature)
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(self._copy_to_clipboard)

        button_layout.addStretch()
        button_layout.addWidget(copy_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _build_summary(self) -> str:
        """Build summary statistics."""
        total = len(self.records)
        success = sum(1 for r in self.records if r.get("Status") == "Sent" or r.get("Status") == "Draft Created" or r.get("Status") == "Preview Generated")
        failed = sum(1 for r in self.records if r.get("Status") == "Failed")

        mode_text = {
            "preview_only": "Preview Generated",
            "create_drafts": "Draft Created",
            "send_immediately": "Sent"
        }.get(self.delivery_mode, "Processed")

        lines = [
            f"✓ Processing Complete",
            f"Total: {total} | Success: {success} | Failed: {failed}"
        ]
        return "\n".join(lines)

    def _build_all_records(self) -> str:
        """Build all records display."""
        lines = ["Time | Student ID | Email | Status | Error"]
        lines.append("-" * 100)
        for record in self.records:
            status = record.get("Status", "Unknown")
            error = record.get("Error", "")
            error_str = f"({error})" if error else "OK"
            line = f"{record.get('Time', '')} | {record.get('Student ID', '')} | {record.get('Email', '')} | {status} | {error_str}"
            lines.append(line)
        return "\n".join(lines)

    def _build_errors(self) -> str:
        """Build errors-only display."""
        errors = [r for r in self.records if r.get("Status") == "Failed"]
        if not errors:
            return "No errors!"

        lines = ["Student ID | Email | Error"]
        lines.append("-" * 80)
        for record in errors:
            line = f"{record.get('Student ID', '')} | {record.get('Email', '')} | {record.get('Error', '')}"
            lines.append(line)
        return "\n".join(lines)

    def _copy_to_clipboard(self):
        from PySide6.QtGui import QClipboard
        from PySide6.QtWidgets import QApplication
        
        text = self._build_all_records()
        QApplication.clipboard().setText(text)
        # Show brief feedback
        copy_btn = self.sender()
        if copy_btn:
            original_text = copy_btn.text()
            copy_btn.setText("Copied!")
            from PySide6.QtCore import QTimer
            QTimer.singleShot(1500, lambda: copy_btn.setText(original_text))
