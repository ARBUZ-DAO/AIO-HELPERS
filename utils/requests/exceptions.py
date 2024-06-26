class ClientException(Exception):
    pass


class APIException(Exception):
    pass


class TransactionException(Exception):
    pass


class HTTPException(Exception):
    """
    An exception that occurs when an HTTP request is unsuccessful.

    Attributes:
        response (Optional[Dict[str, Any]]): a JSON response to a request.
        status_code (Optional[int]): a request status code.

    """
    response: dict[str, ...] | None
    status_code: int | None

    def __init__(self, response: dict[str, ...] | None = None, status_code: int | None = None) -> None:
        """
        Initialize the class.

        Args:
            response (Optional[Dict[str, Any]]): a JSON response to a request. (None)
            status_code (Optional[int]): a request status code. (None)

        """
        self.response = response
        self.status_code = status_code

    def __str__(self):
        if self.response:
            return f'{self.status_code}: {self.response}'

        return f'{self.status_code}'