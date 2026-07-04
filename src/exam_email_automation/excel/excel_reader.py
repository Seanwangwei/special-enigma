from __future__ import annotations

from pathlib import Path
from typing import Iterable
import pandas as pd

from exam_email_automation.models.module_result import ModuleResult
from exam_email_automation.models.student import Student
from exam_email_automation.validation.validator import Validator
from exam_email_automation.logging.logger import configure_logging


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
            student_id=str(student_id).strip(),
            first_name=str(first_row.get("first name", "")).strip(),
            surname=str(first_row.get("surname", "")).strip(),
            email=str(first_row.get("email", "")).strip(),
            template_name=str(first_row.get("email template", "")).strip(),
            stage_average=str(first_row.get("stage average", "")).strip(),
            pass_credits=str(first_row.get("pass credits", "")).strip(),
            failed_modules=str(first_row.get("number of failed modules", "")).strip(),
        )

        for _, row in rows.iterrows():
            module = ModuleResult(
                module_code=str(row.get("module code", "")).strip(),
                module_name=str(row.get("module name", "")).strip(),
                assessment_format=str(row.get("assessment format in august", "")).strip(),
                attempt=str(row.get("attempt", "")).strip(),
                pass_credits=str(row.get("pass credits", "")).strip(),
            )
            student.modules.append(module)

        if not Validator.validate_email(student.email):
            self.logger.warning("Invalid email address for student %s: %s", student.student_id, student.email)

        return student
