from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class ConfirmationDialog(QDialog):
    """Dialog showing processing summary before confirmation."""

    def __init__(self, parent, summary: dict):
        """
        Args:
            parent: Parent widget
            summary: Dict with keys: total_students, pass_emails, fail_emails, ec_emails, delivery_mode, delivery_method
        """
        super().__init__(parent)
        self.summary = summary
        self.setWindowTitle("Ready to Process")
        self.setGeometry(200, 200, 500, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Ready to process")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        layout.addSpacing(10)

        # Stats section
        stats_text = self._build_stats()
        stats_label = QLabel(stats_text)
        stats_label.setFont(QFont("Courier", 11))
        layout.addWidget(stats_label)

        # Delivery info
        delivery_text = self._build_delivery_info()
        delivery_label = QLabel(delivery_text)
        delivery_font = QFont()
        delivery_font.setBold(True)
        delivery_label.setFont(delivery_font)
        layout.addWidget(delivery_label)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.reject)
        continue_btn = QPushButton("Continue")
        continue_btn.clicked.connect(self.accept)

        button_layout.addStretch()
        button_layout.addWidget(back_btn)
        button_layout.addWidget(continue_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _build_stats(self) -> str:
        """Build statistics display."""
        lines = []
        lines.append("━" * 40)
        lines.append("")
        lines.append(f"Students: {self.summary.get('total_students', 0)}")
        lines.append("")
        lines.append(f"PASS emails:    {self.summary.get('pass_emails', 0)}")
        lines.append(f"FAIL emails:    {self.summary.get('fail_emails', 0)}")
        lines.append(f"EC emails:      {self.summary.get('ec_emails', 0)}")
        lines.append("")
        lines.append("━" * 40)
        return "\n".join(lines)

    def _build_delivery_info(self) -> str:
        """Build delivery method and mode display."""
        lines = []
        lines.append("")
        lines.append("Delivery:")
        method = self.summary.get('delivery_method', 'outlook')
        mode = self.summary.get('delivery_mode', 'create_drafts')
        
        if mode == 'preview_only':
            lines.append("● Preview Only")
        elif mode == 'create_drafts':
            lines.append("● Create Outlook Drafts")
        elif mode == 'send_immediately':
            lines.append(f"● Send Immediately (via {method.upper()})")
        
        return "\n".join(lines)
