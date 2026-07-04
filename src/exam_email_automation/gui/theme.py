"""
Design token constants and theme utilities.

All visual design values defined in one place — maps to the design tokens
in docs/design-mockup.html. These feed into styles.qss and widget styling.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict


# ============================================================
# COLOR PALETTE
# ============================================================

class Colors:
    """Semantic color tokens. Hex values match the design mockup."""

    # Primary
    BLUE_50 = "#eff6ff"
    BLUE_100 = "#dbeafe"
    BLUE_200 = "#bfdbfe"
    BLUE_500 = "#3b82f6"
    BLUE_600 = "#2563eb"
    BLUE_700 = "#1d4ed8"

    # Success
    GREEN_50 = "#f0fdf4"
    GREEN_100 = "#dcfce7"
    GREEN_500 = "#22c55e"
    GREEN_600 = "#16a34a"
    GREEN_700 = "#15803d"

    # Warning
    AMBER_50 = "#fffbeb"
    AMBER_100 = "#fef3c7"
    AMBER_500 = "#f59e0b"
    AMBER_600 = "#d97706"

    # Error
    RED_50 = "#fef2f2"
    RED_100 = "#fee2e2"
    RED_500 = "#ef4444"
    RED_600 = "#dc2626"

    # Neutral
    SLATE_50 = "#f8fafc"
    SLATE_100 = "#f1f5f9"
    SLATE_200 = "#e2e8f0"
    SLATE_300 = "#cbd5e1"
    SLATE_400 = "#94a3b8"
    SLATE_500 = "#64748b"
    SLATE_600 = "#475569"
    SLATE_700 = "#334155"
    SLATE_800 = "#1e293b"
    SLATE_900 = "#0f172a"

    # Semantic aliases
    PRIMARY = BLUE_600
    PRIMARY_HOVER = BLUE_700
    PRIMARY_LIGHT = BLUE_50
    SUCCESS = GREEN_600
    SUCCESS_LIGHT = GREEN_50
    WARNING = AMBER_600
    WARNING_LIGHT = AMBER_50
    ERROR = RED_600
    ERROR_LIGHT = RED_50

    # Surfaces
    BG_APP = "#f1f5f9"
    BG_SURFACE = "#ffffff"
    BORDER = SLATE_200
    BORDER_FOCUS = BLUE_500

    # Text
    TEXT_PRIMARY = SLATE_800
    TEXT_SECONDARY = SLATE_500
    TEXT_TERTIARY = SLATE_400
    TEXT_INVERSE = "#ffffff"

    # Log panel
    LOG_BG = SLATE_900
    LOG_TEXT = "#e2e8f0"
    LOG_OK = "#6ee7b7"
    LOG_ERROR = "#fca5a5"
    LOG_TIMESTAMP = SLATE_500


# ============================================================
# TYPOGRAPHY
# ============================================================

class Fonts:
    """Font families and size scale."""
    SANS = "Segoe UI, -apple-system, BlinkMacSystemFont, system-ui, sans-serif"
    MONO = "Consolas, SF Mono, Cascadia Code, JetBrains Mono, Fira Code, monospace"

    SIZE_XS = "11px"
    SIZE_SM = "13px"  # QSS: 14px Qt ≈ 13px CSS feel on Windows
    SIZE_BASE = "14px"
    SIZE_LG = "16px"
    SIZE_XL = "18px"
    SIZE_2XL = "22px"


# ============================================================
# SPACING (4px grid)
# ============================================================

class Spacing:
    """Spacing scale in pixels."""
    S1 = 4
    S2 = 8
    S3 = 12
    S4 = 16
    S5 = 20
    S6 = 24
    S8 = 32


# ============================================================
# BORDER RADIUS
# ============================================================

class Radius:
    """Border radius scale in pixels."""
    SM = 4
    MD = 6
    LG = 8
    XL = 12


# ============================================================
# BADGE VARIANTS
# ============================================================

BADGE_STYLES: Dict[str, Dict[str, str]] = {
    "success": {"bg": Colors.GREEN_100, "fg": Colors.GREEN_600},
    "warning": {"bg": Colors.AMBER_100, "fg": Colors.AMBER_600},
    "error":   {"bg": Colors.RED_100,   "fg": Colors.RED_600},
    "info":    {"bg": Colors.BLUE_100,  "fg": Colors.BLUE_600},
}


# ============================================================
# THEME LOADER
# ============================================================

_STYLESHEET_CACHE: str | None = None


def load_stylesheet() -> str:
    """Load the QSS stylesheet from disk, with caching."""
    global _STYLESHEET_CACHE
    if _STYLESHEET_CACHE is not None:
        return _STYLESHEET_CACHE

    qss_path = Path(__file__).resolve().parent / "styles.qss"
    if not qss_path.exists():
        _STYLESHEET_CACHE = ""
        return ""

    raw = qss_path.read_text(encoding="utf-8")

    # Substitute color tokens so the QSS stays in sync with theme.py
    for name in dir(Colors):
        if name.startswith("_"):
            continue
        value = getattr(Colors, name)
        if isinstance(value, str) and value.startswith("#"):
            raw = raw.replace(f"${{Colors.{name}}}", value)

    _STYLESHEET_CACHE = raw
    return raw


def apply_theme(app: "QApplication") -> None:  # noqa: F821
    """Apply the full design theme to a QApplication instance."""
    qss = load_stylesheet()
    if qss:
        app.setStyleSheet(qss)

    # Set default font
    font = app.font()
    font.setFamily("Segoe UI")
    font.setPointSize(9)
    app.setFont(font)
