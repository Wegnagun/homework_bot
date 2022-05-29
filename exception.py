class HomeWorkBaseException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.msg = message if message else None

    def __str__(self):
        return f'Ошибка: {self.msg}!'


class ServerError(HomeWorkBaseException):
    pass


class CriticalSystemErrors(HomeWorkBaseException):
    pass
