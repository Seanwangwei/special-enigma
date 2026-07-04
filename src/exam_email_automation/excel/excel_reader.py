from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable
import pandas as pd

from exam_email_automation.models.module_result import ModuleResult
from exam_email_automation.models.student import Student
from exam_email_automation.validation.validator import Validator
from exam_email_automation.logging.logger import configure_logging


def _safe_str(value) -> str:
    """Convert a cell value to a string, guarding against NaN values."""
    try:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return ""
    except TypeError:
        pass
    return str(value).strip()


class ExcelReader:
    def __init__(self) -> None:
        self.logger = configure_logging(Path.cwd() / "logs")
        self.validator = Validator()

    def load_students(self, path: Path) -> list[Student]:
        path = Path(path)
        self.validator.validate_file_exists(path)

        dataframe = pd.read_excel(path, engine="openpyxl")
        missing_columns = self.validator.validate_columns(dataframe.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        normalized = self._normalize_columns(dataframe.columns)
        dataframe = dataframe.rename(columns=normalized)

        students: list[Student] = []
        grouped = dataframe.groupby("student id", sort=False)

        for student_id, group in grouped:
            student = self._build_student(student_id, group)
            students.append(student)

        return students

    def _normalize_columns(self, columns: Iterable[str]) -> dict[str, str]:
        return {str(column): str(column).strip().lower() for column in columns}

    def _build_student(self, student_id: str, rows: pd.DataFrame) -> Student:
        first_row = rows.iloc[0]
        student = Student(
            student_id=_safe_str(student_id),
            first_name=_safe_str(first_row.get("first name", "")),
            surname=_safe_str(first_row.get("surname", "")),
            email=_safe_str(first_row.get("email", "")),
            template_name=_safe_str(first_row.get("email template", "")),
            stage_average=_safe_str(first_row.get("stage average", "")),
            pass_credits=_safe_str(first_row.get("pass credits", "")),
            failed_modules=_safe_str(first_row.get("number of failed modules", "")),
        )

        for _, row in rows.iterrows():
            module = ModuleResult(
                module_code=_safe_str(row.get("module code", "")),
                module_name=_safe_str(row.get("module name", "")),
                assessment_format=_safe_str(row.get("assessment format in august", "")),
                attempt=_safe_str(row.get("attempt", "")),
                pass_credits=_safe_str(row.get("pass credits", "")),
            )
            student.modules.append(module)

        if not Validator.validate_email(student.email):
            self.logger.warning("Invalid email address for student %s: %s", student.student_id, student.email)

        return student
