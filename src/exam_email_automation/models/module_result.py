from __future__ import annotations

from dataclasses import dataclass, field


# Known module-level fields that map to standard Excel columns.
_MODULE_KNOWN = frozenset({
    "module_code", "module_name", "assessment_format", "attempt", "pass_credits",
})


@dataclass
class ModuleResult:
    """A single module row for a student.

    Extra columns beyond the five known ones are captured in ``extra_fields``
    and accessible via ``get(name, default)`` for use in Jinja2 table row
    templates (Sprint 7 — dynamic table population).
    """

    module_code: str = ""
    module_name: str = ""
    assessment_format: str = ""
    attempt: str = ""
    pass_credits: str = ""
    extra_fields: dict[str, str] = field(default_factory=dict)

    def get(self, field_name: str, default: str = "") -> str:
        """Look up a field by normalised name.

        Checks the five known fields first, then ``extra_fields``.
        This method is designed to be called from Jinja2 templates:

            {{ module.get('module_code', '') }}
            {{ module.get('credits', '') }}
        """
        if field_name == "module_code":
            return self.module_code
        if field_name == "module_name":
            return self.module_name
        if field_name == "assessment_format":
            return self.assessment_format
        if field_name == "attempt":
            return self.attempt
        if field_name == "pass_credits":
            return self.pass_credits
        return self.extra_fields.get(field_name, default)
