from exam_email_automation.email.email_builder import EmailBuilder
from exam_email_automation.models.module_result import ModuleResult
from exam_email_automation.models.student import Student


def test_compose_subject_for_known_template() -> None:
    student = Student(
        student_id="1001",
        first_name="Dana",
        surname="Lee",
        email="dana@example.com",
        template_name="Template 1",
        stage_average="80",
        pass_credits="60",
        failed_modules="0",
        modules=[
            ModuleResult("COMP301", "Software Engineering", "Exam", "1", "15")
        ],
    )
    builder = EmailBuilder()
    message = builder.compose(student, "<p>Test</p>")

    assert message.subject == "Exam Results and Progression"
    assert message.to_address == "dana@example.com"
    assert "Test" in message.html_body


def test_compose_subject_falls_back() -> None:
    student = Student(
        student_id="1002",
        first_name="Eve",
        surname="Taylor",
        email="eve@example.com",
        template_name="Unknown Template",
        stage_average="48",
        pass_credits="45",
        failed_modules="2",
        modules=[],
    )
    builder = EmailBuilder()
    message = builder.compose(student, "<p>Test</p>")

    assert message.subject == "Exam Results Notification"
    assert message.attachments == []
