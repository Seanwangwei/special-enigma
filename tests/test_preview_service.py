from pathlib import Path
from exam_email_automation.config.config_loader import Config
from exam_email_automation.models.module_result import ModuleResult
from exam_email_automation.models.student import Student
from exam_email_automation.services.preview_service import PreviewService
from exam_email_automation.templates.template_engine import TemplateEngine


def test_generate_and_save_preview_html(tmp_path: Path) -> None:
    config = Config(
        preview_folder=tmp_path / "preview",
        log_folder=tmp_path / "logs",
        attachment_folder=tmp_path / "attachments",
        templates_folder=Path.cwd() / "src" / "exam_email_automation" / "templates",
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
    engine = TemplateEngine(config.templates_folder)
    preview_service = PreviewService(engine, config)

    student = Student(
        student_id="1001",
        first_name="Alice",
        surname="Smith",
        email="alice@example.com",
        template_name="Template 1",
        stage_average="70",
        pass_credits="60",
        failed_modules="0",
        modules=[
            ModuleResult(
                module_code="COMP101",
                module_name="Programming",
                assessment_format="Exam",
                attempt="1",
                pass_credits="15",
            )
        ],
    )

    html_body = preview_service.generate_preview_html(student)
    assert "Alice" in html_body
    assert "Programming" in html_body

    path = preview_service.save_preview(student, html_body)
    assert path.exists()
    assert path.suffix == ".html"
    assert "Alice" in path.read_text(encoding="utf-8")
