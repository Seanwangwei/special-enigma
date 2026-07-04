from enum import Enum


class DeliveryMode(Enum):
    """Email delivery mode selection.
    
    PREVIEW_ONLY: Generate and save HTML preview without creating emails.
    CREATE_DRAFTS: Create Outlook draft emails (default; Windows only).
    SEND_IMMEDIATELY: Send emails immediately via Outlook or SMTP.
    """

    PREVIEW_ONLY = "preview_only"
    CREATE_DRAFTS = "create_drafts"
    SEND_IMMEDIATELY = "send_immediately"
