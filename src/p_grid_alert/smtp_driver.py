from __future__ import annotations

import logging
import smtplib
from email.mime.text import MIMEText

from .utils import EMAIL_CONFIG

_LOGGER = logging.getLogger(__name__)


def send_alert(street: str, pdf_url: str, excerpt: str) -> None:
    """Send email alert for power outage."""
    try:
        recipients = [r.strip() for r in EMAIL_CONFIG['email_to'].split(',') if r.strip()]

        if not recipients:
            _LOGGER.warning('No email recipients configured')
            return

        msg = MIMEText(f'Outage scheduled for {street}\n\nPDF: {pdf_url}\n\n{excerpt}')
        msg['Subject'] = f'Power Outage Alert: {street}'
        msg['From'] = EMAIL_CONFIG['smtp_user']
        msg['To'] = ', '.join(recipients)

        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['smtp_user'], EMAIL_CONFIG['smtp_pass'])
            server.send_message(msg)

        _LOGGER.info(f'✓ Alert sent to {len(recipients)} recipient(s)')
    except Exception as e:
        _LOGGER.error(f'Failed to send email: {e}')
