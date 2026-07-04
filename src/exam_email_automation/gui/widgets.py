from PySide6.QtWidgets import QLabel


class SectionLabel(QLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("font-weight: bold; font-size: 14px;")
