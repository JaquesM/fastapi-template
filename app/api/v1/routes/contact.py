from fastapi import APIRouter

from app.validators.contact import validate_contact_email
from app.schemas import Message
from app.schemas.contact import NewContact
from app.services.email import send_email, render_email_template
from app.core.config import settings

router = APIRouter()

@router.post("/", response_model=Message)
def send_contact_info(contact_input: NewContact) -> Message:
    """
    Sends contact information via email.

    This function performs the following actions:
    - Sends an email to a predefined recipient with the provided contact details.
    - Sends a confirmation email to the contact, acknowledging receipt of their information.

    **Args:**
    - `contact_input (NewContact)`: An instance containing the contact's details.

    **Returns:**
    - `Message`: A confirmation message indicating that the contact information was sent successfully.
    """

    # In case of test email, don't send it
    if validate_contact_email(contact_input.email):
        # Send email to default from email address
        send_email(
            email_to=settings.EMAILS_FROM_EMAIL,
            subject="Novo Contato do Site",
            html_content = render_email_template(
                template_name="new_contact.html",
                context={
                    "name": contact_input.name,
                    "email": contact_input.email,
                    "phone": contact_input.phone,
                    "company": contact_input.company
                },
            )
        )

        # Send email to the Contact
        send_email(
            email_to=contact_input.email,
            subject="Contato Recebido",
            html_content = render_email_template(
                template_name="contact_received.html",
                context={
                    "name": contact_input.name,
                },
            )
        )

    return Message(message="Contact info sent successfully")
