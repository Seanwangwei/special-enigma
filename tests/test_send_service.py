from pathlib import Path
from exam_email_automation.config.config_loader import Config
from exam_email_automation.email.email_builder import EmailBuilder
from exam_email_automation.models.module_result import ModuleResult
from exam_email_automation.models.student import Student
from exam_email_automation.services.send_service import SendService


def make_config(tmp_path: Path) -> Config:
    return Config(
        preview_folder=tmp_path / "preview",
        log_folder=tmp_path / "logs",
        attachment_folder=tmp_path / "attachments",
        templates_folder=tmp_path / "templates",
        use_default_outlook=True,
    )


def test_send_student_with_invalid_email(tmp_path: Path) -> None:
    config = make_config(tmp_path)
    service = SendService(config)
    student = Student(
        student_id="1001",
        first_name="Fiona",
        surname="Green",
        email="invalid-email",
        template_name="Template 1",
        stage_average="65",
        pass_credits="45",
        failed_modules="1",
        modules=[],
    )
    record = service.send_student(student, "<p>Test</p>")

    assert record["Status"] == "Failed"
    assert "Invalid email" in record["Error"]


def test_send_student_success(monkeypatch, tmp_path: Path) -> None:
    config = make_config(tmp_path)
    service = SendService(config)
    student = Student(
        student_id="1002",
        first_name="George",
        surname="Hall",
        email="george@example.com",
        template_name="Template 1",
        stage_average="76",
        pass_credits="60",
        failed_modules="0",
        modules=[],
    )

    def fake_send_message(to_address, subject, html_body, attachments):
        assert to_address == student.email
        assert "Exam Results" in subject

    monkeypatch.setattr(service.email_sender, "send_message", fake_send_message)
    record = service.send_student(student, "<p>Test</p>")

    assert record["Status"] == "Sent"
    assert record["Error"] == ""
