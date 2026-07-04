from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union
import yaml


@dataclass(frozen=True)
class Config:
    preview_folder: Path
    log_folder: Path
    attachment_folder: Path
    templates_folder: Path
    use_default_outlook: bool


class ConfigLoader:
    def __init__(self, config_path: Optional[Union[Path, str]] = None) -> None:
        self.config_path = Path(config_path) if config_path is not None else Path.cwd() / "config.yaml"

    def load(self) -> Config:
        base_path = self.config_path.parent
        if self.config_path.exists():
            with self.config_path.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or {}
        else:
            data = {}

        preview_folder = self._resolve_folder(base_path, data.get("preview_folder", "preview"))
        log_folder = self._resolve_folder(base_path, data.get("log_folder", "logs"))
        attachment_folder = self._resolve_folder(base_path, data.get("attachment_folder", "attachments"))
        templates_folder = self._resolve_folder(base_path, data.get("templates_folder", "templates"))
        use_default_outlook = bool(data.get("use_default_outlook", True))

        return Config(
            preview_folder=preview_folder,
            log_folder=log_folder,
            attachment_folder=attachment_folder,
            templates_folder=templates_folder,
            use_default_outlook=use_default_outlook,
        )

    @staticmethod
    def _resolve_folder(base_path: Path, folder_name: Any) -> Path:
        folder = Path(str(folder_name))
        if not folder.is_absolute():
            folder = base_path / folder
        return folder
