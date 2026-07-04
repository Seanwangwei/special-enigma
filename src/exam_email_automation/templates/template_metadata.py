"""Template metadata — subject lines, companion YAML, TemplateMeta dataclass."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class TemplateMeta:
    """Metadata for a user-uploaded email template.

    Attributes:
        template_name: Display name (e.g., filename).
        subject: Email subject line.
        source_type: 'docx' or 'html'.
        variables: All variable names from the template.
        special_variables: Variables that are programmatically generated.
        html_content: The template content as HTML (with {{variables}} preserved).
    """

    template_name: str
    subject: str
    source_type: str  # "docx" or "html"
    variables: list[str] = field(default_factory=list)
    special_variables: list[str] = field(default_factory=list)
    html_content: str = ""


def load_companion_yaml(docx_path: Path) -> Optional[dict]:
    """Look for a companion YAML file next to the .docx template.

    For 'mytemplate.docx', looks for 'mytemplate.yaml'.
    Expected YAML schema:
        subject: "Your Exam Results"

    Returns:
        Parsed dict on success, None if file missing or unparseable.
    """
    yaml_path = docx_path.with_suffix(".yaml")
    if not yaml_path.exists():
        # Also try .yml extension
        yaml_path = docx_path.with_suffix(".yml")
    if not yaml_path.exists():
        return None

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else None
    except Exception:
        return None
