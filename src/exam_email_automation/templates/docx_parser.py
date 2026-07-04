"""Parse Word (.docx) email templates and extract {{variables}}.

Provides:
- Variable extraction from .docx files
- DOCX-to-HTML conversion preserving basic formatting
- Variable classification (simple vs. special/reserved)
- Column name normalization utility
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# Variables that are generated programmatically, not expected as Excel columns
SPECIAL_VARIABLES: set[str] = {
    "module_table",
    "current_date",
}

# Pattern to match {{variable_name}} in template text
VARIABLE_PATTERN = re.compile(r"\{\{(\w+)\}\}")


def normalize_variable_name(name: str) -> str:
    """Normalize a column name to match template variable conventions.

    Rules: lowercase, strip whitespace, replace spaces with underscores.
    This ensures Excel column 'First Name' matches template {{first_name}}.
    """
    return str(name).strip().lower().replace(" ", "_")


@dataclass
class TemplateInfo:
    """Result of parsing a .docx template file.

    Attributes:
        html_content: The document converted to HTML with {{variables}} preserved.
        simple_variables: Variable names that map to Excel columns.
        special_variables: Variable names that are programmatically generated.
        all_variables: All variable names found (simple + special).
    """

    html_content: str
    simple_variables: list[str] = field(default_factory=list)
    special_variables: list[str] = field(default_factory=list)

    @property
    def all_variables(self) -> list[str]:
        return self.simple_variables + self.special_variables


def _extract_variables_from_text(text: str) -> list[str]:
    """Return all unique {{variable}} names found in text."""
    return list(dict.fromkeys(VARIABLE_PATTERN.findall(text)))


def _classify_variables(variable_names: list[str]) -> tuple[list[str], list[str]]:
    """Split variable names into (simple, special) lists.

    Simple variables map to Excel columns.
    Special variables are generated programmatically (e.g., module_table).
    """
    simple = []
    special = []
    for name in variable_names:
        if name in SPECIAL_VARIABLES:
            special.append(name)
        else:
            simple.append(name)
    return simple, special


def _run_to_html(run) -> str:
    """Convert a single python-docx Run to inline HTML.

    Preserves bold (<strong>) and italic (<em>) formatting.
    """
    text = run.text
    if not text:
        return ""

    if run.bold and run.italic:
        return f"<strong><em>{text}</em></strong>"
    elif run.bold:
        return f"<strong>{text}</strong>"
    elif run.italic:
        return f"<em>{text}</em>"
    return text


def parse_and_convert(docx_path: Path) -> TemplateInfo:
    """Parse a .docx file, extract variables, and convert content to HTML.

    Args:
        docx_path: Path to the .docx template file.

    Returns:
        TemplateInfo with html_content, simple_variables, and special_variables.

    Paragraphs become <p> tags. Tables become <table> with <tr>/<td>.
    Bold runs wrap in <strong>, italic runs wrap in <em>.
    {{variables}} are preserved as literal text for Jinja2 rendering.
    """
    # Lazy import so the module can be imported without python-docx installed
    from docx import Document

    doc = Document(str(docx_path))
    all_vars: list[str] = []
    html_parts: list[str] = []

    for element in doc.element.body:
        tag = element.tag.split("}")[-1] if "}" in element.tag else element.tag

        if tag == "p":
            para = _find_paragraph(doc, element)
            if para is not None:
                para_html, para_vars = _paragraph_to_html(para)
                if para_html.strip():
                    html_parts.append(para_html)
                    all_vars.extend(para_vars)

        elif tag == "tbl":
            table = _find_table(doc, element)
            if table is not None:
                table_html, table_vars = _table_to_html(table)
                if table_html.strip():
                    html_parts.append(table_html)
                    all_vars.extend(table_vars)

    if not html_parts:
        html_parts.append("<p></p>")

    simple, special = _classify_variables(list(dict.fromkeys(all_vars)))
    return TemplateInfo(
        html_content="\n".join(html_parts),
        simple_variables=simple,
        special_variables=special,
    )


def _find_paragraph(doc, element):
    """Find the Paragraph object matching an XML element."""
    for para in doc.paragraphs:
        if para._element is element:
            return para
    return None


def _find_table(doc, element):
    """Find the Table object matching an XML element."""
    for table in doc.tables:
        if table._element is element:
            return table
    return None


def _paragraph_to_html(para) -> tuple[str, list[str]]:
    """Convert a Paragraph to HTML <p> tag with inline formatting.

    Returns:
        (html_string, list_of_variables_found)
    """
    vars_found: list[str] = []
    run_parts: list[str] = []

    for run in para.runs:
        run_text = run.text
        if run_text:
            vars_found.extend(_extract_variables_from_text(run_text))
            run_parts.append(_run_to_html(run))

    if not run_parts:
        return ("", [])

    html = "<p>" + "".join(run_parts) + "</p>"
    return (html, vars_found)


def _table_to_html(table) -> tuple[str, list[str]]:
    """Convert a Table to an HTML <table> with <tr> and <td>.

    Returns:
        (html_string, list_of_variables_found)
    """
    vars_found: list[str] = []
    rows_html: list[str] = []

    for row in table.rows:
        cells_html: list[str] = []
        for cell in row.cells:
            cell_text_parts: list[str] = []
            for para in cell.paragraphs:
                for run in para.runs:
                    run_text = run.text
                    if run_text:
                        vars_found.extend(_extract_variables_from_text(run_text))
                        cell_text_parts.append(_run_to_html(run))
            cells_html.append("<td>" + "".join(cell_text_parts) + "</td>")
        rows_html.append("<tr>" + "".join(cells_html) + "</tr>")

    if not rows_html:
        return ("", [])

    html = '<table border="1" cellpadding="6">' + "".join(rows_html) + "</table>"
    return (html, vars_found)


def extract_variables(docx_path: Path) -> TemplateInfo:
    """Extract variables from a .docx file without full HTML conversion.

    Faster than parse_and_convert; used when only variable names are needed.

    Args:
        docx_path: Path to the .docx template file.

    Returns:
        TemplateInfo with empty html_content and extracted variable lists.
    """
    from docx import Document

    doc = Document(str(docx_path))
    all_vars: list[str] = []

    for para in doc.paragraphs:
        all_vars.extend(_extract_variables_from_text(para.text))

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    all_vars.extend(_extract_variables_from_text(para.text))

    simple, special = _classify_variables(list(dict.fromkeys(all_vars)))
    return TemplateInfo(
        html_content="",
        simple_variables=simple,
        special_variables=special,
    )
