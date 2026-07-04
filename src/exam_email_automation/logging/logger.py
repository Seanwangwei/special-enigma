import logging
from pathlib import Path
from typing import Any
import pandas as pd


def configure_logging(log_folder: Path, logger_name: str = "exam_email_automation") -> logging.Logger:
    log_folder.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        file_handler = logging.FileHandler(log_folder / "application.log", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


class AuditLogger:
    def __init__(self, log_folder: Path) -> None:
        self.log_folder = log_folder
        self.log_folder.mkdir(parents=True, exist_ok=True)

    def save(self, records: list[dict[str, Any]]) -> Path:
        df = pd.DataFrame(records)
        path = self.log_folder / "send_log.xlsx"
        df.to_excel(path, index=False)
        return path
