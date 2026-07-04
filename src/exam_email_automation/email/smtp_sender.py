from __future__ import annotations

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Optional

from .email_builder import EmailMessage


class SMTPConfig:
    def __init__(self, host: str, port: int = 587, username: Optional[str] = None, password: Optional[str] = None, use_ssl: bool = False, use_tls: bool = True):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.use_tls = use_tls


class SMTPEmailSender:
    """Simple SMTP email sender used for cross-platform delivery and testing.

    Example:
        cfg = SMTPConfig('smtp.example.com', 587, 'user', 'pass')
        sender = SMTPEmailSender(cfg)
        sender.send_message(email_message)
    """

    def __init__(self, config: SMTPConfig):
        self.config = config

    def _build_mime(self, message: EmailMessage) -> MIMEMultipart:
        msg = MIMEMultipart()
        msg['Subject'] = message.subject
        msg['From'] = self.config.username or 'noreply@example.com'
        msg['To'] = message.to_address

        msg.attach(MIMEText(message.html_body or '', 'html'))

        for attachment in message.attachments or []:
            p = Path(attachment)
            if not p.exists():
                continue
            part = MIMEBase('application', 'octet-stream')
            with open(p, 'rb') as f:
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{p.name}"')
            msg.attach(part)

        return msg

    def send_message(self, message: EmailMessage) -> None:
        msg = self._build_mime(message)
        recipients = [message.to_address]

        if self.config.use_ssl:
            smtp = smtplib.SMTP_SSL(self.config.host, self.config.port)
        else:
            smtp = smtplib.SMTP(self.config.host, self.config.port)

        try:
            smtp.ehlo()
            if not self.config.use_ssl and self.config.use_tls:
                smtp.starttls()
                smtp.ehlo()
            if self.config.username and self.config.password:
                smtp.login(self.config.username, self.config.password)
            smtp.sendmail(msg['From'], recipients, msg.as_string())
        finally:
            try:
                smtp.quit()
            except Exception:
                smtp.close()
