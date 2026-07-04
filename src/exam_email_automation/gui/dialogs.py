from pathlib import Path
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QTextBrowser, QMessageBox
from exam_email_automation.models.student import Student


class PreviewDialog(QDialog):
    def __init__(self, students: list[Student], html_map: dict[str, str], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Email Preview")
        self.students = students
        self.html_map = html_map
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        title = QLabel("Select a student to preview the generated email.")
        layout.addWidget(title)

        body_layout = QHBoxLayout()
        self.list_widget = QListWidget()
        self.text_browser = QTextBrowser()
        body_layout.addWidget(self.list_widget, 1)
        body_layout.addWidget(self.text_browser, 2)
        layout.addLayout(body_layout)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

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
    @staticmethod
    def show_error(parent, title: str, message: str) -> None:
        QMessageBox.critical(parent, title, message)


class InfoDialog:
    @staticmethod
    def show_info(parent, title: str, message: str) -> None:
        QMessageBox.information(parent, title, message)
