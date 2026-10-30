from __future__ import annotations

import logging
import smtplib
from email.mime.text import MIMEText
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from p_grid_alert.event_processor import OutageEvent
    from p_grid_alert.utils import EmailConfig

_LOGGER = logging.getLogger(__name__)


def send_alert(street: str, pdf_url: str, events: list[OutageEvent], email: EmailConfig) -> None:
    """Send one email alert listing all `events`; SMTP errors propagate to the caller."""
    msg = MIMEText(message_body(street, pdf_url, events))
    msg['Subject'] = f'Alerta Intrerupere de Curent: {street} - {len(events)} evenimente'
    msg['From'] = email.smtp_user
    msg['To'] = ', '.join(email.recipients)

    with smtplib.SMTP(email.smtp_server, email.smtp_port) as server:
        server.starttls()
        server.login(email.smtp_user, email.smtp_pass)
        server.send_message(msg)

    _LOGGER.info(
        f'✓ Alert sent to {len(email.recipients)} recipient(s) with {len(events)} event(s)'
    )


def message_body(street: str, pdf_url: str, events: list[OutageEvent]) -> str:
    event_details = '\n\n'.join(
        [
            f'Eveniment {i+1}:\nZiua: {event.day}\nPerioada: {event.hours or "necunoscuta"}'
            f'\n\nContext:\n{event.excerpt}'
            for i, event in enumerate(events)
        ]
    )

    return f"""Intreruperi de curent programate pentru strada {street}.

Au fost gasite {len(events)} intreruperi programate:

{event_details}

Document PDF: {pdf_url}
"""
