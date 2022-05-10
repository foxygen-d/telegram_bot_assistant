import json
import logging
import os
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup

from exceptions import Error404, MissingVariables, ApiResponseIsEmpty


logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    filemode='a',
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        button = ReplyKeyboardMarkup([['/check_my_homework']],
                                     resize_keyboard=True)

        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            reply_markup=button,
        )
        logger.info('Удачная отправка сообщения в Telegram')

    except telegram.TelegramError:
        logger.error('Сбой при отправке сообщения в Telegram')


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    timestamp = current_timestamp
    params = {'from_date': timestamp}
    try:
        homework_info = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except requests.exceptions.ConnectionError as e:
        logger.error('Проблемы с подключением, попробуйте ещё раз')
        raise SystemExit(e)
    except requests.exceptions.HTTPError as e:
        logger.error('Недопустимый HTTP-ответ')
        raise SystemExit(e)
    except requests.exceptions.Timeout as e:
        logger.error('Время ожидания ответа от сервера превысило лимит')
        raise SystemExit(e)
    except requests.exceptions.TooManyRedirects as e:
        logger.error('URL-адрес неправильный, попробуйте другой')
        raise SystemExit(e)

    if homework_info.status_code != HTTPStatus.OK:
        raise Error404

    try:
        return homework_info.json()

    except json.decoder.JSONDecodeError:
        logger.error('Это не JSON')


def check_response(response):
    """Проверяет ответ API на корректность."""
    if type(response) is not dict:
        logger.error('API не соответствует ожиданиям')
        raise TypeError('API не соответствует ожиданиям')
    if not response:
        raise ApiResponseIsEmpty
    if 'homeworks' not in response:
        raise KeyError('Отсутствует ожидаемый ключ в ответе API')
    if type(response.get('homeworks')) is not list:
        raise TypeError('API не соответствует ожиданиям')
    return response.get('homeworks')


def parse_status(homework):
    """Извлекает из информации статус домашней работы."""
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
    except KeyError:
        logger.error('Обращение происходит по несуществующему ключу')
        raise KeyError('Обращение происходит по несуществующему ключу')

    try:
        verdict = HOMEWORK_STATUSES[homework_status]
    except KeyError:
        logger.debug('Недокументированный статус домашней '
                     'работы обнаружен в ответе API')
        raise KeyError('Недокументированный статус домашней '
                       'работы обнаружен в ответе API')

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        return True
    return False


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            if not check_tokens():
                logger.critical('Отсутствуют обязательные переменные '
                                'окружения во время запуска бота')
                raise MissingVariables
            response = get_api_answer(current_timestamp)
            response = check_response(response)
            if response:
                message = parse_status(response[0])
            else:
                message = 'У вас пока нет домашних заданий на проверке!'
            send_message(bot, message)
            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
