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

    def compose(self, student: Student, html_body: str, attachments: Optional[Iterable[Path]] = None) -> EmailMessage:
        subject = self.SUBJECT_MAP.get(student.template_name.strip().lower(), "Exam Results Notification")
        return EmailMessage(
            to_address=student.email,
            subject=subject,
            html_body=html_body,
            attachments=list(attachments or []),
        )
