from pathlib import Path
from exam_email_automation.config.config_loader import ConfigLoader


def test_load_default_config(tmp_path: Path) -> None:
    loader = ConfigLoader(tmp_path / "missing_config.yaml")
    config = loader.load()

    assert config.preview_folder == tmp_path / "preview"
    assert config.log_folder == tmp_path / "logs"
    assert config.attachment_folder == tmp_path / "attachments"
    assert config.templates_folder == tmp_path / "templates"
    assert config.use_default_outlook is True
    assert config.delivery_mode == "create_drafts"
    assert config.email_provider == "outlook"
    assert config.outlook_mailbox_email is None
    assert config.smtp_enabled is False


def test_load_custom_config(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """preview_folder: custom_preview
log_folder: custom_logs
attachment_folder: custom_attachments
templates_folder: custom_templates
use_default_outlook: false
delivery_mode: send_immediately
email_provider: outlook
outlook_mailbox_email: shared@example.com
smtp_enabled: true
smtp_host: smtp.gmail.com
smtp_port: 465
smtp_username: user@gmail.com
smtp_password: secret
smtp_use_tls: false
smtp_use_ssl: true
""",
        encoding="utf-8",
    )
    loader = ConfigLoader(config_file)
    config = loader.load()

    assert config.preview_folder == tmp_path / "custom_preview"
    assert config.log_folder == tmp_path / "custom_logs"
    assert config.attachment_folder == tmp_path / "custom_attachments"
    assert config.templates_folder == tmp_path / "custom_templates"
    assert config.use_default_outlook is False
    assert config.delivery_mode == "send_immediately"
    assert config.email_provider == "outlook"
    assert config.outlook_mailbox_email == "shared@example.com"
    assert config.smtp_enabled is True
    assert config.smtp_host == "smtp.gmail.com"
    assert config.smtp_port == 465
    assert config.smtp_username == "user@gmail.com"
    assert config.smtp_password == "secret"
    assert config.smtp_use_ssl is True
    assert config.smtp_use_tls is False


def test_templates_folder_resolves_relative_to_config_path(tmp_path: Path) -> None:
    """The templates folder should be resolved relative to the config file's directory."""
    config_content = "templates_folder: my_templates\n"
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content, encoding="utf-8")

    loader = ConfigLoader(config_file)
    config = loader.load()

    assert config.templates_folder == tmp_path / "my_templates"


def test_templates_folder_defaults_when_not_configured(tmp_path: Path) -> None:
    """When templates_folder is not in config, it defaults relative to the config path."""
    config_content = "preview_folder: preview\n"
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content, encoding="utf-8")

    loader = ConfigLoader(config_file)
    config = loader.load()

    assert config.templates_folder == tmp_path / "templates"
