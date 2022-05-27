import logging
import os
import sys
import time
from http import HTTPStatus

import emojis
import requests
import telegram
from dotenv import load_dotenv

from exception import ResponseException, ApiUnavailable, MessageDontSent

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
    try:
        return bot.send_message(TELEGRAM_CHAT_ID, message)
    except MessageDontSent:
        logger.error('не удалось отправить сообщение')


def get_api_answer(current_timestamp):
    """ получаем ответ с API домашки """
    timestamp = current_timestamp
    params = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            url=ENDPOINT,
            headers=HEADERS,
            params=params,
        )
        logger.info(f'Ответ сервера {homework_statuses.status_code}')
        if homework_statuses.status_code != HTTPStatus.OK:
            logger.error(f'Ошибка {homework_statuses.status_code}!')
            raise ResponseException(f'Ошибка {homework_statuses.status_code}!')
        return homework_statuses.json()
    except requests.ConnectionError:
        logger.error(f'Адрес {ENDPOINT} недоступен!')
        raise ApiUnavailable(f'Адрес {ENDPOINT} недоступен!')


def check_response(response):
    """проверяем наличии в респонсе словаря homeworks"""
    try:
        homework = response['homeworks']
        if type(homework) != list:
            logger.error('в респонсе содержится не list')
            raise TypeError('в респонсе содержится не list')
        else:
            return homework[0]
    except KeyError:
        raise KeyError('вот беда, ай-ай-ай')


def parse_status(homework):
    """парсим данные с ответа яндекс.домашка"""
    global homework_status
    if homework['homework_name'] not in homework:
        print(homework)
        logger.error('ключа "homework_name" нет в homework')
        raise KeyError('ключа "homework_name" нет в homework')
    else:
        homework_name = homework['homework_name']
    if homework['status'] not in HOMEWORK_STATUSES:
        logger.error('такой статус проверки не известен')
        raise KeyError(f"статуса {homework['status']} нет в HOMEWORK_STATUSES")
    if homework_status != homework['status']:
        homework_status = homework['status']
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    else:
        logger.debug('статус работы не изменился')
        return 'статус проверки работы не изменился'


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
                     + emojis.encode(':smile:'))
        while True:
            try:
                logger.debug('Запуск')
                current_timestamp = int(time.time())
                two_month = 2592000
                response = get_api_answer(current_timestamp - two_month)
                homework = check_response(response)
                send_message(bot, parse_status(homework))
                time.sleep(RETRY_TIME)
            except Exception as error:
                message = (f'Сбой в работе программы: {error} '
                           + emojis.encode(':sob:'))
                send_message(bot, message)
                time.sleep(RETRY_TIME)
    else:
        logger.critical('Ошибка, проверьте токены в .env')


if __name__ == '__main__':
    main()
