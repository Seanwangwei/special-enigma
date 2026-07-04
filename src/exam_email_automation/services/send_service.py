from pathlib import Path
from typing import Iterable, Optional
from datetime import datetime
from exam_email_automation.config.config_loader import Config
from exam_email_automation.email.delivery_mode import DeliveryMode
from exam_email_automation.email.email_builder import EmailBuilder, EmailMessage
from exam_email_automation.email.email_sender import OutlookEmailSender
from exam_email_automation.email.smtp_sender import SMTPConfig, SMTPEmailSender
from exam_email_automation.logging.logger import AuditLogger, configure_logging
from exam_email_automation.models.student import Student
from exam_email_automation.validation.validator import Validator


MODE_MAP = {
    "preview_only": DeliveryMode.PREVIEW_ONLY,
    "create_drafts": DeliveryMode.CREATE_DRAFTS,
    "send_immediately": DeliveryMode.SEND_IMMEDIATELY,
}


class SendService:
    """Service for sending or drafting emails based on delivery mode.

    Supports three modes:
    - PREVIEW_ONLY: Generate and save HTML preview only.
    - CREATE_DRAFTS: Create Outlook draft emails (default; Windows only).
    - SEND_IMMEDIATELY: Send emails immediately via the configured provider.

    Supports two providers:
    - Outlook (default): Uses pywin32 COM integration.
    - SMTP: Uses smtplib for cross-platform delivery.
    """

    def __init__(self, config: Config, delivery_mode: Optional[DeliveryMode] = None, mailbox_email: Optional[str] = None) -> None:
        """Initialize SendService.

        Args:
            config: Application configuration.
            delivery_mode: How to handle email delivery (preview, draft, send).
                           If None, resolved from config.delivery_mode.
            mailbox_email: Optional Outlook shared mailbox email address.
        """
        self.config = config
        if delivery_mode is None:
            delivery_mode = MODE_MAP.get(config.delivery_mode, DeliveryMode.CREATE_DRAFTS)
        self.delivery_mode = delivery_mode
        self.mailbox_email = mailbox_email or config.outlook_mailbox_email
        self.email_builder = EmailBuilder()
        self.validator = Validator()
        self.audit_logger = AuditLogger(config.log_folder)
        self.logger = configure_logging(config.log_folder)

        # Select provider based on config
        if config.email_provider == "smtp" and config.smtp_enabled:
            smtp_cfg = SMTPConfig(
                host=config.smtp_host,
                port=config.smtp_port,
                username=config.smtp_username,
                password=config.smtp_password,
                use_ssl=config.smtp_use_ssl,
                use_tls=config.smtp_use_tls,
            )
            self.email_sender = SMTPEmailSender(smtp_cfg)
            self._is_smtp = True
        else:
            self.email_sender = OutlookEmailSender(
                use_default_profile=config.use_default_outlook,
                mailbox_email=self.mailbox_email,
            )
            self._is_smtp = False

    def send_student(self, student: Student, html_body: str, attachments: Optional[Iterable[Path]] = None) -> dict[str, str]:
        """Process a single student email based on delivery mode.

        Args:
            student: Student model containing email and template info.
            html_body: Rendered HTML email body.
            attachments: Optional file paths to attach.

        Returns:
            Record dict with Time, Student ID, Email, Template, Status, Error.
        """
        record = {
            "Time": datetime.now().isoformat(timespec="seconds"),
            "Student ID": student.student_id,
            "Email": student.email,
            "Template": student.template_name,
            "Status": "Failed",
            "Error": "",
        }

        if not self.validator.validate_email(student.email):
            record["Error"] = "Invalid email address"
            self.logger.error("Invalid email for %s: %s", student.student_id, student.email)
            return record

        message = self.email_builder.compose(student, html_body, attachments)

        try:
            if self.delivery_mode == DeliveryMode.PREVIEW_ONLY:
                record["Status"] = "Preview Generated"
                self.logger.info("Preview generated for %s (%s)", student.full_name, student.email)
            elif self._is_smtp:
                # SMTP path: send_message takes an EmailMessage object.
                # SMTP does not support draft mode; treat CREATE_DRAFTS as send.
                self.email_sender.send_message(message)
                if self.delivery_mode == DeliveryMode.CREATE_DRAFTS:
                    record["Status"] = "Sent (SMTP)"
                else:
                    record["Status"] = "Sent"
                self.logger.info("Email sent via SMTP to %s (%s)", student.full_name, student.email)
            elif self.delivery_mode == DeliveryMode.CREATE_DRAFTS:
                self.email_sender.create_draft(
                    message.to_address, message.subject, message.html_body, message.attachments
                )
                record["Status"] = "Draft Created"
                self.logger.info("Outlook draft created for %s (%s)", student.full_name, student.email)
            elif self.delivery_mode == DeliveryMode.SEND_IMMEDIATELY:
                self.email_sender.send_message(
                    message.to_address, message.subject, message.html_body, message.attachments
                )
                record["Status"] = "Sent"
                self.logger.info("Email sent to %s (%s)", student.full_name, student.email)
        except Exception as exc:
            record["Error"] = str(exc)
            self.logger.exception("Failed to process email for %s", student.email)

        return record

    def send_all(self, students: list[Student], html_map: dict[str, str], attachments: Optional[Iterable[Path]] = None) -> list[dict[str, str]]:
        """Process all students' emails based on delivery mode.

        Args:
            students: List of Student models.
            html_map: Dict mapping student ID to rendered HTML body.
            attachments: Optional file paths to attach to all emails.

        Returns:
            List of record dicts; also saved to audit log.
        """
        records: list[dict[str, str]] = []
        for student in students:
            html_body = html_map.get(student.student_id, "")
            record = self.send_student(student, html_body, attachments)
            records.append(record)

        self.audit_logger.save(records)
        return records
