"""
Real email sending via SendGrid.

Handles template rendering and email delivery with retry.
"""

from __future__ import annotations

import os
from typing import Dict, Optional

from jinja2.sandbox import SandboxedEnvironment
from jinja2 import BaseLoader
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
)

from velora_common.logging import get_logger

logger = get_logger(__name__)


class EmailSender:
    """SendGrid-based email sender with template rendering."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        from_email: Optional[str] = None,
    ) -> None:
        self._api_key = api_key or os.environ.get(
            "SENDGRID_API_KEY", ""
        )
        self._from_email = from_email or os.environ.get(
            "EMAIL_FROM_ADDRESS",
            "noreply@velora.io",
        )
        self._jinja = SandboxedEnvironment(loader=BaseLoader())

        if not self._api_key:
            logger.warning(
                "email_sender_not_configured",
                reason="SENDGRID_API_KEY not set",
            )

    def render_template(
        self,
        template_body: str,
        context: Dict[str, str],
    ) -> str:
        """Render a Jinja2 email template."""
        tmpl = self._jinja.from_string(template_body)
        return tmpl.render(**context)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        plain_body: Optional[str] = None,
    ) -> bool:
        """Send an email via SendGrid API."""
        if not self._api_key:
            logger.warning(
                "email_not_sent",
                reason="no API key",
                to=to_email[:3] + "***",
            )
            return False

        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import (
                Content,
                Email,
                Mail,
                To,
            )

            sg = SendGridAPIClient(self._api_key)
            message = Mail(
                from_email=Email(self._from_email),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content(
                    "text/html", html_body
                ),
            )
            if plain_body:
                message.add_content(
                    Content("text/plain", plain_body)
                )

            response = sg.send(message)

            logger.info(
                "email_sent",
                status=response.status_code,
                to=to_email[:3] + "***",
            )
            return response.status_code in (200, 201, 202)

        except Exception:
            logger.exception(
                "email_send_failed",
                to=to_email[:3] + "***",
            )
            raise

    async def send_assessment_invitation(
        self,
        to_email: str,
        vendor_name: str,
        assessment_title: str,
        due_date: str,
        portal_url: str,
        template_body: Optional[str] = None,
    ) -> bool:
        """Send assessment invitation email."""
        default_template = """
        <h2>Assessment Request: {{ assessment_title }}</h2>
        <p>Dear {{ vendor_name }} Team,</p>
        <p>You have been invited to complete a security assessment.</p>
        <ul>
            <li><strong>Assessment:</strong> {{ assessment_title }}</li>
            <li><strong>Due Date:</strong> {{ due_date }}</li>
        </ul>
        <p><a href="{{ portal_url }}">Complete Assessment</a></p>
        <p>Best regards,<br>Velora TPRM</p>
        """
        body = template_body or default_template
        html = self.render_template(body, {
            "vendor_name": vendor_name,
            "assessment_title": assessment_title,
            "due_date": due_date,
            "portal_url": portal_url,
        })
        return await self.send_email(
            to_email=to_email,
            subject=f"Assessment Request: {assessment_title}",
            html_body=html,
        )

    async def send_reminder(
        self,
        to_email: str,
        vendor_name: str,
        assessment_title: str,
        days_remaining: int,
        portal_url: str,
    ) -> bool:
        """Send assessment reminder email."""
        html = self.render_template("""
        <h2>Reminder: {{ assessment_title }}</h2>
        <p>Dear {{ vendor_name }} Team,</p>
        <p>This is a reminder that your assessment is due
        in <strong>{{ days_remaining }} days</strong>.</p>
        <p><a href="{{ portal_url }}">Complete Assessment</a></p>
        """, {
            "vendor_name": vendor_name,
            "assessment_title": assessment_title,
            "days_remaining": str(days_remaining),
            "portal_url": portal_url,
        })
        return await self.send_email(
            to_email=to_email,
            subject=(
                f"Reminder: {assessment_title} "
                f"— {days_remaining} days remaining"
            ),
            html_body=html,
        )
