class AppException(Exception):
    """
    Base exception for all application-level exceptions.
    All custom application exceptions should inherit from this class.
    """

    def __init__(
        self,
        message: str,
        code: str,
        status_code: int,
        details: dict | None = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details

        super().__init__(message)


class ResourceNotFoundException(AppException):
    """
    Raised when a requested resource does not exist.
    """

    def __init__(
        self,
        message: str,
        code: str = "RESOURCE_NOT_FOUND",
        details: dict | None = None,
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=404,
            details=details,
        )


class DuplicateResourceException(AppException):
    """
    Raised when creating a resource that already exists.
    """

    def __init__(
        self,
        message: str,
        code: str = "RESOURCE_ALREADY_EXISTS",
        details: dict | None = None,
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=409,
            details=details,
        )
