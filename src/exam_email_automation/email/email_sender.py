from pathlib import Path
from typing import Iterable, Optional


class OutlookEmailSender:
    def __init__(self, use_default_profile: bool = True) -> None:
        self.use_default_profile = use_default_profile

    def _create_outlook(self):
        try:
            import win32com.client
        except ImportError as error:
            raise RuntimeError("Microsoft Outlook sender requires pywin32 on Windows.") from error
        return win32com.client.Dispatch("Outlook.Application")

    def send_message(self, to_address: str, subject: str, html_body: str, attachments: Optional[Iterable[Path]] = None) -> None:
        outlook = self._create_outlook()
        mail = outlook.CreateItem(0)
        mail.To = to_address
        mail.Subject = subject
        mail.HTMLBody = html_body

        for attachment in attachments or []:
            mail.Attachments.Add(str(Path(attachment).resolve()))

        mail.Send()
