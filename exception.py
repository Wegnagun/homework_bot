class HomeWorkBaseException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.msg = message if message else None

    def __str__(self):
        return f'Ошибка: {self.msg}!'


#############
# ошибки, не требующие пересылки в телеграм
#############
class NotSendsError(HomeWorkBaseException):
    pass


class SendMessageError(NotSendsError):
    pass


class ResponseCodeError(NotSendsError):
    pass


class ApiResponseError(NotSendsError):
    pass


class ResponseTypeError(NotSendsError):
    pass


class ResponseContentError(NotSendsError):
    pass


#############
# ошибки, требующие пересылки в телеграм
#############
class CriticalSystemErrors(HomeWorkBaseException):
    pass
