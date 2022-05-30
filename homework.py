import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv
from telegram import TelegramError

from exception import (SendMessageError,
                       ResponseCodeError,
                       ApiResponseError,
                       NotSendsError,
                       ResponseTypeError,
                       ResponseContentError)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM')
TELEGRAM_TOKEN = os.getenv('TELEGRAM')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHATID')
TWO_MONTH = 2592000

homework_status = None

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)


def send_message(bot, message):
    """Отправка ботом сообщений в чат."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except TelegramError:
        logger.error(sys.exc_info())
        raise SendMessageError(
            f'не удалось отправить сообщение: "{message}", {sys.exc_info()}')
    else:
        logger.info('сообщение успешно отправлено')


def get_api_answer(current_timestamp):
    """получаем ответ с API домашки."""
    params = {'from_date': current_timestamp}
    url = ENDPOINT
    try:
        logger.info(f'Начат запрос по адресу {url} '
                    f'с прамаметрами headers={HEADERS}, params={params}')
        homework_statuses = requests.get(
            url=url,
            headers=HEADERS,
            params=params,
        )
        if homework_statuses.status_code != HTTPStatus.OK:
            raise ResponseCodeError(
                f'Ошибка: Ожидался код 200, а получен: '
                f'{homework_statuses.status_code}!')
    except Exception:
        raise ApiResponseError(f'Адрес {ENDPOINT} недоступен!')
    else:
        return homework_statuses.json()


def check_response(response):
    """проверяем наличии в респонсе словаря homeworks."""
    logger.info(f'Начинаю проверку ответа сервера({response})')
    if not isinstance(response, dict):
        raise ResponseTypeError(f'Ошибка: в reponse ожидается словарь, '
                                f'а вернулось - {type(response)}')
    if 'homework_status' and 'current_date' not in response:
        raise ResponseContentError(
            f"В response ожидается 'homework_status' и 'current_date', "
            f"вернулось: 'homework_status'={response['homework_status']}, "
            f"current_date={response['current_date']}")
    homework = response['homeworks']
    if not isinstance(homework, list):
        raise ResponseContentError(
            f'в респонсе содержится не list: type(homework)={type(homework)}')
    return homework


def parse_status(homework):
    """парсим данные с ответа яндекс.домашка."""
    global homework_status
    if 'homework_name' not in homework:
        logger.error('ключа "homework_name" нет в homework')
        raise KeyError('ключа "homework_name" нет в homework')
    else:
        homework_name = homework['homework_name']
    if homework['status'] not in HOMEWORK_VERDICTS:
        logger.error('такой статус проверки не известен')
        raise KeyError(f"статуса {homework['status']} нет в HOMEWORK_STATUSES")
    if homework_status != homework['status']:
        homework_status = homework['status']
        verdict = HOMEWORK_VERDICTS[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    else:
        logger.debug('статус работы не изменился')
        return 'статус проверки работы не изменился'


def check_tokens():
    """проверяем доступность переменных окружения."""
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
                     'Начинаю запрашивать информацию о статусе домашки ')
        while True:
            try:
                logger.debug('Запуск')
                current_timestamp = int(time.time())
                response = get_api_answer(current_timestamp - TWO_MONTH)
                homework = check_response(response)
                send_message(bot, parse_status(homework))
                time.sleep(RETRY_TIME)
            except NotSendsError as error:
                logger.error(error)
            # except ResponseCodeError as error:
            #     logger.error(error)
            except Exception as error:
                message = f'Сбой в работе программы: {error}'
                logger.error(error)
                send_message(bot, message)
                time.sleep(RETRY_TIME)
            # except ServerError:
            #     logger.info('ошибка: ')
            else:   # если не возникло исключений
                pass

    else:
        logger.critical('Ошибка, проверьте токены в .env')


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
