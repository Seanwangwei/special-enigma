from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional
from exam_email_automation.models.student import Student


@dataclass(frozen=True)
class EmailMessage:
    to_address: str
    subject: str
    html_body: str
    attachments: list[Path] = field(default_factory=list)


class EmailBuilder:
    SUBJECT_MAP = {
        "template 1": "Exam Results and Progression",
        "template 2": "Reassessment Examination Instructions",
        "template 3": "Exceptional Circumstances Outcome",
    }

    def __init__(self, override_subject: str | None = None) -> None:
        """Initialize EmailBuilder.

        Args:
            override_subject: If set, this subject is used for all emails
                              regardless of the student's template_name.
                              Used when a user-uploaded DOCX template is active.
        """
        self.override_subject = override_subject

    def compose(self, student: Student, html_body: str, attachments: Optional[Iterable[Path]] = None) -> EmailMessage:
        if self.override_subject:
            subject = self.override_subject
        else:
            subject = self.SUBJECT_MAP.get(student.template_name.strip().lower(), "Exam Results Notification")
        return EmailMessage(
            to_address=student.email,
            subject=subject,
            html_body=html_body,
            attachments=list(attachments or []),
        )
