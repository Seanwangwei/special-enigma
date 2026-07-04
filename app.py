import sys
from pathlib import Path

root_path = Path(__file__).resolve().parent
sys.path.insert(0, str(root_path / "src"))

from PySide6.QtWidgets import QApplication
from exam_email_automation.gui.main_window import MainWindow


def main() -> None:
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
