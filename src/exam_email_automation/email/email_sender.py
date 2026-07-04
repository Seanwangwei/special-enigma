from pathlib import Path
from typing import Iterable, Optional


class OutlookEmailSender:
    """Outlook email sender supporting draft creation and immediate sending.

    Supports selecting a specific Outlook account and optional shared mailbox.
    Draft mode: creates email in Drafts folder without sending.
    Send mode: sends email immediately using Outlook's SMTP.

    Example (draft mode):
        sender = OutlookEmailSender(use_default_profile=True)
        sender.create_draft(to_address, subject, html_body)

    Example (send mode):
        sender.send_message(to_address, subject, html_body)
    """

    def __init__(self, use_default_profile: bool = True, mailbox_email: Optional[str] = None) -> None:
        """Initialize Outlook sender.

        Args:
            use_default_profile: If True, use logged-in user's default mailbox.
            mailbox_email: Optional email address of shared mailbox to use.
        """
        self.use_default_profile = use_default_profile
        self.mailbox_email = mailbox_email

    def _create_outlook(self):
        try:
            import win32com.client
        except ImportError as error:
            raise RuntimeError("Microsoft Outlook sender requires pywin32 on Windows.") from error
        return win32com.client.Dispatch("Outlook.Application")

    def _get_target_account(self, outlook):
        """Get the MAPI account to use for sending/drafting.

        If mailbox_email is specified, finds that account in Outlook.
        Otherwise returns the default account.
        """
        if not self.mailbox_email:
            return outlook.Session.Accounts(1)  # Default account

        # Find account by email address
        for account in outlook.Session.Accounts:
            if account.DisplayName == self.mailbox_email or account.SmtpAddress == self.mailbox_email:
                return account
        raise RuntimeError(f"Mailbox '{self.mailbox_email}' not found in Outlook")

    def create_draft(self, to_address: str, subject: str, html_body: str, attachments: Optional[Iterable[Path]] = None) -> None:
        """Create a draft email in Outlook without sending.

        Args:
            to_address: Recipient email address.
            subject: Email subject.
            html_body: Email body (HTML).
            attachments: Optional file paths to attach.
        """
        outlook = self._create_outlook()
        mail = outlook.CreateItem(0)  # 0 = MailItem
        mail.To = to_address
        mail.Subject = subject
        mail.HTMLBody = html_body

        for attachment in attachments or []:
            mail.Attachments.Add(str(Path(attachment).resolve()))

        # Save draft without sending
        mail.Save()

    def send_message(self, to_address: str, subject: str, html_body: str, attachments: Optional[Iterable[Path]] = None) -> None:
        """Send an email immediately via Outlook.

        Args:
            to_address: Recipient email address.
            subject: Email subject.
            html_body: Email body (HTML).
            attachments: Optional file paths to attach.
        """
        outlook = self._create_outlook()
        mail = outlook.CreateItem(0)  # 0 = MailItem
        mail.To = to_address
        mail.Subject = subject
        mail.HTMLBody = html_body

        for attachment in attachments or []:
            mail.Attachments.Add(str(Path(attachment).resolve()))

        mail.Send()
