import sys
from pathlib import Path

root_path = Path(__file__).resolve().parent
sys.path.insert(0, str(root_path / "src"))

from PySide6.QtWidgets import QApplication
from exam_email_automation.config.config_loader import ConfigLoader
from exam_email_automation.gui.main_window import MainWindow


def _resolve_templates_folder(config) -> None:
    """Fallback: if the configured templates folder does not exist,
    resolve from the source package directory."""
    templates_path = getattr(config, "templates_folder", None)
    if templates_path is not None and templates_path.is_dir():
        return
    # Try the bundled location under the source package
    fallback = root_path / "src" / "exam_email_automation" / "templates"
    if fallback.is_dir():
        object.__setattr__(config, "_templates_folder_original", templates_path)
        object.__setattr__(config, "templates_folder", fallback)


def main() -> None:
    app = QApplication([])
    config = ConfigLoader().load()
    _resolve_templates_folder(config)
    window = MainWindow(config)
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
