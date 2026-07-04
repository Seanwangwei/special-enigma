from __future__ import annotations

from pathlib import Path
from typing import Optional
from PySide6 import QtCore
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QProgressBar,
    QFileDialog,
    QHBoxLayout,
    QVBoxLayout,
    QGroupBox,
    QInputDialog,
)
from exam_email_automation.config.config_loader import Config
from exam_email_automation.excel.excel_reader import ExcelReader
from exam_email_automation.gui.dialogs import ErrorDialog, InfoDialog, PreviewDialog
from exam_email_automation.logging.logger import configure_logging
from exam_email_automation.services.preview_service import PreviewService
from exam_email_automation.services.send_service import SendService
from exam_email_automation.templates.template_engine import TemplateEngine
from exam_email_automation.models.student import Student


class SendWorker(QtCore.QThread):
    progress_changed = Signal(int, int)
    finished = Signal(list)
    status_message = Signal(str)

    def __init__(self, send_service: SendService, students: list[Student], html_map: dict[str, str], attachments: list[Path]) -> None:
        super().__init__()
        self.send_service = send_service
        self.students = students
        self.html_map = html_map
        self.attachments = attachments

    def run(self) -> None:
        records = []
        total = len(self.students)
        for index, student in enumerate(self.students, start=1):
            html_body = self.html_map.get(student.student_id, "")
            record = self.send_service.send_student(student, html_body, self.attachments)
            records.append(record)
            self.progress_changed.emit(index, total)
            self.status_message.emit(f"Sending {index} of {total}: {student.full_name}")
        self.send_service.audit_logger.save(records)
        self.finished.emit(records)


class MainWindow(QMainWindow):
    def __init__(self, config: Config) -> None:
        super().__init__()
        self.setWindowTitle("Exam Result Email Automation")
        self.config = config
        self.logger = configure_logging(self.config.log_folder)
        self.excel_reader = ExcelReader()
        self.template_engine = TemplateEngine(self.config.templates_folder)
        self.preview_service = PreviewService(self.template_engine, self.config)
        self.send_service = SendService(self.config)
        self.students: list[Student] = []
        self.html_map: dict[str, str] = {}
        self.attachments: list[Path] = []
        self.send_worker: Optional[SendWorker] = None
        self._prepare_folders()
        self._build_ui()

    def _prepare_folders(self) -> None:
        self.config.preview_folder.mkdir(parents=True, exist_ok=True)
        self.config.log_folder.mkdir(parents=True, exist_ok=True)
        self.config.attachment_folder.mkdir(parents=True, exist_ok=True)

    def _build_ui(self) -> None:
        container = QWidget()
        main_layout = QVBoxLayout(container)

        file_group = QGroupBox("Excel File")
        file_layout = QHBoxLayout(file_group)
        self.file_path_input = QLineEdit()
        self.file_path_input.setReadOnly(True)
        browse_excel_button = QPushButton("Browse...")
        browse_excel_button.clicked.connect(self._browse_excel_file)
        file_layout.addWidget(self.file_path_input)
        file_layout.addWidget(browse_excel_button)

        template_status = QLabel(self._template_status_text())
        template_status.setAlignment(Qt.AlignLeft)

        attachment_group = QGroupBox("Attachments")
        attachment_layout = QHBoxLayout(attachment_group)
        self.attachment_path_input = QLineEdit()
        self.attachment_path_input.setReadOnly(True)
        browse_attachment_button = QPushButton("Browse...")
        browse_attachment_button.clicked.connect(self._browse_attachment)
        attachment_layout.addWidget(self.attachment_path_input)
        attachment_layout.addWidget(browse_attachment_button)

        action_group = QGroupBox("Actions")
        action_layout = QHBoxLayout(action_group)
        preview_button = QPushButton("Preview Emails")
        preview_button.clicked.connect(self._preview_emails)
        test_button = QPushButton("Send Test Email")
        test_button.clicked.connect(self._send_test_email)
        send_all_button = QPushButton("Send All Emails")
        send_all_button.clicked.connect(self._send_all_emails)
        action_layout.addWidget(preview_button)
        action_layout.addWidget(test_button)
        action_layout.addWidget(send_all_button)

        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_label = QLabel("0 / 0")
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)

        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout(log_group)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        log_layout.addWidget(self.log_output)

        self.status_label = QLabel("Ready")

        main_layout.addWidget(file_group)
        main_layout.addWidget(template_status)
        main_layout.addWidget(attachment_group)
        main_layout.addWidget(action_group)
        main_layout.addWidget(progress_group)
        main_layout.addWidget(log_group)
        main_layout.addWidget(self.status_label)

        self.setCentralWidget(container)
        self.resize(900, 700)

    def _template_status_text(self) -> str:
        loaded_templates = ["Template 1", "Template 2", "Template 3"]
        statuses = [f"{name} ✓ Loaded" for name in loaded_templates]
        return "Templates\n" + " | ".join(statuses)

    def _browse_excel_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select Excel File", str(Path.cwd()), "Excel Files (*.xlsx)")
        if path:
            self.file_path_input.setText(path)
            self._load_excel(Path(path))

    def _browse_attachment(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select Attachment", str(self.config.attachment_folder))
        if path:
            self.attachments = [Path(path)]
            self.attachment_path_input.setText(path)
            self._append_log(f"Selected attachment: {path}")

    def _load_excel(self, path: Path) -> None:
        try:
            self.students = self.excel_reader.load_students(path)
            self.html_map = {
                student.student_id: self.preview_service.generate_preview_html(student)
                for student in self.students
            }
            self.progress_bar.setMaximum(len(self.students))
            self.progress_label.setText(f"0 / {len(self.students)}")
            self._append_log(f"Loaded {len(self.students)} students from {path}")
            self.status_label.setText("Excel file loaded successfully.")
        except Exception as exc:
            self._append_log(str(exc))
            ErrorDialog.show_error(self, "Load Error", str(exc))
            self.status_label.setText("Failed to load Excel file.")

    def _preview_emails(self) -> None:
        if not self.students:
            ErrorDialog.show_error(self, "Preview Error", "Please load an Excel file first.")
            return
        dialog = PreviewDialog(self.students, self.html_map, parent=self)
        dialog.exec()

    def _send_test_email(self) -> None:
        if not self.students:
            ErrorDialog.show_error(self, "Send Test Email", "Please load an Excel file first.")
            return
        labels = [f"{student.full_name} ({student.student_id})" for student in self.students]
        student_index, ok = QInputDialog.getItem(self, "Select Student", "Student:", labels, 0, False)
        if not ok:
            return
        selected_index = labels.index(student_index)
        student = self.students[selected_index]
        html_body = self.html_map.get(student.student_id, "")
        record = self.send_service.send_student(student, html_body, self.attachments)
        self._append_log(f"Test email {record['Status']} for {student.full_name}: {record['Error']}")
        self.status_label.setText(f"Test email {record['Status']}")
        if record["Status"] == "Sent":
            InfoDialog.show_info(self, "Test Email", "Test email sent successfully.")
        else:
            ErrorDialog.show_error(self, "Test Email Failed", record["Error"])

    def _send_all_emails(self) -> None:
        if not self.students:
            ErrorDialog.show_error(self, "Send All Emails", "Please load an Excel file first.")
            return
        if self.send_worker is not None and self.send_worker.isRunning():
            return
        self.send_worker = SendWorker(self.send_service, self.students, self.html_map, self.attachments)
        self.send_worker.progress_changed.connect(self._on_progress_changed)
        self.send_worker.status_message.connect(self._append_log)
        self.send_worker.finished.connect(self._on_send_finished)
        self.send_worker.start()
        self.status_label.setText("Sending emails...")

    def _on_progress_changed(self, completed: int, total: int) -> None:
        self.progress_bar.setValue(completed)
        self.progress_label.setText(f"{completed} / {total}")

    def _on_send_finished(self, records: list[dict[str, str]]) -> None:
        success = sum(1 for record in records if record["Status"] == "Sent")
        failure = len(records) - success
        self._append_log(f"Completed: {success} sent, {failure} failed.")
        self.status_label.setText("Send process completed.")
        InfoDialog.show_info(self, "Send Complete", f"{success} emails sent. {failure} failed.")

    def _append_log(self, message: str) -> None:
        self.log_output.append(message)
