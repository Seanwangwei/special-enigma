from pathlib import Path
from exam_email_automation.validation.validator import Validator


def test_validate_email() -> None:
    assert Validator.validate_email("student@example.com")
    assert not Validator.validate_email("invalid-email")
    assert not Validator.validate_email("")


def test_validate_columns() -> None:
    headers = [
        "Student ID",
        "First Name",
        "Surname",
        "Email",
        "Module Code",
        "Module Name",
        "Assessment Format in August",
        "Attempt",
        "Pass Credits",
        "Stage Average",
        "Email Template",
        "Number of Failed Modules",
    ]
    missing = Validator.validate_columns(headers)
    assert missing == []

    incomplete = ["Student ID", "Email"]
    missing = Validator.validate_columns(incomplete)
    assert "surname" in missing
    assert "module code" in missing


def test_validate_file_exists(tmp_path: Path) -> None:
    path = tmp_path / "missing.xlsx"
    try:
        Validator.validate_file_exists(path)
    except FileNotFoundError as exc:
        assert "File not found" in str(exc)
