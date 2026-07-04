from pathlib import Path
from exam_email_automation.config.config_loader import Config
from exam_email_automation.models.student import Student
from exam_email_automation.templates.template_engine import TemplateEngine


class PreviewService:
    def __init__(self, template_engine: TemplateEngine, config: Config) -> None:
        self.template_engine = template_engine
        self.config = config
        self.config.preview_folder.mkdir(parents=True, exist_ok=True)

    def generate_preview_html(self, student: Student) -> str:
        return self.template_engine.render(student)

    def save_preview(self, student: Student, html_body: str) -> Path:
        sanitized_name = f"{student.student_id}_{student.surname}".replace(" ", "_")
        destination = self.config.preview_folder / f"{sanitized_name}.html"
        destination.write_text(html_body, encoding="utf-8")
        return destination
