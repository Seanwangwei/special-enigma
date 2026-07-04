from unittest.mock import patch, MagicMock

from exam_email_automation.email.email_sender import OutlookEmailSender


@patch('exam_email_automation.email.email_sender.OutlookEmailSender._create_outlook')
def test_create_draft(mock_create_outlook):
    mock_outlook = MagicMock()
    mock_mail = MagicMock()
    mock_outlook.CreateItem.return_value = mock_mail
    mock_create_outlook.return_value = mock_outlook

    sender = OutlookEmailSender()
    sender.create_draft('to@example.com', 'Subject', '<p>Body</p>')

    assert mock_outlook.CreateItem.called
    assert mock_mail.To == 'to@example.com'
    assert mock_mail.Subject == 'Subject'
    assert mock_mail.HTMLBody == '<p>Body</p>'
    assert mock_mail.Save.called
    assert not mock_mail.Send.called


@patch('exam_email_automation.email.email_sender.OutlookEmailSender._create_outlook')
def test_send_message(mock_create_outlook):
    mock_outlook = MagicMock()
    mock_mail = MagicMock()
    mock_outlook.CreateItem.return_value = mock_mail
    mock_create_outlook.return_value = mock_outlook

    sender = OutlookEmailSender()
    sender.send_message('to@example.com', 'Subject', '<p>Body</p>')

    assert mock_outlook.CreateItem.called
    assert mock_mail.To == 'to@example.com'
    assert mock_mail.Subject == 'Subject'
    assert mock_mail.HTMLBody == '<p>Body</p>'
    assert mock_mail.Send.called
    assert not mock_mail.Save.called


@patch('exam_email_automation.email.email_sender.OutlookEmailSender._create_outlook')
def test_create_draft_with_attachments(mock_create_outlook):
    from pathlib import Path
    mock_outlook = MagicMock()
    mock_mail = MagicMock()
    mock_outlook.CreateItem.return_value = mock_mail
    mock_create_outlook.return_value = mock_outlook

    sender = OutlookEmailSender()
    sender.create_draft('to@example.com', 'Subject', '<p>Body</p>', attachments=['file.pdf'])

    assert mock_mail.Attachments.Add.called
    assert mock_mail.Save.called
