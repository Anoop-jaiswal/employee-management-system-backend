class AppException(Exception):
    """Base exception for application-level errors."""

    def __init__(
        self,
        message: str,
    ):
        self.message = message
        super().__init__(message)


class ResourceNotFoundException(AppException):
    """Raised when a requested resource does not exist."""


class DuplicateResourceException(AppException):
    """Raised when a resource already exists."""