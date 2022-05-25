import logging
import sys
import os
import requests
from dotenv import load_dotenv
import telegram
from telegram import ReplyKeyboardMarkup, Bot
from telegram.ext import CommandHandler, Updater
import time

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM')
TELEGRAM_TOKEN = os.getenv('TELEGRAM')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHATID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)


def send_message(bot, message):
    """ Отправка ботом сообщений в чат """
    logger.info('отправка сообщения')
    return bot.send_message(TELEGRAM_CHAT_ID, message)


def get_api_answer(current_timestamp):
    """ получаем ответ с API домашки """
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    return requests.get(ENDPOINT, headers=HEADERS, params=params).json()


def check_response(response):
    try:
        homework = response['homeworks']
        return homework
    except KeyError as ex:
        print('dddd')


def parse_status(homework):
    """парсим данные с ответа яндекс.домашка"""
    homework_name = homework['homework_name']
    homework_status = ...

    ...

    verdict = homework['status']

    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """ проверяем доступность переменных окружения """
    if (PRACTICUM_TOKEN is not None
            and TELEGRAM_TOKEN is not None
            and TELEGRAM_CHAT_ID is not None):
        return True
    else:
        return False


def main():
    """Основная логика работы бота."""

    ...

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)
            parse_status(homework)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            time.sleep(RETRY_TIME)
        else:
            pass


if __name__ == '__main__':
    print(get_api_answer(1653481042 - 2592000)['homeworks'])
    # main()
