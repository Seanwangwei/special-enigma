"""General-purpose dialogs: Preview, Error, Info."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QTextBrowser, QMessageBox, QFrame,
)

from exam_email_automation.models.student import Student


class PreviewDialog(QDialog):
    """Split-pane email preview dialog — student list on left, rendered email on right."""

    def __init__(self, students: list[Student], html_map: dict[str, str], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Email Preview")
        self.setMinimumSize(640, 420)
        self.students = students
        self.html_map = html_map
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Instructions
        instructions = QLabel("Select a student to preview the generated email.")
        instructions.setStyleSheet("font-size: 13px; color: #64748b; border: none; background: transparent;")
        layout.addWidget(instructions)

        # Split pane
        body_layout = QHBoxLayout()
        body_layout.setSpacing(10)

        self.list_widget = QListWidget()
        self.list_widget.setFixedWidth(180)
        body_layout.addWidget(self.list_widget)

        self.text_browser = QTextBrowser()
        body_layout.addWidget(self.text_browser, 1)
        layout.addLayout(body_layout, 1)

        # Separator and close button
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("QFrame { color: #e2e8f0; border: none; border-top: 1px solid #e2e8f0; }")
        layout.addWidget(separator)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_button = QPushButton("Close")
        close_button.setProperty("cssClass", "secondary")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

        # Populate student list
        for student in self.students:
            self.list_widget.addItem(f"{student.full_name} ({student.student_id})")

        self.list_widget.currentRowChanged.connect(self._on_selection_changed)
        if self.students:
            self.list_widget.setCurrentRow(0)

    def _on_selection_changed(self, index: int) -> None:
        if index < 0 or index >= len(self.students):
            self.text_browser.setHtml("")
            return

        student = self.students[index]
        html = self.html_map.get(student.student_id, "")
        self.text_browser.setHtml(html)


class ErrorDialog:
    """Static convenience for critical error message boxes."""

    @staticmethod
    def show_error(parent, title: str, message: str) -> None:
        QMessageBox.critical(parent, title, message)


class InfoDialog:
    """Static convenience for informational message boxes."""

    @staticmethod
    def show_info(parent, title: str, message: str) -> None:
        QMessageBox.information(parent, title, message)
