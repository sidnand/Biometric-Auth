from typing import Optional, Union
from .errors import Error

class ResponseManager:
    @staticmethod
    def error_response(error: Error, message: str) -> dict:
        return {
            "success": False,
            "error": {
                "code": error.code,
                "message": message
            }
        }, error.http_status

    @staticmethod
    def get_error_response(error: Error) -> dict:
        default_message = "Unknown error occurred."
        return ResponseManager.error_response(error, error.message)

    @staticmethod
    def success_response(data: Optional[Union[dict, list]] = None) -> dict:
        return {
            "success": True,
            "data": data
        }, 200