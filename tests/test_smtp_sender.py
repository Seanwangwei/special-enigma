from __future__ import annotations

import threading
import time
from unittest.mock import patch, MagicMock

from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Message

from exam_email_automation.email.smtp_sender import SMTPConfig, SMTPEmailSender
from exam_email_automation.email.email_builder import EmailMessage


class DummySMTPHandler(Message):
    def __init__(self):
        super().__init__()
        self.received = []

    def handle_message(self, message):
        self.received.append((message['from'], message['to'], message.as_bytes()))


def test_smtp_sender_sends_message():
    handler = DummySMTPHandler()
    controller = Controller(handler, hostname='127.0.0.1', port=1025)
    controller.start()
    try:
        cfg = SMTPConfig('127.0.0.1', 1025, use_ssl=False, use_tls=False)
        sender = SMTPEmailSender(cfg)

        msg = EmailMessage(to_address='to@example.com', subject='Test', html_body='<p>hi</p>')
        sender.send_message(msg)

        time.sleep(0.1)
        assert len(handler.received) == 1
        mailfrom, rcpttos, data = handler.received[0]
        assert mailfrom == 'noreply@example.com'
        assert rcpttos == 'to@example.com'
    finally:
        controller.stop()


def make_message():
    return EmailMessage(
        to_address='to@example.com',
        subject='Test',
        html_body='<p>Hello</p>',
        attachments=[],
    )


@patch('exam_email_automation.email.smtp_sender.smtplib.SMTP')
def test_send_message_tls(mock_smtp_cls):
    mock_smtp = MagicMock()
    mock_smtp_cls.return_value = mock_smtp

    cfg = SMTPConfig('smtp.example.com', 587, username='u', password='p', use_ssl=False, use_tls=True)
    sender = SMTPEmailSender(cfg)
    sender.send_message(make_message())

    mock_smtp.ehlo.assert_called()
    mock_smtp.starttls.assert_called()
    mock_smtp.login.assert_called_with('u', 'p')
    mock_smtp.sendmail.assert_called()


@patch('exam_email_automation.email.smtp_sender.smtplib.SMTP_SSL')
def test_send_message_ssl(mock_smtp_ssl_cls):
    mock_smtp = MagicMock()
    mock_smtp_ssl_cls.return_value = mock_smtp

    cfg = SMTPConfig('smtp.example.com', 465, username='u', password='p', use_ssl=True, use_tls=False)
    sender = SMTPEmailSender(cfg)
    sender.send_message(make_message())

    mock_smtp.ehlo.assert_called()
    mock_smtp.login.assert_called_with('u', 'p')
    mock_smtp.sendmail.assert_called()
