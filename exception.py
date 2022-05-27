import requests
from telegram.error import TelegramError


class ResponseException(requests.exceptions.RequestException):
    def __init__(self, *args):
        super().__init__(*args)
        self.msg = args[0] if args else None

    def __str__(self):
        return f'Ошибка: {self.msg}!'


class ApiUnavailable(requests.ConnectionError):
    def __init__(self, *args):
        super().__init__(*args)
        self.msg = args[0] if args else None

    def __str__(self):
        return f'Ошибка: {self.msg}!'


class MessageDontSent(TelegramError):
    def __init__(self, *args):
        super().__init__(*args)
        self.msg = args[0] if args else None

    def __str__(self):
        return f'Ошибка: {self.msg}!'


class HaveEmptyResponse(Exception):
    def __init__(self, *args):
        super().__init__(*args)
        self.msg = args[0] if args else None

    def __str__(self):
        return f'Ошибка: {self.msg}!'
