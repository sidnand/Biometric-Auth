from enum import Enum

class Error(Enum):
    """
    Enum class for error codes and messages.

    Attributes:
        USER_NOT_FOUND (tuple): The error code and message for user not found.
        INTERNAL_SERVER_ERROR (tuple): The error code and message for internal server error.
        UNAUTHORIZED (tuple): The error code and message for unauthorized access.
    """

    USER_NOT_FOUND = ("user_not_found", "User not found.", 404)
    INTERNAL_SERVER_ERROR = ("internal_server_error", "Internal server error. Please try again later.", 500)
    UNAUTHORIZED = ("unauthorized", "Unauthorized", 401)

    def __init__(self, code: str, message: str, http_status: int) -> None:
        self._code = code
        self._message = message
        self._http_status = http_status

    @property
    def code(self) -> str:
        return self._code

    @property
    def message(self) -> str:
        return self._message

    @property
    def http_status(self) -> int:
        return self._http_status