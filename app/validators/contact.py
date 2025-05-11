from app.core.config import settings


def validate_contact_email(email: str):
    """
    Validates the given email address.

    This function checks if the provided email address is not the test email
    defined in the settings. If the email is the test email, it returns False,
    indicating that the email should not be sent.

    Args:
        email (str): The email address to be validated.

    Returns:
        bool: True if the email is not the test email, False otherwise.
    """
    # In case of test email, don't send it
    return email != settings.EMAIL_TEST_USER
