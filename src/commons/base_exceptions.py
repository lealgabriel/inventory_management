from typing import Any, Optional, Self, Union

from ..utils.types import JsonSerializable

class BaseCustomException(Exception):

    def __init__(self: Self, message: Optional[JsonSerializable] = None, *args: Any, **kwargs: Any) -> None:
        self.message = message or getattr(self, "message", "Exception not Mapped")
        super().__init__(message, *args, **kwargs)

    def __str__(self: Self) -> str:
        return f"{self.message}"



class CommonException(Exception):
    """Base exception class for all exceptions in this project."""

    code: int
    message: str
    detail: Union[Any, None]

    def __init__(
        self, code: int = 400, message: str = "Bad Request", detail: Union[Any, None] = None
    ):
        self.code = code
        self.message = message
        self.detail = detail

    def __str__(self):
        return f"""
            code: {self.code}
            message: {self.message}
            detail: {self.detail}
            traceback: {self.__traceback__}
            """

    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "detail": self.detail,
        }

class BusinessLogicException(BaseCustomException):
    pass


class RequiredParameterNotSetByTheServer(BusinessLogicException):
    pass


class SecurityBusinessLogicException(BusinessLogicException):
    pass


class AlreadyExistsException(CommonException):
    def __init__(self, message):
        super().__init__(code=409, message=message, detail="duplicate_entry")


class NotFoundException(CommonException):
    def __init__(self, message):
        super().__init__(code=404, message=message, detail="not_found")