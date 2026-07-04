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
from collections import Counter
from exam_email_automation.config.config_loader import Config
from exam_email_automation.email.delivery_mode import DeliveryMode
from exam_email_automation.excel.excel_reader import ExcelReader
from exam_email_automation.gui.confirmation_dialog import ConfirmationDialog
from exam_email_automation.gui.delivery_method_dialog import DeliveryMethodDialog
from exam_email_automation.gui.delivery_mode_dialog import DeliveryModeDialog
from exam_email_automation.gui.dialogs import ErrorDialog, InfoDialog, PreviewDialog
from exam_email_automation.gui.results_dialog import ResultsDialog
from exam_email_automation.gui.validation_dialog import ValidationResultsDialog
from exam_email_automation.gui.widgets import SectionLabel
from exam_email_automation.logging.logger import configure_logging
from exam_email_automation.services.preview_service import PreviewService
from exam_email_automation.services.send_service import MODE_MAP, SendService
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


class PreviewWorker(QtCore.QThread):
    """Generate HTML previews in a background thread to keep the GUI responsive."""
    progress_changed = Signal(int, int)
    finished = Signal(dict)
    status_message = Signal(str)

    def __init__(self, preview_service: PreviewService, students: list[Student]) -> None:
        super().__init__()
        self.preview_service = preview_service
        self.students = students

    def run(self) -> None:
        html_map: dict[str, str] = {}
        total = len(self.students)
        for index, student in enumerate(self.students, start=1):
            html_map[student.student_id] = self.preview_service.generate_preview_html(student)
            self.progress_changed.emit(index, total)
            self.status_message.emit(f"Generating preview {index} of {total}: {student.full_name}")
        self.finished.emit(html_map)


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
        self.preview_worker: Optional[PreviewWorker] = None
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

        template_status = SectionLabel(self._template_status_text())
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
        try:
            templates = self.template_engine.environment.list_templates()
        except Exception:
            templates = []
        if not templates:
            return "Templates\n(No templates found)"
        statuses = [
            f"{name} ✓ Loaded" if name.endswith(".html") else name
            for name in sorted(templates)
        ]
        return "Templates\n" + " | ".join(statuses)

    def _browse_excel_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select Excel File", str(Path.cwd()), "Excel Files (*.xlsx)")
        if path:
            self.file_path_input.setText(path)
            self._load_excel(Path(path))

    def _browse_attachment(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(self, "Select Attachments", str(self.config.attachment_folder))
        if paths:
            for p in paths:
                self.attachments.append(Path(p))
            current = self.attachment_path_input.text()
            if current:
                current += "; "
            self.attachment_path_input.setText(current + "; ".join(paths))
            self._append_log(f"Added {len(paths)} attachment(s): {'; '.join(paths)}")

    def _load_excel(self, path: Path) -> None:
        try:
            self.students = self.excel_reader.load_students(path)
        except Exception as exc:
            self._append_log(str(exc))
            ErrorDialog.show_error(self, "Load Error", str(exc))
            self.status_label.setText("Failed to load Excel file.")
            return

        self.progress_bar.setMaximum(len(self.students))
        self.progress_label.setText(f"0 / {len(self.students)}")
        self._append_log(f"Loaded {len(self.students)} students from {path}")
        self.status_label.setText("Generating email previews...")

        # Generate HTML previews in a background thread
        self.preview_worker = PreviewWorker(self.preview_service, self.students)
        self.preview_worker.progress_changed.connect(self._on_progress_changed)
        self.preview_worker.status_message.connect(self._append_log)
        self.preview_worker.finished.connect(self._on_preview_finished)
        self.preview_worker.start()

    def _on_preview_finished(self, html_map: dict[str, str]) -> None:
        self.html_map = html_map
        self._append_log("Email previews generated.")
        self.status_label.setText("Excel file loaded successfully.")

    def _preview_emails(self) -> None:
        if not self.students:
            ErrorDialog.show_error(self, "Preview Error", "Please load an Excel file first.")
            return
        dialog = PreviewDialog(self.students, self.html_map, parent=self)
        dialog.exec()

    def _validate_loaded_data(self) -> dict:
        """Validate loaded students and return structured error dict for ValidationResultsDialog."""
        errors: dict[str, list[str]] = {
            "missing_emails": [],
            "duplicate_ids": [],
            "invalid_templates": [],
            "invalid_columns": [],
        }
        if not self.students:
            return errors

        seen_ids: Counter[str] = Counter()
        for student in self.students:
            seen_ids[student.student_id] += 1
            if not student.email or student.email.strip() == "":
                errors["missing_emails"].append(
                    f"{student.full_name} (ID: {student.student_id})"
                )

        for sid, count in seen_ids.items():
            if count > 1:
                errors["duplicate_ids"].append(
                    f"Student ID '{sid}' appears {count} times"
                )

        return errors

    def _build_summary(self, delivery_method: str, delivery_mode: str) -> dict:
        """Build a summary dict for the ConfirmationDialog."""
        pass_count = sum(
            1 for s in self.students
            if "pass" in s.template_name.lower()
        )
        fail_count = sum(
            1 for s in self.students
            if "template 2" in s.template_name.lower()
            or "reassessment" in s.template_name.lower()
        )
        ec_count = sum(
            1 for s in self.students
            if "template 3" in s.template_name.lower()
            or "ec" in s.template_name.lower()
        )
        return {
            "total_students": len(self.students),
            "pass_emails": pass_count,
            "fail_emails": fail_count,
            "ec_emails": ec_count,
            "delivery_mode": delivery_mode,
            "delivery_method": delivery_method,
        }

    def _send_test_email(self) -> None:
        if not self.students:
            ErrorDialog.show_error(self, "Send Test Email", "Please load an Excel file first.")
            return

        # Select student
        labels = [f"{student.full_name} ({student.student_id})" for student in self.students]
        student_index, ok = QInputDialog.getItem(self, "Select Student", "Student:", labels, 0, False)
        if not ok:
            return
        selected_index = labels.index(student_index)
        student = self.students[selected_index]

        # Shortened wizard: Delivery Method → Delivery Mode
        method_dialog = DeliveryMethodDialog(self)
        if method_dialog.exec() != DeliveryMethodDialog.DialogCode.Accepted:
            return
        method = method_dialog.get_selected_method()
        mailbox = method_dialog.get_selected_mailbox()

        mode_dialog = DeliveryModeDialog(self, default_mode="send_immediately")
        if mode_dialog.exec() != DeliveryModeDialog.DialogCode.Accepted:
            return
        mode_str = mode_dialog.get_selected_mode()
        mode = MODE_MAP.get(mode_str, DeliveryMode.CREATE_DRAFTS)

        # Build a temporary SendService with the user's choices
        service = SendService(self.config, delivery_mode=mode, mailbox_email=mailbox)
        # Override provider if SMTP selected in dialog (only for this send)
        if method == "smtp":
            from exam_email_automation.email.smtp_sender import SMTPConfig, SMTPEmailSender
            smtp_cfg = SMTPConfig(
                host=self.config.smtp_host, port=self.config.smtp_port,
                username=self.config.smtp_username, password=self.config.smtp_password,
                use_ssl=self.config.smtp_use_ssl, use_tls=self.config.smtp_use_tls,
            )
            service.email_sender = SMTPEmailSender(smtp_cfg)
            service._is_smtp = True

        html_body = self.html_map.get(student.student_id, "")
        record = service.send_student(student, html_body, self.attachments)
        self._append_log(f"Test email {record['Status']} for {student.full_name}: {record['Error']}")
        self.status_label.setText(f"Test email {record['Status']}")
        if record["Status"] in ("Sent", "Draft Created", "Preview Generated"):
            InfoDialog.show_info(self, "Test Email", f"Test email processed: {record['Status']}.")
        else:
            ErrorDialog.show_error(self, "Test Email Failed", record["Error"])

    def _send_all_emails(self) -> None:
        if not self.students:
            ErrorDialog.show_error(self, "Send All Emails", "Please load an Excel file first.")
            return
        if self.send_worker is not None and self.send_worker.isRunning():
            return

        # Step 1: Validate
        validation_errors = self._validate_loaded_data()
        has_errors = any(v for v in validation_errors.values())
        if has_errors:
            validation_dialog = ValidationResultsDialog(self, validation_errors)
            if validation_dialog.exec() != ValidationResultsDialog.DialogCode.Accepted:
                self._append_log("Send cancelled by user after validation errors.")
                self.status_label.setText("Send cancelled.")
                return

        # Step 2: Delivery Method (Outlook vs SMTP)
        method_dialog = DeliveryMethodDialog(self)
        if method_dialog.exec() != DeliveryMethodDialog.DialogCode.Accepted:
            self._append_log("Send cancelled at delivery method selection.")
            self.status_label.setText("Send cancelled.")
            return
        delivery_method = method_dialog.get_selected_method()
        mailbox = method_dialog.get_selected_mailbox()
        self._append_log(f"Delivery method: {delivery_method}")

        # Step 3: Delivery Mode (Preview / Draft / Send)
        default_mode = self.config.delivery_mode if hasattr(self.config, 'delivery_mode') else "create_drafts"
        mode_dialog = DeliveryModeDialog(self, default_mode=default_mode)
        if mode_dialog.exec() != DeliveryModeDialog.DialogCode.Accepted:
            self._append_log("Send cancelled at delivery mode selection.")
            self.status_label.setText("Send cancelled.")
            return
        mode_str = mode_dialog.get_selected_mode()
        delivery_mode = MODE_MAP.get(mode_str, DeliveryMode.CREATE_DRAFTS)
        self._append_log(f"Delivery mode: {mode_str}")

        # Step 4: Confirmation
        summary = self._build_summary(delivery_method, mode_str)
        confirm_dialog = ConfirmationDialog(self, summary)
        if confirm_dialog.exec() != ConfirmationDialog.DialogCode.Accepted:
            self._append_log("Send cancelled at confirmation.")
            self.status_label.setText("Send cancelled.")
            return

        # Step 5: Execute
        service = SendService(self.config, delivery_mode=delivery_mode, mailbox_email=mailbox)
        if delivery_method == "smtp":
            from exam_email_automation.email.smtp_sender import SMTPConfig, SMTPEmailSender
            smtp_cfg = SMTPConfig(
                host=self.config.smtp_host, port=self.config.smtp_port,
                username=self.config.smtp_username, password=self.config.smtp_password,
                use_ssl=self.config.smtp_use_ssl, use_tls=self.config.smtp_use_tls,
            )
            service.email_sender = SMTPEmailSender(smtp_cfg)
            service._is_smtp = True

        self.send_worker = SendWorker(service, self.students, self.html_map, self.attachments)
        self.send_worker.progress_changed.connect(self._on_progress_changed)
        self.send_worker.status_message.connect(self._append_log)
        self.send_worker.finished.connect(self._on_send_finished)
        self.send_worker.start()
        self.status_label.setText("Processing emails...")

    def _on_progress_changed(self, completed: int, total: int) -> None:
        self.progress_bar.setValue(completed)
        self.progress_label.setText(f"{completed} / {total}")

    def _on_send_finished(self, records: list[dict[str, str]]) -> None:
        success = sum(1 for record in records if record["Status"] in ("Sent", "Draft Created", "Preview Generated", "Sent (SMTP)"))
        failure = len(records) - success
        self._append_log(f"Completed: {success} processed, {failure} failed.")
        self.status_label.setText("Send process completed.")

        # Determine delivery mode for the results dialog
        mode_str = self.config.delivery_mode
        results_dialog = ResultsDialog(self, records, mode_str)
        results_dialog.exec()

    def _append_log(self, message: str) -> None:
        self.log_output.append(message)
