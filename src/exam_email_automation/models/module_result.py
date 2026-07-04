from dataclasses import dataclass


@dataclass(frozen=True)
class ModuleResult:
    module_code: str
    module_name: str
    assessment_format: str
    attempt: str
    pass_credits: str
