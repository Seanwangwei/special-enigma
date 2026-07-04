import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from exam_email_automation.templates.docx_parser import normalize_variable_name, SPECIAL_VARIABLES


@dataclass
class MismatchReport:
    """Result of validating template variables against Excel columns.

    Attributes:
        missing_in_excel: Template variables with no matching Excel column.
        unused_excel_columns: Excel columns with no matching template variable.
    """

    missing_in_excel: list[str]
    unused_excel_columns: list[str]

    @property
    def is_clean(self) -> bool:
        return len(self.missing_in_excel) == 0


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
    def validate_columns(
        cls,
        headers: Iterable[str],
        template_variables: Optional[list[str]] = None,
    ) -> list[str]:
        """Validate that required columns are present.

        When template_variables is provided, validates against those variables
        instead of the hardcoded REQUIRED_COLUMNS list. Special variables
        (e.g., module_table) are excluded from validation.

        Args:
            headers: Column headers from the Excel file.
            template_variables: Optional list of template variable names.
                                When None, falls back to REQUIRED_COLUMNS.

        Returns:
            List of missing column/variable names.
        """
        normalized = {normalize_variable_name(str(h)) for h in headers}

        if template_variables is not None:
            # Template-driven: check each template variable has a matching column
            missing = []
            for var in template_variables:
                if var in SPECIAL_VARIABLES:
                    continue  # Special variables are generated, not from Excel
                if normalize_variable_name(var) not in normalized:
                    missing.append(var)
            return missing

        # Legacy: validate against hardcoded REQUIRED_COLUMNS
        return [c for c in cls.REQUIRED_COLUMNS if normalize_variable_name(c) not in normalized]

    @classmethod
    def validate_template_against_excel(
        cls,
        template_variables: list[str],
        excel_headers: Iterable[str],
    ) -> MismatchReport:
        """Compare template variables to Excel column headers.

        Args:
            template_variables: Variable names extracted from the template.
            excel_headers: Column headers from the Excel file.

        Returns:
            MismatchReport with missing_in_excel and unused_excel_columns.
        """
        norm_headers = {normalize_variable_name(str(h)) for h in excel_headers}
        norm_vars = {normalize_variable_name(v) for v in template_variables}

        # Template variables that need Excel columns (exclude specials)
        simple_vars = {
            normalize_variable_name(v)
            for v in template_variables
            if v not in SPECIAL_VARIABLES
        }

        missing_in_excel = [v for v in template_variables
                           if v not in SPECIAL_VARIABLES
                           and normalize_variable_name(v) not in norm_headers]
        unused_excel_columns = [str(h) for h in excel_headers
                               if normalize_variable_name(str(h)) not in norm_vars]

        return MismatchReport(
            missing_in_excel=missing_in_excel,
            unused_excel_columns=unused_excel_columns,
        )

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
