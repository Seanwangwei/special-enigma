"""General-purpose dialogs: Preview, About, Error, Info."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QTextBrowser, QMessageBox, QFrame,
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

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


class AboutDialog(QDialog):
    """About dialog showing app name, version, icon, and tech stack."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        from exam_email_automation.version import get_version_string
        self._version = get_version_string()
        self.setWindowTitle("About Exam Email Automation")
        self.setFixedSize(400, 280)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        # Icon + name + version row
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        icon_label = QLabel()
        icon_pixmap = QPixmap()
        # Try loading the icon file via the same search logic as icon.py
        from exam_email_automation.gui.icon import _find_icon_file
        png_path = _find_icon_file("icon.png")
        if png_path is not None:
            icon_pixmap = QPixmap(str(png_path))
        if icon_pixmap.isNull():
            # Fallback: use the programmatic icon rendered at 48x48
            from exam_email_automation.gui.icon import create_app_icon
            icon_pixmap = create_app_icon().pixmap(48, 48)
        else:
            icon_pixmap = icon_pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon_label.setPixmap(icon_pixmap)
        icon_label.setFixedSize(48, 48)
        header_layout.addWidget(icon_label)

        title_layout = QVBoxLayout()
        name_label = QLabel("Exam Email Automation")
        name_label.setStyleSheet("font-size: 16px; font-weight: 700; color: #1e293b; border: none; background: transparent;")
        version_label = QLabel(self._version)
        version_label.setStyleSheet("font-size: 13px; color: #64748b; border: none; background: transparent;")
        title_layout.addWidget(name_label)
        title_layout.addWidget(version_label)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Description
        desc_label = QLabel(
            "Automate personalized exam result emails for\n"
            "Registrar Office staff. Import Excel, review\n"
            "previews, and deliver via Outlook or SMTP."
        )
        desc_label.setStyleSheet("font-size: 13px; color: #475569; border: none; background: transparent; line-height: 1.5;")
        layout.addWidget(desc_label)

        # Tech stack
        tech_label = QLabel("Built with Python 3.12, PySide6, Jinja2")
        tech_label.setStyleSheet("font-size: 11px; color: #94a3b8; border: none; background: transparent;")
        layout.addWidget(tech_label)

        layout.addStretch()

        # OK button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        ok_button = QPushButton("OK")
        ok_button.setProperty("cssClass", "primary")
        ok_button.clicked.connect(self.close)
        ok_button.setFixedWidth(80)
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)


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
