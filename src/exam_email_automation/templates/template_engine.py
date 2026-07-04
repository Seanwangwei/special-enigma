from pathlib import Path
from typing import Any
from jinja2 import Environment, FileSystemLoader, DictLoader, ChoiceLoader, select_autoescape
from exam_email_automation.models.student import Student


class TemplateEngine:
    # Internal key used in the DictLoader for user-uploaded templates
    UPLOADED_TEMPLATE_KEY = "_uploaded_template"

    def __init__(self, template_folder: Path) -> None:
        self.template_folder = Path(template_folder)
        self._dict_templates: dict[str, str] = {}
        self.environment = Environment(
            loader=ChoiceLoader([
                DictLoader(self._dict_templates),
                FileSystemLoader(str(self.template_folder)),
            ]),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def load_docx_template(self, html_content: str) -> None:
        """Register a DOCX-converted HTML template for rendering.

        Once loaded, all renders use this template regardless of
        the student's template_name column.
        """
        self._dict_templates[self.UPLOADED_TEMPLATE_KEY] = html_content

    def has_uploaded_template(self) -> bool:
        """Return True if a user-uploaded DOCX template is active."""
        return self.UPLOADED_TEMPLATE_KEY in self._dict_templates

    def unload_uploaded_template(self) -> None:
        """Remove the uploaded template, reverting to bundled HTML templates."""
        self._dict_templates.pop(self.UPLOADED_TEMPLATE_KEY, None)

    def render(self, student: Student) -> str:
        # When a DOCX template is loaded, always use it
        if self.has_uploaded_template():
            template_name = self.UPLOADED_TEMPLATE_KEY
        else:
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
