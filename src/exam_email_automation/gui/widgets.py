"""Reusable styled widgets for the Exam Email Automation GUI."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout
from PySide6.QtCore import Qt


class SectionLabel(QLabel):
    """Bold section header used between QGroupBox sections."""

    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setProperty("cssClass", "section-label")
        self.setAlignment(Qt.AlignLeft)


class BadgeLabel(QLabel):
    """Small rounded pill label for counts and status indicators.

    Variants: 'success' | 'warning' | 'error' | 'info'
    """

    VARIANTS = ("success", "warning", "error", "info")

    def __init__(
        self,
        text: str = "",
        variant: str = "info",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(text, parent)
        if variant not in self.VARIANTS:
            variant = "info"
        self.setProperty("cssClass", f"badge-{variant}")
        # Force the dynamic property to take effect
        self.style().unpolish(self)
        self.style().polish(self)

    def set_variant(self, variant: str) -> None:
        if variant not in self.VARIANTS:
            variant = "info"
        self.setProperty("cssClass", f"badge-{variant}")
        self.style().unpolish(self)
        self.style().polish(self)


class StepIndicator(QWidget):
    """Horizontal wizard step indicator with numbered circles and connectors.

    Usage:
        indicator = StepIndicator(["Method", "Mode", "Confirm"])
        indicator.set_current_step(1)  # 0-indexed
        indicator.mark_done(0)         # mark step 0 as completed
    """

    def __init__(
        self,
        steps: list[str],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._steps = steps
        self._current: int = 0
        self._done: set[int] = set()
        self._labels: list[QLabel] = []
        self._circles: list[QLabel] = []
        self._connectors: list[QWidget] = []
        self._build()

    def _build(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        for i, name in enumerate(self._steps):
            if i > 0:
                connector = QWidget()
                connector.setFixedHeight(2)
                connector.setMinimumWidth(20)
                connector.setStyleSheet("background: #e2e8f0; border: none; border-radius: 1px;")
                layout.addWidget(connector, 1)
                self._connectors.append(connector)

            circle = QLabel()
            circle.setText(str(i + 1))
            circle.setAlignment(Qt.AlignCenter)
            circle.setFixedSize(26, 26)
            circle.setStyleSheet(
                "font-size: 11px; font-weight: 700; border: 2px solid #e2e8f0; "
                "border-radius: 13px; background: #ffffff; color: #94a3b8;"
            )
            layout.addWidget(circle)
            self._circles.append(circle)

            label = QLabel(name)
            label.setStyleSheet("font-size: 11px; color: #94a3b8; font-weight: 400; border: none; background: transparent;")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
            self._labels.append(label)

    def set_current_step(self, index: int) -> None:
        """Set the active step (0-indexed)."""
        if index < 0 or index >= len(self._steps):
            return
        self._current = index
        self._refresh()

    def mark_done(self, index: int) -> None:
        """Mark a step as completed."""
        if 0 <= index < len(self._steps):
            self._done.add(index)
            self._refresh()

    def _refresh(self) -> None:
        for i in range(len(self._steps)):
            circle = self._circles[i]
            label = self._labels[i]

            if i in self._done:
                circle.setText("✓")
                circle.setStyleSheet(
                    "font-size: 12px; font-weight: 700; border: 2px solid #16a34a; "
                    "border-radius: 13px; background: #16a34a; color: #ffffff;"
                )
                label.setStyleSheet("font-size: 11px; color: #16a34a; font-weight: 600; border: none; background: transparent;")
            elif i == self._current:
                circle.setText(str(i + 1))
                circle.setStyleSheet(
                    "font-size: 11px; font-weight: 700; border: 2px solid #2563eb; "
                    "border-radius: 13px; background: #2563eb; color: #ffffff;"
                )
                label.setStyleSheet("font-size: 11px; color: #2563eb; font-weight: 600; border: none; background: transparent;")
            else:
                circle.setText(str(i + 1))
                circle.setStyleSheet(
                    "font-size: 11px; font-weight: 700; border: 2px solid #e2e8f0; "
                    "border-radius: 13px; background: #ffffff; color: #94a3b8;"
                )
                label.setStyleSheet("font-size: 11px; color: #94a3b8; font-weight: 400; border: none; background: transparent;")

        # Update connectors
        for idx, connector in enumerate(self._connectors):
            if idx + 1 in self._done:
                connector.setStyleSheet("background: #16a34a; border: none; border-radius: 1px;")
            else:
                connector.setStyleSheet("background: #e2e8f0; border: none; border-radius: 1px;")
