from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable
import pandas as pd

from exam_email_automation.models.module_result import ModuleResult
from exam_email_automation.models.student import Student
from exam_email_automation.templates.docx_parser import normalize_variable_name
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

    def load_students(self, path: Path, template_variables: list[str] | None = None) -> list[Student]:
        path = Path(path)
        self.validator.validate_file_exists(path)

        dataframe = pd.read_excel(path, engine="openpyxl")

        # When template variables are provided, validate against them instead of
        # the hardcoded REQUIRED_COLUMNS list.  This lets the Excel have any
        # columns matching the user's own .docx template.
        missing_columns = self.validator.validate_columns(
            dataframe.columns,
            template_variables=template_variables,
        )
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        normalized = self._normalize_columns(dataframe.columns)
        dataframe = dataframe.rename(columns=normalized)

        # Determine the grouping column — prefer "student id" after normalisation,
        # but fall back to any column whose normalised name ends with "student_id".
        group_col = "student id"
        if group_col not in dataframe.columns and template_variables:
            for var in template_variables:
                from exam_email_automation.templates.docx_parser import normalize_variable_name
                if normalize_variable_name(var) in ("student_id", "studentid"):
                    # Find the matching column in the dataframe
                    for col in dataframe.columns:
                        if normalize_variable_name(str(col)) == normalize_variable_name(var):
                            group_col = col
                            break
                    break

        if group_col not in dataframe.columns:
            raise ValueError(
                f"Cannot group students — no 'student id' column found. "
                f"Available columns: {', '.join(str(c) for c in dataframe.columns)}"
            )

        students: list[Student] = []
        grouped = dataframe.groupby(group_col, sort=False)

        for student_id, group in grouped:
            student = self._build_student(student_id, group)
            students.append(student)

        return students

    def _normalize_columns(self, columns: Iterable[str]) -> dict[str, str]:
        return {str(column): str(column).strip().lower() for column in columns}

    KNOWN_COLUMNS = {
        "student id", "first name", "surname", "email",
        "email template", "stage average", "pass credits",
        "number of failed modules",
    }

    def _build_student(self, student_id: str, rows: pd.DataFrame) -> Student:
        first_row = rows.iloc[0]
        # Capture columns beyond the known set as extra_fields.
        # Collect values from ALL rows (not just first_row) so that
        # module-level columns like "Module Name" aggregate across
        # multiple rows for the same student (BUG-007).
        extra_fields: dict[str, str] = {}
        for col in rows.columns:
            norm_col = str(col).strip().lower()
            if norm_col not in self.KNOWN_COLUMNS:
                key = normalize_variable_name(str(col))
                values: list[str] = []
                seen: set[str] = set()
                for _, row in rows.iterrows():
                    val = _safe_str(row.get(col, ""))
                    if val and val not in seen:
                        values.append(val)
                        seen.add(val)
                if key and values:
                    extra_fields[key] = ", ".join(values)

        student = Student(
            student_id=_safe_str(student_id),
            first_name=_safe_str(first_row.get("first name", "")),
            surname=_safe_str(first_row.get("surname", "")),
            email=_safe_str(first_row.get("email", "")),
            template_name=_safe_str(first_row.get("email template", "")),
            stage_average=_safe_str(first_row.get("stage average", "")),
            pass_credits=_safe_str(first_row.get("pass credits", "")),
            failed_modules=_safe_str(first_row.get("number of failed modules", "")),
            extra_fields=extra_fields,
        )

        # Known module-level column names (normalised)
        _MODULE_COLS = {
            "module code", "module name", "assessment format in august",
            "attempt", "pass credits",
        }

        for _, row in rows.iterrows():
            # Collect extra module-level fields (beyond the 5 known ones)
            mod_extra: dict[str, str] = {}
            for col in rows.columns:
                norm_col = str(col).strip().lower()
                if norm_col not in self.KNOWN_COLUMNS and norm_col not in _MODULE_COLS:
                    key = normalize_variable_name(str(col))
                    val = _safe_str(row.get(col, ""))
                    if key and val:
                        mod_extra[key] = val

            module = ModuleResult(
                module_code=_safe_str(row.get("module code", "")),
                module_name=_safe_str(row.get("module name", "")),
                assessment_format=_safe_str(row.get("assessment format in august", "")),
                attempt=_safe_str(row.get("attempt", "")),
                pass_credits=_safe_str(row.get("pass credits", "")),
                extra_fields=mod_extra,
            )
            student.modules.append(module)

        if not Validator.validate_email(student.email):
            self.logger.warning("Invalid email address for student %s: %s", student.student_id, student.email)

        return student
