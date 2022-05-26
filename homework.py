import logging
import sys
import os
import requests
from dotenv import load_dotenv
import telegram
from telegram import ReplyKeyboardMarkup, Bot
from telegram.ext import CommandHandler, Updater
import time
import emojis

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM')
TELEGRAM_TOKEN = os.getenv('TELEGRAM')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHATID')
homework_status = None

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
    try:
        request = requests.get(ENDPOINT, headers=HEADERS, params=params)
        request.raise_for_status()
        return request.json()
    except requests.exceptions.HTTPError as error:
        raise SystemExit(error)


def check_response(response):
    """проверяем наличии в респонсе словаря homeworks"""
    try:
        homework = response['homeworks']
        return homework
    except KeyError as ex:
        print(ex)


def parse_status(homework):
    """парсим данные с ответа яндекс.домашка"""
    global homework_status
    homework_name = homework[0]['homework_name']
    if homework_status != homework[0]['status']:
        homework_status = homework[0]['status']
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    else:
        return 'Статус проверки работы пока не изменился'


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
    if check_tokens():
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        send_message(bot,
                     'Начинаю запрашивать информацию о статусе домашки'
                     + emojis.encode(':sob:'))
        while True:
            try:
                logger.debug('Запуск')
                current_timestamp = int(time.time())
                response = get_api_answer(current_timestamp - 2592000)
                homework = check_response(response)
                send_message(bot, parse_status(homework))
                time.sleep(5)
            except Exception as error:
                message = (f'Сбой в работе программы: {error} '
                           + emojis.encode(':sob:'))
                send_message(bot, message)
                time.sleep(RETRY_TIME)
            else:
                # какой-то конец
                pass
    else:
        logger.error('Ошибка, проверьте токены в .env')


if __name__ == '__main__':
    # try:
    #     current_timestamp = int(time.time())
    #     timestamp = current_timestamp - 2592000
    #     params = {'from_date': timestamp}
    #     request = requests.get(ENDPOINT, headers=HEADERS, params=0)
    #     request.raise_for_status()
    # except requests.exceptions.HTTPError as error:
    #     raise SystemExit(error)
    main()
