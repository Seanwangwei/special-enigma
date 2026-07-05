"""Application window icon — loads from file if available, falls back to programmatic generation."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QColor, QPen
from PySide6.QtCore import Qt, QRect


def _find_icon_file(filename: str) -> Path | None:
    """Search for an icon file in known locations (source tree and PyInstaller bundle)."""
    # PyInstaller _MEIPASS bundle directory
    if hasattr(sys, "_MEIPASS"):
        candidate = Path(sys._MEIPASS) / "resources" / filename
        if candidate.exists():
            return candidate

    # Source tree: resources/ directory relative to this file
    candidate = Path(__file__).resolve().parent.parent.parent.parent / "resources" / filename
    if candidate.exists():
        return candidate

    # Fallback: cwd/resources/
    candidate = Path.cwd() / "resources" / filename
    if candidate.exists():
        return candidate

    return None


def create_app_icon() -> QIcon:
    """Return the application icon, preferring a file asset over programmatic generation."""
    # Try loading from file first (higher quality in packaged builds)
    png_path = _find_icon_file("icon.png")
    if png_path is not None:
        return QIcon(str(png_path))

    # Fallback: generate programmatically (no external assets needed)
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Blue rounded rectangle (envelope body)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor("#2563eb"))
    painter.drawRoundedRect(QRect(4, 14, 56, 38), 6, 6)

    # Envelope flap (triangle)
    painter.setBrush(QColor("#1d4ed8"))
    path = QPainterPath()
    path.moveTo(4, 14)
    path.lineTo(32, 38)
    path.lineTo(60, 14)
    path.closeSubpath()
    painter.fillPath(path, QColor("#3b82f6"))

    # White checkmark overlay
    painter.setPen(QPen(QColor("#ffffff"), 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    painter.drawLine(18, 34, 28, 44)
    painter.drawLine(28, 44, 46, 26)

    painter.end()

    return QIcon(pixmap)
