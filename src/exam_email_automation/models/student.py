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

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.surname}".strip()

    def to_context(self) -> dict[str, Any]:
        return {
            "first_name": self.first_name,
            "surname": self.surname,
            "student_id": self.student_id,
            "stage_average": self.stage_average,
            "pass_credits": self.pass_credits,
            "failed_modules": self.failed_modules,
        }
