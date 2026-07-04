import sys
from pathlib import Path

root_path = Path(__file__).resolve().parent
sys.path.insert(0, str(root_path / "src"))

from PySide6.QtWidgets import QApplication
from exam_email_automation.config.config_loader import ConfigLoader
from exam_email_automation.gui.main_window import MainWindow


def main() -> None:
    config_path = Path(__file__).resolve().parent / "config.yaml"
    config = ConfigLoader(config_path).load()
    app = QApplication([])
    window = MainWindow(config)
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
