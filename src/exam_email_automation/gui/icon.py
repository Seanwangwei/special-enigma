"""Generate the application window icon programmatically (no external assets needed)."""

from __future__ import annotations

from PySide6.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QColor, QPen
from PySide6.QtCore import Qt, QRect


def create_app_icon() -> QIcon:
    """Generate a simple envelope icon for the application."""
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
