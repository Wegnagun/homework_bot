"""Бот, который запрашивает статус домашики на API яндекс.домашка."""
import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv
from requests.exceptions import HTTPError
from telegram import TelegramError

from exception import (SendMessageError,
                       ResponseCodeError,
                       ApiResponseError,
                       NotSendsError,
                       ResponseContentError,
                       ResponseContentTypeError)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM')
TELEGRAM_TOKEN = os.getenv('TELEGRAM')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHATID')
RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)


def send_message(bot, message: str):
    """Отправка ботом сообщений в чат."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except TelegramError:
        raise SendMessageError(
            f'не удалось отправить сообщение: "{message}"')
    else:
        logger.info('сообщение успешно отправлено')


def get_api_answer(current_timestamp: int) -> dict:
    """получаем ответ с API домашки."""
    params = dict(url=ENDPOINT,
                  headers=HEADERS,
                  params={'from_date': current_timestamp})
    try:
        logger.info(f'Начат запрос по адресу {ENDPOINT} '
                    f'с парамметрами {params}')
        homework_statuses = requests.get(**params)
        if homework_statuses.status_code != HTTPStatus.OK:
            raise ResponseCodeError(
                f'Ожидался код 200, а получен: '
                f'{homework_statuses.status_code}, '
                f'параметры запроса: {params}!')
    except ResponseCodeError:
        raise
    except Exception:
        raise ApiResponseError(
            f'Адрес {ENDPOINT} недоступен! '
            f'параметры запроса: {params}')

    try:
        homework_statuses.json()
    except HTTPError as error:
        raise ApiResponseError(
            f'неудалось получить json формат: {error}')
    else:
        return homework_statuses.json()


def check_response(response: dict) -> list:
    """проверяем наличие в респонсе словаря homeworks."""
    logger.info(f'Начинаю проверку ответа сервера ({response})')
    if not isinstance(response, dict):
        raise TypeError(f'В {response} ожидается словарь, '
                        f'а вернулось - {type(response)}')
    current_date = response.get('current_date')
    if current_date is None:
        raise ResponseContentError(
            f"В response ожидается 'current_date': "
            f"current_date={current_date}")
    homeworks = response.get('homeworks')
    if homeworks is None:
        raise ResponseContentError(f"В словаре {homeworks} "
                                   f"отсутствует 'homeworks'")
    if not isinstance(homeworks, list):
        raise ResponseContentTypeError(
            f'в "homework" содержится не list: '
            f'type(homework)={type(homeworks)}')
    return homeworks


def parse_status(homework: dict) -> str:
    """парсим данные с ответа сервера."""
    logger.info('Начинаем собирать данные из homework')
    homework_status = homework.get('status')
    homework_name = homework.get('homework_name')
    if homework_name is None:
        raise KeyError(f"ключа 'homework_name' нет в {homework}"
                       f"или вернулось None")
    if homework_status not in HOMEWORK_VERDICTS:
        raise ValueError(f"статуса {homework_status} нет в HOMEWORK_VERDICTS"
                         f"или вернулось None")
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """проверяем доступность переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Ошибка, проверьте токены в .env')
        sys.exit('Ошибка, проверьте токены в .env')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    send_message(bot,
                 'Начинаю запрашивать информацию о статусе работы')
    current_timestamp = int(time.time())
    logger.debug('Запуск')
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework_list = check_response(response)
            if len(homework_list) > 0:
                send_message(bot, parse_status(homework_list[0]))
            current_timestamp = response.get('current_date', current_timestamp)
        except NotSendsError as error:
            logger.error(error, exc_info=True)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message, exc_info=True)
            send_message(bot, message)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    # настройка логирования
    file_handler = logging.FileHandler(
        filename=os.path.join('main.log'))
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [file_handler, stdout_handler]
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=handlers,
        format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
    )
    ###
    main()
