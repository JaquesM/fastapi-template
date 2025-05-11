from fastapi import HTTPException


# Login Exceptions
class UserNotFoundException(HTTPException):
    """
    Exception raised when a user email was not found.

    This exception is typically raised when an attempt is made to access
    a user by email, but no user with the specified email exists in the system.

    Attributes:
        status_code (int): The HTTP status code for the exception (404).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=404, detail="A user with this email does not exist in the system.")

class UserNotActiveException(HTTPException):
    """
    Exception raised when the user is not active.

    This exception is typically raised when an attempt is made to access
    a user that is not active in the system.

    Attributes:
        status_code (int): The HTTP status code for the exception (403).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=403, detail="This user is not active.")

class CustomerNotFoundException(HTTPException):
    """
    Exception raised when a customer was not found.

    This exception is typically raised when an attempt is made to access
    a customer that does not exist in the system.

    Attributes:
        status_code (int): The HTTP status code for the exception (404).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=404, detail="Customer not found.")


# Permissions Exceptions
class UserNotAuthenticatedException(HTTPException):
    """
    Exception raised when a user is not authenticated.

    This exception is typically raised when an attempt is made to access
    a user that is not authenticated in the system.

    Attributes:
        status_code (int): The HTTP status code for the exception (401).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=401, detail="The user is not authenticated.")

class UserHasNoAccessToCustomerException(HTTPException):
    """
    Exception raised when a user has no access to a customer.

    This exception is typically raised when an attempt is made to access
    a customer that the user has no access to.

    Attributes:
        status_code (int): The HTTP status code for the exception (403).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=403, detail="The user has no access to this customer.")

class UserActionNotAllowedException(HTTPException):
    """
    Exception raised when a user attempts to perform an action they are not allowed to.

    Attributes:
        status_code (int): HTTP status code for the exception, defaults to 403.
        detail (str): A message providing more details about the exception.
    """
    def __init__(self):
        super().__init__(status_code=403, detail="The user is not allowed to perform this action.")

class UserNotSuperuserException(HTTPException):
    """
    Exception raised when a user is not a superuser.

    This exception is typically raised when an attempt is made to access
    a superuser that does not exist in the system.

    Attributes:
        status_code (int): The HTTP status code for the exception (403).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=403, detail="This user doesn't have enough privileges.")


# Token Exceptions
class TokenExpiredException(HTTPException):
    """
    Exception raised when a token has expired.

    This exception is typically raised when an attempt is made to access
    a token that has expired.

    Attributes:
        status_code (int): The HTTP status code for the exception (401).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=401, detail="Token expired.")

class InvalidTokenException(HTTPException):
    """
    Exception raised when a token is invalid.

    This exception is typically raised when an attempt is made to access
    a token that is invalid.

    Attributes:
        status_code (int): The HTTP status code for the exception (400).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=400, detail="Invalid token.")

class InvalidRefreshTokenException(HTTPException):
    """
    Exception raised when a refresh token is invalid.

    This exception is typically raised when an attempt is made to access
    a refresh token that is invalid.

    Attributes:
        status_code (int): The HTTP status code for the exception (400).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=400, detail="Invalid refresh token.")

class TokenRevokedException(HTTPException):
    """
    Exception raised when a token has been revoked.

    This exception is typically raised when an attempt is made to access
    a token that has been revoked.

    Attributes:
        status_code (int): The HTTP status code for the exception (401).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=401, detail="Token has been revoked.")

class TokenNotFoundException(HTTPException):
    """
    Exception raised when a token is not found.

    This exception is typically raised when an attempt is made to access
    a token that is not found.

    Attributes:
        status_code (int): The HTTP status code for the exception (404).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=404, detail="Token not found.")

class TokenHasBeenUsedException(HTTPException):
    """
    Exception raised when a token has been used.

    This exception is typically raised when an attempt is made to access
    a token that has been used.

    Attributes:
        status_code (int): The HTTP status code for the exception (401).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=401, detail="Token has been used.")


# OAuth2 Exceptions
class GoogleOAuthException(HTTPException):
    """
    Exception raised when an error occurs with Google OAuth.

    This exception is typically raised when an error occurs with Google OAuth.

    Attributes:
        status_code (int): The HTTP status code for the exception (400).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=400, detail="An error occurred with Google OAuth.")

class MicrosoftOAuthException(HTTPException):
    """
    Exception raised when an error occurs with Microsoft OAuth.

    This exception is typically raised when an error occurs with Microsoft OAuth.

    Attributes:
        status_code (int): The HTTP status code for the exception (400).
        detail (str): A message describing the exception.
    """
    def __init__(self):
        super().__init__(status_code=400, detail="An error occurred with Microsoft OAuth.")

