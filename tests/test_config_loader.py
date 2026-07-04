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


def test_load_custom_config(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "preview_folder: custom_preview\nlog_folder: custom_logs\nattachment_folder: custom_attachments\ntemplates_folder: custom_templates\nuse_default_outlook: false\n",
        encoding="utf-8",
    )
    loader = ConfigLoader(config_file)
    config = loader.load()

    assert config.preview_folder == tmp_path / "custom_preview"
    assert config.log_folder == tmp_path / "custom_logs"
    assert config.attachment_folder == tmp_path / "custom_attachments"
    assert config.templates_folder == tmp_path / "custom_templates"
    assert config.use_default_outlook is False
