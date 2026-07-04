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
    delivery_mode: str                    # "preview_only", "create_drafts", "send_immediately"
    email_provider: str                   # "outlook", "smtp"
    outlook_mailbox_email: Optional[str]  # Optional shared mailbox email
    smtp_enabled: bool
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_use_tls: bool
    smtp_use_ssl: bool


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
        delivery_mode = str(data.get("delivery_mode", "create_drafts"))
        email_provider = str(data.get("email_provider", "outlook"))
        outlook_mailbox_email = data.get("outlook_mailbox_email")
        smtp_enabled = bool(data.get("smtp_enabled", False))
        smtp_host = str(data.get("smtp_host", "smtp.example.com"))
        smtp_port = int(data.get("smtp_port", 587))
        smtp_username = str(data.get("smtp_username", ""))
        smtp_password = str(data.get("smtp_password", ""))
        smtp_use_tls = bool(data.get("smtp_use_tls", True))
        smtp_use_ssl = bool(data.get("smtp_use_ssl", False))

        return Config(
            preview_folder=preview_folder,
            log_folder=log_folder,
            attachment_folder=attachment_folder,
            templates_folder=templates_folder,
            use_default_outlook=use_default_outlook,
            delivery_mode=delivery_mode,
            email_provider=email_provider,
            outlook_mailbox_email=outlook_mailbox_email,
            smtp_enabled=smtp_enabled,
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_username=smtp_username,
            smtp_password=smtp_password,
            smtp_use_tls=smtp_use_tls,
            smtp_use_ssl=smtp_use_ssl,
        )

    @staticmethod
    def _resolve_folder(base_path: Path, folder_name: Any) -> Path:
        folder = Path(str(folder_name))
        if not folder.is_absolute():
            folder = base_path / folder
        return folder
