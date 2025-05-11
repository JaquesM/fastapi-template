from fastapi import HTTPException


class CampaignAlreadyExistsException(HTTPException):
    """
    Exception raised when a campaign already exists.

    This exception is typically raised when an attempt is made to add a campaign
    to a customer, but a campaign with this name already exists for that customer.

    Attributes:
        status_code (int): The HTTP status code for the exception (404).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=404, detail="A campaign with this name already exists for that customer.")

class CampaignNotFoundException(HTTPException):
    """
    Exception raised when a campaign is not found.

    This exception is typically raised when an attempt is made to update or delete
    a campaign, but the campaign with the specified ID does not exist.

    Attributes:
        status_code (int): The HTTP status code for the exception (404).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=404, detail="Campaign not found.")

class CampaignNotAssociatedException(HTTPException):
    """
    Exception raised when a campaign is not associated with a customer.

    This exception is typically raised when an attempt is made to update or delete
    a campaign, but the campaign is not associated with the customer.

    Attributes:
        status_code (int): The HTTP status code for the exception (404).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=404, detail="Campaign not associated with the customer.")

class CampaignNotAllowedException(HTTPException):
    """
    Exception raised when a user is not allowed to access a campaign.

    This exception is typically raised when an attempt is made to access a campaign,
    but the user is not allowed to access the campaign.

    Attributes:
        status_code (int): The HTTP status code for the exception (403).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=403, detail="The user has no access to this campaign.")

class InvalidCampaignNameException(HTTPException):
    """
    Exception raised when a campaign name is invalid.

    This exception is typically raised when an attempt is made to create a campaign,
    but the campaign name is invalid.

    Attributes:
        status_code (int): The HTTP status code for the exception (422).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=422, detail="Invalid campaign name.")

class InvalidCampaignEndDateException(HTTPException):
    """
    Exception raised when a campaign end date is invalid.

    This exception is typically raised when an attempt is made to create a campaign,
    but the campaign end date is invalid.

    Attributes:
        status_code (int): The HTTP status code for the exception (422).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=422, detail="Invalid campaign end date.")


# Enpoint-specific exceptions
class CouldNotCreateCampaignException(HTTPException):
    """
    Exception raised when a campaign could not be created.

    This exception is typically raised when an attempt is made to create a campaign,
    but the operation fails for some reason.

    Attributes:
        status_code (int): The HTTP status code for the exception (500).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=500, detail="Could not create campaign.")

