from dataclasses import dataclass, field
from typing import Any
from .module_result import ModuleResult


@dataclass
class Student:
    student_id: str
    first_name: str
    surname: str
    email: str
    template_name: str
    stage_average: str
    pass_credits: str
    failed_modules: str
    modules: list[ModuleResult] = field(default_factory=list)
    extra_fields: dict[str, str] = field(default_factory=dict)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.surname}".strip()

    def to_context(self) -> dict[str, Any]:
        context = {
            "first_name": self.first_name,
            "surname": self.surname,
            "student_id": self.student_id,
            "stage_average": self.stage_average,
            "pass_credits": self.pass_credits,
            "failed_modules": self.failed_modules,
        }
        # Merge extra fields; structured fields win on key collision
        for key, value in self.extra_fields.items():
            if key not in context:
                context[key] = value
        return context
