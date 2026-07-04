from pathlib import Path
from exam_email_automation.logging.logger import AuditLogger
import pandas as pd


def test_audit_logger_saves_excel(tmp_path: Path) -> None:
    audit_logger = AuditLogger(tmp_path)
    records = [
        {
            "Time": "2026-07-03T12:00:00",
            "Student ID": "1001",
            "Email": "alice@example.com",
            "Template": "Template 1",
            "Status": "Sent",
            "Error": "",
        }
    ]
    path = audit_logger.save(records)

    assert path.exists()
    assert "send_log" in path.name and path.name.endswith(".xlsx")

    df = pd.read_excel(path, engine="openpyxl")
    assert str(df.loc[0, "Student ID"]) == "1001"
    assert df.loc[0, "Status"] == "Sent"
