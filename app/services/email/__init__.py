from dataclasses import dataclass
from pathlib import Path
from typing import Any
from jinja2 import Template

from app.core.config import settings

from app.services.monitoring import logger
from app.services.boto3 import get_aws_session

session = get_aws_session()
ses_client = session.client("ses")

@dataclass
class EmailData:
    html_content: str
    subject: str


def send_email(
    *,
    email_to: str,
    subject: str = "",
    html_content: str = "",
) -> None:

    response = ses_client.send_email(
        Source=settings.EMAILS_FROM_EMAIL,
        Destination={
            'ToAddresses': [email_to],
        },
        Message={
            'Subject': {
                'Data': subject,
            },
            'Body': {
                'Html': {
                    'Data': html_content,
                },
            },
        },
    )

    logger.info(f"send email result: {response}")


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template_str = (
        Path(__file__).parent / "email-templates" / "build" / template_name
    ).read_text()
    html_content = Template(template_str).render(context)
    return html_content


# Specific email templates
def generate_magic_link_email(customer_name: str, username: str, link: str, valid_minutes: int) -> EmailData:
    subject = f"{customer_name} - Login link"
    html_content = render_email_template(
        template_name="magic_link.html",
        context={"customer_name": customer_name, "username": username, "link": link, "valid_minutes": valid_minutes},
    )
    return EmailData(html_content=html_content, subject=subject)

