import requests
from telegram.error import TelegramError


class ResponseException(requests.exceptions.RequestException):
    pass


class ApiUnavailable(requests.ConnectionError):
    pass


class MessageDontSent(TelegramError):
    pass
