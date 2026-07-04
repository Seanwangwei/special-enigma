from pathlib import Path
from typing import Iterable, Optional
from datetime import datetime
from exam_email_automation.config.config_loader import Config
from exam_email_automation.email.email_builder import EmailBuilder, EmailMessage
from exam_email_automation.email.email_sender import OutlookEmailSender
from exam_email_automation.logging.logger import AuditLogger, configure_logging
from exam_email_automation.models.student import Student
from exam_email_automation.validation.validator import Validator


class SendService:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.email_sender = OutlookEmailSender(use_default_profile=config.use_default_outlook)
        self.email_builder = EmailBuilder()
        self.validator = Validator()
        self.audit_logger = AuditLogger(config.log_folder)
        self.logger = configure_logging(config.log_folder)

    def send_student(self, student: Student, html_body: str, attachments: Optional[Iterable[Path]] = None) -> dict[str, str]:
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
            self.email_sender.send_message(message.to_address, message.subject, message.html_body, message.attachments)
            record["Status"] = "Sent"
            self.logger.info("Email sent to %s (%s)", student.full_name, student.email)
        except Exception as exc:
            record["Error"] = str(exc)
            self.logger.exception("Failed to send email to %s", student.email)

        return record

    def send_all(self, students: list[Student], html_map: dict[str, str], attachments: Optional[Iterable[Path]] = None) -> list[dict[str, str]]:
        records: list[dict[str, str]] = []
        for student in students:
            html_body = html_map.get(student.student_id, "")
            record = self.send_student(student, html_body, attachments)
            records.append(record)

        self.audit_logger.save(records)
        return records
