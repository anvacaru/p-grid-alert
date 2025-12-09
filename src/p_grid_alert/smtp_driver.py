from __future__ import annotations

import logging
import smtplib
from email.mime.text import MIMEText

from .utils import EMAIL_CONFIG

_LOGGER = logging.getLogger(__name__)


def send_alert(street: str, pdf_url: str, excerpt: str, day: str, time: str) -> None:
    """Send email alert for power outage."""
    try:
        recipients = [r.strip() for r in EMAIL_CONFIG['email_to'].split(',') if r.strip()]

        if not recipients:
            _LOGGER.warning('No email recipients configured')
            return

        body = message_body(street, pdf_url, excerpt, day, time)

        msg = MIMEText(body)
        msg['Subject'] = f'Alerta Intrerupere de Curent: {street} - {day} {time}'
        msg['From'] = EMAIL_CONFIG['smtp_user']
        msg['To'] = ', '.join(recipients)

        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['smtp_user'], EMAIL_CONFIG['smtp_pass'])
            server.send_message(msg)

        _LOGGER.info(f'✓ Alert sent to {len(recipients)} recipient(s)')
    except Exception as e:
        _LOGGER.error(f'Failed to send email: {e}')


def message_body(street: str, pdf_url: str, excerpt: str, day: str, time: str) -> str:
    return f"""Intrerupere de curent programata pentru strada {street}.

Ziua: {day}
Perioada: {time}

Document PDF: {pdf_url}

Context:
{excerpt}
"""
