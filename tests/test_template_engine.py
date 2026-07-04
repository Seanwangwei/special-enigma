from pathlib import Path
from exam_email_automation.models.module_result import ModuleResult
from exam_email_automation.models.student import Student
from exam_email_automation.templates.template_engine import TemplateEngine


def test_render_template_with_module_table(tmp_path: Path) -> None:
    template_folder = Path(__file__).resolve().parents[1] / "src" / "exam_email_automation" / "templates"
    engine = TemplateEngine(template_folder)
    student = Student(
        student_id="1001",
        first_name="Charlie",
        surname="Brown",
        email="charlie@example.com",
        template_name="Template 1",
        stage_average="72",
        pass_credits="60",
        failed_modules="0",
        modules=[
            ModuleResult(
                module_code="COMP201",
                module_name="Algorithms",
                assessment_format="Exam",
                attempt="1",
                pass_credits="15",
            )
        ],
    )
    rendered = engine.render(student)

    assert "Charlie" in rendered
    assert "Algorithms" in rendered
    assert "<table" in rendered
