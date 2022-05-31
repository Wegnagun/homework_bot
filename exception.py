class HomeWorkBaseException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.msg = message if message else None

    def __str__(self):
        return f'Ошибка: {self.msg}!'


class NotSendsError(HomeWorkBaseException):
    """Ошибки, когда не надо посылать в телегу."""
    pass


class SendMessageError(NotSendsError):
    """Провал в отсылке сообщения."""
    pass


class ResponseCodeError(NotSendsError):
    """Коды ответа сервера, отличные от 200."""
    pass


class ApiResponseError(NotSendsError):
    """Ошибки сервера."""
    pass


class ResponseContentError(NotSendsError):
    """Ошибки содержимого сервера."""
    pass
