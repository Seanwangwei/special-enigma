import re
from pathlib import Path
from typing import Iterable


class Validator:
    EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    REQUIRED_COLUMNS = [
        "student id",
        "surname",
        "first name",
        "email",
        "module code",
        "module name",
        "assessment format in august",
        "attempt",
        "pass credits",
        "stage average",
        "email template",
        "number of failed modules",
    ]

    @classmethod
    def validate_columns(cls, headers: Iterable[str]) -> list[str]:
        normalized = {str(header).strip().lower() for header in headers}
        missing = [column for column in cls.REQUIRED_COLUMNS if column not in normalized]
        return missing

    @classmethod
    def validate_email(cls, email: str) -> bool:
        return bool(email and cls.EMAIL_PATTERN.match(email.strip()))

    @staticmethod
    def validate_file_exists(path: Path) -> None:
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")

    @staticmethod
    def validate_folder_exists(path: Path) -> None:
        if not path.exists() or not path.is_dir():
            raise FileNotFoundError(f"Folder not found: {path}")
