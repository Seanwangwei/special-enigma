from unittest.mock import patch, MagicMock
from pathlib import Path

from exam_email_automation.config.config_loader import Config
from exam_email_automation.email.delivery_mode import DeliveryMode
from exam_email_automation.models.student import Student
from exam_email_automation.services.send_service import SendService


def make_config(tmp_path: Path) -> Config:
    return Config(
        preview_folder=tmp_path / "preview",
        log_folder=tmp_path / "logs",
        attachment_folder=tmp_path / "attachments",
        templates_folder=tmp_path / "templates",
        use_default_outlook=True,
        delivery_mode="preview_only",
        email_provider="outlook",
        outlook_mailbox_email=None,
        smtp_enabled=False,
        smtp_host="smtp.example.com",
        smtp_port=587,
        smtp_username="",
        smtp_password="",
        smtp_use_tls=True,
        smtp_use_ssl=False,
    )


def make_student() -> Student:
    from exam_email_automation.models.module_result import ModuleResult
    return Student(
        student_id="001",
        first_name="John",
        surname="Doe",
        email="john@example.com",
        template_name="Template 1",
        stage_average="75",
        pass_credits="60",
        failed_modules="0",
        modules=[ModuleResult(module_code="MOD001", module_name="Math", assessment_format="Exam", attempt="1", pass_credits="10")],
    )


@patch('exam_email_automation.services.send_service.OutlookEmailSender')
def test_send_student_preview_only(mock_outlook_cls, tmp_path: Path):
    config = make_config(tmp_path)
    config.log_folder.mkdir(parents=True, exist_ok=True)

    service = SendService(config, delivery_mode=DeliveryMode.PREVIEW_ONLY)
    student = make_student()
    record = service.send_student(student, '<p>Test</p>')

    assert record['Status'] == 'Preview Generated'
    assert record['Student ID'] == '001'
    assert record['Email'] == 'john@example.com'


@patch('exam_email_automation.services.send_service.OutlookEmailSender')
def test_send_student_create_draft(mock_outlook_cls, tmp_path: Path):
    mock_outlook = MagicMock()
    mock_outlook_cls.return_value = mock_outlook
    config = make_config(tmp_path)
    config.log_folder.mkdir(parents=True, exist_ok=True)

    service = SendService(config, delivery_mode=DeliveryMode.CREATE_DRAFTS)
    student = make_student()
    record = service.send_student(student, '<p>Test</p>')

    assert record['Status'] == 'Draft Created'
    assert mock_outlook.create_draft.called


@patch('exam_email_automation.services.send_service.OutlookEmailSender')
def test_send_student_send_immediately(mock_outlook_cls, tmp_path: Path):
    mock_outlook = MagicMock()
    mock_outlook_cls.return_value = mock_outlook
    config = make_config(tmp_path)
    config.log_folder.mkdir(parents=True, exist_ok=True)

    service = SendService(config, delivery_mode=DeliveryMode.SEND_IMMEDIATELY)
    student = make_student()
    record = service.send_student(student, '<p>Test</p>')

    assert record['Status'] == 'Sent'
    assert mock_outlook.send_message.called


@patch('exam_email_automation.services.send_service.OutlookEmailSender')
def test_send_student_invalid_email(mock_outlook_cls, tmp_path: Path):
    config = make_config(tmp_path)
    config.log_folder.mkdir(parents=True, exist_ok=True)

    service = SendService(config, delivery_mode=DeliveryMode.CREATE_DRAFTS)
    student = make_student()
    student.email = "invalid-email"
    record = service.send_student(student, '<p>Test</p>')

    assert record['Status'] == 'Failed'
    assert 'Invalid email address' in record['Error']
