from fastapi import HTTPException

class UserNotFoundException(HTTPException):
    """
    Exception raised when a user is not found.

    This exception is typically raised when an attempt is made to retrieve a user
    that does not exist.

    Attributes:
        status_code (int): The HTTP status code for the exception (404).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=404, detail="User not found.")

class InvalidUserNameException(HTTPException):
    """
    Exception raised when a user name is invalid.

    This exception is typically raised when an attempt is made to create a user
    with an invalid name.

    Attributes:
        status_code (int): The HTTP status code for the exception (422).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=422, detail="Invalid user name.")

class InvalidUserEmailException(HTTPException):
    """
    Exception raised when a user email is invalid.

    This exception is typically raised when an attempt is made to create a user
    with an invalid email.

    Attributes:
        status_code (int): The HTTP status code for the exception (422).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=422, detail="Invalid user email.")
        
class InvalidUserRoleRequirementsException(HTTPException):
    """
    Exception raised when a user role requirements are not met.

    This exception is typically raised when an attempt is made to create a visitor
    user without specifying any campaigns.

    Attributes:
        status_code (int): The HTTP status code for the exception (422).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=422, detail="Invalid user role requirements.")

class UserCustomerLinkAlreadyExistException(HTTPException):
    """
    Exception raised when a user is already associated to a customer.

    This exception is typically raised when an attempt is made to add a user
    to a customer, but the user already exists in that customer.

    Attributes:
        status_code (int): The HTTP status code for the exception (404).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=404, detail="A user with this email already exists for that customer.")

class UserCustomerLinkNotFoundException(HTTPException):
    """
    Exception raised when a user-customer link is not found.

    This exception is typically raised when an attempt is made to retrieve a user-customer link
    that does not exist.

    Attributes:
        status_code (int): The HTTP status code for the exception (404).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=404, detail="This user has no access to this customer.")

# Enpoint-specific exceptions
class CouldNotCreateUserException(HTTPException):
    """
    Exception raised when a user could not be created.

    This exception is typically raised when an attempt is made to create a user.

    Attributes:
        status_code (int): The HTTP status code for the exception (500).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=500, detail="Could not create user.")
