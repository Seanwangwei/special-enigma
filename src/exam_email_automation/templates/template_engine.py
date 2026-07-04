from pathlib import Path
from typing import Any
from jinja2 import Environment, FileSystemLoader, select_autoescape
from exam_email_automation.models.student import Student


class TemplateEngine:
    def __init__(self, template_folder: Path) -> None:
        self.template_folder = Path(template_folder)
        self.environment = Environment(
            loader=FileSystemLoader(str(self.template_folder)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render(self, student: Student) -> str:
        template_name = self._resolve_template_name(student.template_name)
        template = self.environment.get_template(template_name)
        return template.render(**student.to_context(), module_table=self.generate_module_table(student))

    def _resolve_template_name(self, template_name: str) -> str:
        name = template_name.strip()
        normalized = name.lower().strip()
        mapping = {
            "template 1": "template1.html",
            "template 2": "template2.html",
            "template 3": "template3.html",
        }
        if normalized in mapping:
            return mapping[normalized]

        if not name.lower().endswith(".html"):
            name = f"{name}.html"
        return name

    @staticmethod
    def generate_module_table(student: Student) -> str:
        if not student.modules:
            return "<p>No module results available.</p>"

        rows = [
            "<tr><th>Module Code</th><th>Module Name</th><th>Assessment</th><th>Attempt</th></tr>"
        ]
        for module in student.modules:
            rows.append(
                "<tr>"
                f"<td>{module.module_code}</td>"
                f"<td>{module.module_name}</td>"
                f"<td>{module.assessment_format}</td>"
                f"<td>{module.attempt}</td>"
                "</tr>"
            )
        return f"<table border=1 cellpadding=6>{''.join(rows)}</table>"
