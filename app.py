import os
import subprocess
import sys
from pathlib import Path

import PySide6

root_path = Path(__file__).resolve().parent
sys.path.insert(0, str(root_path / "src"))

# ---------------------------------------------------------------------------
# macOS: after a pkill / force-quit the cocoa plugin dylib can become
# unloadable due to kernel code-signing cache invalidation.  The only
# reliable fix is a quick reinstall (wheel is already cached → ~2 s).
# We detect the problem and fix it automatically so the user never
# sees the error.
# ---------------------------------------------------------------------------
if sys.platform == "darwin":
    _plugins = Path(PySide6.__file__).parent / "Qt" / "plugins" / "platforms"
    _cocoa = _plugins / "libqcocoa.dylib"
    if _cocoa.exists():
        try:
            import ctypes
            ctypes.CDLL(str(_cocoa.resolve()))
        except OSError:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--force-reinstall",
                 "PySide6_Essentials", "--quiet", "--no-deps"],
                check=False,
            )
    os.environ.setdefault("QT_QPA_PLATFORM_PLUGIN_PATH", str(_plugins))

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

    # Apply the design system theme (styles.qss) before creating any windows
    from exam_email_automation.gui.theme import apply_theme
    apply_theme(app)

    # QSettings identity (enables window geometry persistence)
    app.setOrganizationName("ExamEmailAutomation")
    app.setApplicationName("Exam Email Automation")

    # Set application window icon
    from exam_email_automation.gui.icon import create_app_icon
    app.setWindowIcon(create_app_icon())

    config = ConfigLoader().load()
    _resolve_templates_folder(config)
    window = MainWindow(config)
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
