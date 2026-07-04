from __future__ import annotations

from pathlib import Path
from typing import Optional
from PySide6 import QtCore
from PySide6.QtCore import Qt, Signal, QSettings, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
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
    QApplication,
    QDialog,
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
from exam_email_automation.gui.widgets import BadgeLabel, SectionLabel, StepIndicator
from exam_email_automation.logging.logger import configure_logging
from exam_email_automation.services.preview_service import PreviewService
from exam_email_automation.services.send_service import MODE_MAP, SendService
from exam_email_automation.templates.docx_parser import parse_and_convert, SPECIAL_VARIABLES
from exam_email_automation.templates.template_engine import TemplateEngine
from exam_email_automation.templates.template_metadata import TemplateMeta, load_companion_yaml
from exam_email_automation.validation.validator import Validator
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
        self.template_meta: Optional[TemplateMeta] = None
        self._prepare_folders()
        self._build_ui()
        self._setup_shortcuts()
        self._load_settings()

    def _prepare_folders(self) -> None:
        self.config.preview_folder.mkdir(parents=True, exist_ok=True)
        self.config.log_folder.mkdir(parents=True, exist_ok=True)
        self.config.attachment_folder.mkdir(parents=True, exist_ok=True)

    def _build_ui(self) -> None:
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # --- Template Upload Section ---
        template_group = QGroupBox("📄 Email Template (.docx)")
        template_layout = QVBoxLayout(template_group)
        template_row = QHBoxLayout()
        self.template_path_input = QLineEdit()
        self.template_path_input.setReadOnly(True)
        self.template_path_input.setPlaceholderText("Upload a Word template with {{variables}}...")
        upload_template_button = QPushButton("Browse…")
        upload_template_button.setProperty("cssClass", "secondary")
        upload_template_button.clicked.connect(self._upload_docx_template)
        clear_template_button = QPushButton("Clear")
        clear_template_button.setProperty("cssClass", "ghost")
        clear_template_button.clicked.connect(self._clear_uploaded_template)
        template_row.addWidget(self.template_path_input, 1)
        template_row.addWidget(upload_template_button)
        template_row.addWidget(clear_template_button)
        template_layout.addLayout(template_row)
        # Badge container for detected variables
        self.template_badges_layout = QHBoxLayout()
        self.template_badges_layout.setSpacing(4)
        self.template_badges_layout.addStretch()
        template_layout.addLayout(self.template_badges_layout)
        self.template_vars_label = QLabel("")
        self.template_vars_label.setProperty("cssClass", "template-vars")
        self.template_vars_label.setVisible(False)
        template_layout.addWidget(self.template_vars_label)

        # --- Excel File Section ---
        file_group = QGroupBox("📊 Excel File")
        file_layout = QHBoxLayout(file_group)
        self.file_path_input = QLineEdit()
        self.file_path_input.setReadOnly(True)
        self.file_path_input.setPlaceholderText("Browse for student results spreadsheet (.xlsx)...")
        browse_excel_button = QPushButton("Browse…")
        browse_excel_button.setProperty("cssClass", "secondary")
        browse_excel_button.clicked.connect(self._browse_excel_file)
        clear_excel_button = QPushButton("Clear")
        clear_excel_button.setProperty("cssClass", "ghost")
        clear_excel_button.clicked.connect(self._clear_excel)
        file_layout.addWidget(self.file_path_input, 1)
        file_layout.addWidget(browse_excel_button)
        file_layout.addWidget(clear_excel_button)

        # --- Attachments Section ---
        attachment_group = QGroupBox("📎 Attachments (optional)")
        attachment_layout = QHBoxLayout(attachment_group)
        self.attachment_path_input = QLineEdit()
        self.attachment_path_input.setReadOnly(True)
        self.attachment_path_input.setPlaceholderText("No file selected")
        browse_attachment_button = QPushButton("Browse…")
        browse_attachment_button.setProperty("cssClass", "secondary")
        browse_attachment_button.clicked.connect(self._browse_attachment)
        clear_attachment_button = QPushButton("Clear")
        clear_attachment_button.setProperty("cssClass", "ghost")
        clear_attachment_button.clicked.connect(self._clear_attachments)
        attachment_layout.addWidget(self.attachment_path_input, 1)
        attachment_layout.addWidget(browse_attachment_button)
        attachment_layout.addWidget(clear_attachment_button)

        # --- Actions Section ---
        action_group = QGroupBox("⚡ Actions")
        action_layout = QHBoxLayout(action_group)
        self.preview_button = QPushButton("▶ Preview Emails")
        self.preview_button.setProperty("cssClass", "primary")
        self.preview_button.clicked.connect(self._preview_emails)
        self.preview_button.setEnabled(False)
        self.test_button = QPushButton("✉ Send Test Email")
        self.test_button.setProperty("cssClass", "secondary")
        self.test_button.clicked.connect(self._send_test_email)
        self.test_button.setEnabled(False)
        self.send_all_button = QPushButton("📨 Send All Emails")
        self.send_all_button.setProperty("cssClass", "secondary")
        self.send_all_button.clicked.connect(self._send_all_emails)
        self.send_all_button.setEnabled(False)
        action_layout.addWidget(self.preview_button)
        action_layout.addWidget(self.test_button)
        action_layout.addWidget(self.send_all_button)

        # --- Progress Section (hidden until data loaded) ---
        self.progress_group = QGroupBox("📈 Progress")
        progress_layout = QVBoxLayout(self.progress_group)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_label = QLabel("0 / 0")
        self.progress_label.setStyleSheet("font-size: 12px; color: #64748b; border: none; background: transparent;")
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        self.progress_group.setVisible(False)

        # --- Log Section (hidden until data loaded) ---
        self.log_group = QGroupBox("📋 Log")
        log_layout = QVBoxLayout(self.log_group)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setProperty("cssClass", "log")
        log_layout.addWidget(self.log_output)
        self.log_group.setVisible(False)

        # --- Status bar ---
        self.status_label = QLabel("Ready")
        self.status_label.setProperty("cssClass", "status-label")

        main_layout.addWidget(template_group)
        main_layout.addWidget(file_group)
        main_layout.addWidget(attachment_group)
        main_layout.addWidget(action_group)
        main_layout.addWidget(self.progress_group)
        main_layout.addWidget(self.log_group)
        main_layout.addWidget(self.status_label)

        self.setCentralWidget(container)
        self.resize(680, 680)
        self.setMinimumSize(480, 400)

    def _clear_excel(self) -> None:
        """Clear the loaded Excel file and reset related state."""
        self.file_path_input.clear()
        self.students = []
        self.html_map = {}
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(0)
        self.progress_label.setText("0 / 0")
        self.preview_button.setEnabled(False)
        self.test_button.setEnabled(False)
        self.send_all_button.setEnabled(False)
        self.progress_group.setVisible(False)
        self.log_group.setVisible(False)
        self._append_log("Excel file cleared.")
        self.status_label.setText("Ready")

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

    def _clear_attachments(self) -> None:
        self.attachments.clear()
        self.attachment_path_input.clear()
        self._append_log("Attachments cleared.")

    def _upload_docx_template(self) -> None:
        """Upload a Word .docx template, parse variables, and register with the engine."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Word Template", str(Path.cwd()),
            "Word Documents (*.docx)"
        )
        if not path:
            return

        docx_path = Path(path)
        try:
            template_info = parse_and_convert(docx_path)
        except Exception as exc:
            ErrorDialog.show_error(self, "Template Error", f"Could not read template:\n{exc}")
            self._append_log(f"Template load failed: {exc}")
            return

        # Check for companion YAML with subject line
        companion = load_companion_yaml(docx_path)
        subject = None
        if companion and isinstance(companion.get("subject"), str):
            subject = companion["subject"].strip()

        # If no subject in YAML, prompt the user
        if not subject:
            subject, ok = QInputDialog.getText(
                self, "Email Subject",
                "Enter the email subject line for this template:",
                text="Exam Results Notification"
            )
            if not ok or not subject.strip():
                ErrorDialog.show_error(self, "Subject Required", "A subject line is required to use the template.")
                return
            subject = subject.strip()

        # Store the old template info for cleanup
        old_meta = self.template_meta

        # Create TemplateMeta
        self.template_meta = TemplateMeta(
            template_name=docx_path.name,
            subject=subject,
            source_type="docx",
            variables=template_info.all_variables,
            special_variables=template_info.special_variables,
            html_content=template_info.html_content,
        )

        # Register with the template engine
        self.template_engine.load_docx_template(template_info.html_content)

        # Update EmailBuilder with the override subject
        self.send_service.email_builder.override_subject = subject

        # Clear previously loaded students (template changed)
        if self.students:
            self._append_log("Template changed — previously loaded student data has been cleared.")
        self.students = []
        self.html_map = {}
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(0)
        self.progress_label.setText("0 / 0")

        # Update UI
        self.template_path_input.setText(path)

        # Show variable badges
        self._clear_template_badges()
        if template_info.all_variables:
            for var in template_info.all_variables:
                badge = BadgeLabel(var, variant="info")
                badge.setToolTip(f"Template variable: {{{{ {var} }}}}")
                self.template_badges_layout.insertWidget(self.template_badges_layout.count() - 1, badge)

        special_note = f" | Special: {', '.join(template_info.special_variables)}" if template_info.special_variables else ""
        self.template_vars_label.setText(f"{len(template_info.all_variables)} variable(s) detected{special_note}")
        self.template_vars_label.setVisible(True)

        self._append_log(
            f"Loaded template: {docx_path.name} | "
            f"Subject: {subject} | "
            f"{len(template_info.simple_variables)} variable(s), "
            f"{len(template_info.special_variables)} special"
        )
        self.status_label.setText("Template loaded. Select an Excel file to continue.")

    def _clear_uploaded_template(self) -> None:
        """Remove the uploaded DOCX template and revert to bundled HTML templates."""
        if self.template_meta is None:
            return

        self.template_engine.unload_uploaded_template()
        self.send_service.email_builder.override_subject = None
        self.template_meta = None
        self.template_path_input.clear()
        self._clear_template_badges()
        self.template_vars_label.setVisible(False)

        # Clear loaded data (bundled templates use student.template_name column)
        self.students = []
        self.html_map = {}
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(0)
        self.progress_label.setText("0 / 0")
        self.preview_button.setEnabled(False)
        self.test_button.setEnabled(False)
        self.send_all_button.setEnabled(False)
        self.progress_group.setVisible(False)

        self._append_log("Uploaded template cleared. Using bundled HTML templates.")
        self.status_label.setText("Ready")

    def _clear_template_badges(self) -> None:
        """Remove all variable badge widgets from the badge layout."""
        while self.template_badges_layout.count() > 1:  # keep the trailing stretch
            item = self.template_badges_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _load_excel(self, path: Path) -> None:
        # When a DOCX template is active, validate columns against template variables
        if self.template_meta is not None and self.template_meta.variables:
            template_vars = self.template_meta.variables
            try:
                # Read just the headers first for validation
                import pandas as pd
                df_headers = pd.read_excel(path, engine="openpyxl", nrows=0)
                report = Validator.validate_template_against_excel(
                    template_vars,
                    df_headers.columns,
                )
                if not report.is_clean:
                    self._show_mismatch_dialog(report, path)
                    return
            except Exception as exc:
                self._append_log(str(exc))
                ErrorDialog.show_error(self, "Load Error", str(exc))
                self.status_label.setText("Failed to read Excel file.")
                return

        try:
            self.students = self.excel_reader.load_students(path)
        except Exception as exc:
            self._append_log(str(exc))
            ErrorDialog.show_error(self, "Load Error", str(exc))
            self.status_label.setText("Failed to load Excel file.")
            return

        self.progress_bar.setMaximum(len(self.students))
        self.progress_label.setText(f"0 / {len(self.students)}")
        self.progress_group.setVisible(True)
        self.log_group.setVisible(True)
        self.preview_button.setEnabled(True)
        self.test_button.setEnabled(True)
        self.send_all_button.setEnabled(True)
        self._append_log(f"Loaded {len(self.students)} students from {path}")
        self.status_label.setText("Generating email previews...")

        # Generate HTML previews in a background thread
        self.preview_worker = PreviewWorker(self.preview_service, self.students)
        self.preview_worker.progress_changed.connect(self._on_progress_changed)
        self.preview_worker.status_message.connect(self._append_log)
        self.preview_worker.finished.connect(self._on_preview_finished)
        self.preview_worker.start()
        QApplication.setOverrideCursor(Qt.WaitCursor)

    def _show_mismatch_dialog(self, report, path: Path) -> None:
        """Show a dialog when template variables don't match Excel columns."""
        from PySide6.QtWidgets import QMessageBox

        msg = QMessageBox(self)
        msg.setWindowTitle("Column Mismatch")
        msg.setIcon(QMessageBox.Warning)

        lines = ["The uploaded template's variables do not match the Excel file columns.\n"]
        if report.missing_in_excel:
            lines.append("Missing from Excel (template needs these):")
            for v in report.missing_in_excel[:10]:
                lines.append(f"  • {{ {{{v}}} }}")
            if len(report.missing_in_excel) > 10:
                lines.append(f"  ... and {len(report.missing_in_excel) - 10} more")
            lines.append("")
        if report.unused_excel_columns:
            lines.append("Unused Excel columns (not in template):")
            for c in report.unused_excel_columns[:10]:
                lines.append(f"  • {c}")
            if len(report.unused_excel_columns) > 10:
                lines.append(f"  ... and {len(report.unused_excel_columns) - 10} more")

        msg.setText("\n".join(lines))
        msg.setInformativeText("Do you want to continue anyway? Missing variables will appear as empty in the email.")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        if msg.exec() == QMessageBox.Yes:
            self._append_log("User chose to continue despite column mismatch.")
            try:
                self.students = self.excel_reader.load_students(path)
            except Exception as exc:
                self._append_log(str(exc))
                ErrorDialog.show_error(self, "Load Error", str(exc))
                self.status_label.setText("Failed to load Excel file.")
                return
            self.progress_bar.setMaximum(len(self.students))
            self.progress_label.setText(f"0 / {len(self.students)}")
            self.progress_group.setVisible(True)
            self.log_group.setVisible(True)
            self.preview_button.setEnabled(True)
            self.test_button.setEnabled(True)
            self.send_all_button.setEnabled(True)
            self._append_log(f"Loaded {len(self.students)} students from {path}")
            self.status_label.setText("Generating email previews...")
            self.preview_worker = PreviewWorker(self.preview_service, self.students)
            self.preview_worker.progress_changed.connect(self._on_progress_changed)
            self.preview_worker.status_message.connect(self._append_log)
            self.preview_worker.finished.connect(self._on_preview_finished)
            self.preview_worker.start()
            QApplication.setOverrideCursor(Qt.WaitCursor)
        else:
            self._append_log("Excel load cancelled due to column mismatch.")
            self.status_label.setText("Ready")

    def _on_preview_finished(self, html_map: dict[str, str]) -> None:
        self.html_map = html_map
        self._append_log("Email previews generated.")
        self.status_label.setText("Excel file loaded successfully.")
        QApplication.restoreOverrideCursor()

    def _preview_emails(self) -> None:
        if not self.students:
            ErrorDialog.show_error(self, "Preview Error", "Please load an Excel file first.")
            return
        dialog = PreviewDialog(self.students, self.html_map, parent=self)
        self._center_dialog(dialog)
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
        self._center_dialog(method_dialog)
        if method_dialog.exec() != DeliveryMethodDialog.DialogCode.Accepted:
            return
        method = method_dialog.get_selected_method()
        mailbox = method_dialog.get_selected_mailbox()

        mode_dialog = DeliveryModeDialog(self, default_mode="send_immediately")
        self._center_dialog(mode_dialog)
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
            self._center_dialog(validation_dialog)
            if validation_dialog.exec() != ValidationResultsDialog.DialogCode.Accepted:
                self._append_log("Send cancelled by user after validation errors.")
                self.status_label.setText("Send cancelled.")
                return

        # Step 2: Delivery Method (Outlook vs SMTP)
        method_dialog = DeliveryMethodDialog(self)
        self._center_dialog(method_dialog)
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
        self._center_dialog(mode_dialog)
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
        self._center_dialog(confirm_dialog)
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
        QApplication.setOverrideCursor(Qt.WaitCursor)

    def _on_progress_changed(self, completed: int, total: int) -> None:
        self.progress_bar.setValue(completed)
        self.progress_label.setText(f"{completed} / {total}")

    def _on_send_finished(self, records: list[dict[str, str]]) -> None:
        QApplication.restoreOverrideCursor()
        success = sum(1 for record in records if record["Status"] in ("Sent", "Draft Created", "Preview Generated", "Sent (SMTP)"))
        failure = len(records) - success
        self._append_log(f"Completed: {success} processed, {failure} failed.")
        self.status_label.setText("Send process completed.")

        # Determine delivery mode for the results dialog
        mode_str = self.config.delivery_mode
        results_dialog = ResultsDialog(self, records, mode_str)
        self._center_dialog(results_dialog)
        results_dialog.exec()

    def _setup_shortcuts(self) -> None:
        """Register keyboard shortcuts for the main window."""
        QShortcut(QKeySequence("Ctrl+O"), self, self._browse_excel_file)
        QShortcut(QKeySequence("Ctrl+P"), self, self._preview_emails)

    def _load_settings(self) -> None:
        settings = QSettings()
        geo = settings.value("main_window/geometry")
        if geo is not None:
            self.restoreGeometry(geo)
        else:
            self.resize(680, 680)

    def _save_settings(self) -> None:
        settings = QSettings()
        settings.setValue("main_window/geometry", self.saveGeometry())

    def _center_dialog(self, dialog: QDialog) -> None:
        """Center a dialog relative to this main window."""
        dialog.adjustSize()
        center = self.mapToGlobal(self.rect().center())
        dialog.move(center.x() - dialog.width() // 2, center.y() - dialog.height() // 2)

    def closeEvent(self, event) -> None:
        self._save_settings()
        super().closeEvent(event)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        # Debounced save — QTimer with 500ms delay
        if not hasattr(self, '_resize_timer'):
            self._resize_timer = QTimer(self)
            self._resize_timer.setSingleShot(True)
            self._resize_timer.setInterval(500)
            self._resize_timer.timeout.connect(self._save_settings)
        self._resize_timer.start()

    def moveEvent(self, event) -> None:
        super().moveEvent(event)
        if not hasattr(self, '_move_timer'):
            self._move_timer = QTimer(self)
            self._move_timer.setSingleShot(True)
            self._move_timer.setInterval(500)
            self._move_timer.timeout.connect(self._save_settings)
        self._move_timer.start()

    def _append_log(self, message: str) -> None:
        if not self.log_group.isVisible():
            self.log_group.setVisible(True)
        self.log_output.append(message)
