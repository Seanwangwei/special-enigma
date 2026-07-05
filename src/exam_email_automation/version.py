"""Version information helpers."""

from __future__ import annotations

from exam_email_automation import __version__


def get_version_string() -> str:
    """Return the version string for display (e.g. 'v1.0.0')."""
    return f"v{__version__}"


def get_full_app_name() -> str:
    """Return the full application name with version (e.g. 'Exam Email Automation v1.0.0')."""
    return f"Exam Email Automation v{__version__}"
