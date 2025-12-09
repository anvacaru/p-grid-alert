from __future__ import annotations

import logging
import smtplib
from email.mime.text import MIMEText

from .utils import EMAIL_CONFIG

_LOGGER = logging.getLogger(__name__)


def send_alert(street: str, pdf_url: str, events: list[dict[str, str]]) -> None:
    """Send email alert for power outage(s)."""
    try:
        recipients = [r.strip() for r in EMAIL_CONFIG['email_to'].split(',') if r.strip()]

        if not recipients:
            _LOGGER.warning('No email recipients configured')
            return

        body = message_body(street, pdf_url, events)

        msg = MIMEText(body)
        msg['Subject'] = f'Alerta Intrerupere de Curent: {street} - {len(events)} evenimente'
        msg['From'] = EMAIL_CONFIG['smtp_user']
        msg['To'] = ', '.join(recipients)

        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['smtp_user'], EMAIL_CONFIG['smtp_pass'])
            server.send_message(msg)

        _LOGGER.info(f'✓ Alert sent to {len(recipients)} recipient(s) with {len(events)} event(s)')
    except Exception as e:
        _LOGGER.error(f'Failed to send email: {e}')


def message_body(street: str, pdf_url: str, events: list[dict[str, str]]) -> str:
    event_details = '\n\n'.join(
        [
            f"Eveniment {i+1}:\nZiua: {event['day']}\nPerioada: {event['time']}\n\nContext:\n{event['excerpt']}"
            for i, event in enumerate(events)
        ]
    )

    return f"""Intreruperi de curent programate pentru strada {street}.

Au fost gasite {len(events)} intreruperi programate:

{event_details}

Document PDF: {pdf_url}
"""
