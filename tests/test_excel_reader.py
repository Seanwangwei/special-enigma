from pathlib import Path
import pandas as pd
from exam_email_automation.excel.excel_reader import ExcelReader


def test_load_students_groups_by_student_id(tmp_path: Path) -> None:
    data = [
        {
            "Student ID": "1001",
            "First Name": "Alice",
            "Surname": "Smith",
            "Email": "alice@example.com",
            "Module Code": "COMP101",
            "Module Name": "Programming",
            "Assessment Format in August": "Exam",
            "Attempt": "1",
            "Pass Credits": 15,
            "Stage Average": 68,
            "Email Template": "Template 1",
            "Number of Failed Modules": 0,
        },
        {
            "Student ID": "1001",
            "First Name": "Alice",
            "Surname": "Smith",
            "Email": "alice@example.com",
            "Module Code": "COMP102",
            "Module Name": "Data Structures",
            "Assessment Format in August": "Exam",
            "Attempt": "1",
            "Pass Credits": 15,
            "Stage Average": 68,
            "Email Template": "Template 1",
            "Number of Failed Modules": 0,
        },
        {
            "Student ID": "1002",
            "First Name": "Bob",
            "Surname": "Jones",
            "Email": "bob@example.com",
            "Module Code": "COMP103",
            "Module Name": "Databases",
            "Assessment Format in August": "Project",
            "Attempt": "2",
            "Pass Credits": 10,
            "Stage Average": 55,
            "Email Template": "Template 2",
            "Number of Failed Modules": 1,
        },
    ]
    path = tmp_path / "students.xlsx"
    pd.DataFrame(data).to_excel(path, index=False)

    reader = ExcelReader()
    students = reader.load_students(path)

    assert len(students) == 2
    alice = next(student for student in students if student.student_id == "1001")
    assert len(alice.modules) == 2
    assert alice.email == "alice@example.com"
    bob = next(student for student in students if student.student_id == "1002")
    assert bob.template_name == "Template 2"


def test_nan_values_produce_empty_strings(tmp_path: Path) -> None:
    """Cells with NaN values should produce empty strings, not literal 'nan'."""
    import math
    data = [
        {
            "Student ID": "2001",
            "First Name": float("nan"),
            "Surname": "Doe",
            "Email": "john@example.com",
            "Module Code": "COMP201",
            "Module Name": float("nan"),
            "Assessment Format in August": "Exam",
            "Attempt": 1,
            "Pass Credits": float("nan"),
            "Stage Average": 72,
            "Email Template": "Template 1",
            "Number of Failed Modules": 0,
        },
    ]
    path = tmp_path / "nan_students.xlsx"
    pd.DataFrame(data).to_excel(path, index=False)

    reader = ExcelReader()
    students = reader.load_students(path)

    assert len(students) == 1
    student = students[0]
    assert student.first_name == "", f"Expected empty string, got '{student.first_name}'"
    assert student.pass_credits == "", f"Expected empty string, got '{student.pass_credits}'"
