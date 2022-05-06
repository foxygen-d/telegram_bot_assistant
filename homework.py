import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup
from http import HTTPStatus


logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    filemode='a',
    format='%(asctime)s %(levelname)s %(message)s'
)

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
        logging.info('Удачная отправка сообщения в Telegram')

    except Exception:
        logging.error('Сбой при отправке сообщения в Telegram')


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    try:
        timestamp = current_timestamp
        params = {'from_date': timestamp}
        homework_info = requests.get(ENDPOINT, headers=HEADERS, params=params)

    except Exception:
        logging.error('Недоступность эндпоинта')
        raise Exception('Недоступность эндпоинта')

    if homework_info.status_code != HTTPStatus.OK:
        raise Exception('Ошибка status_code')

    return homework_info.json()


def check_response(response):
    """Проверяет ответ API на корректность."""
    if type(response) is not dict:
        logging.error('API не соответствует ожиданиям')
        raise TypeError('API не соответствует ожиданиям')
    if not response:
        raise Exception('Ответ API содержит пустой словарь')
    if 'homeworks' not in response:
        raise Exception('Отсутствует ожидаемый ключ в ответе API')
    if type(response.get('homeworks')) is not list:
        raise Exception('API не соответствует ожиданиям')
    return response.get('homeworks')


def parse_status(homework):
    """
    Извлекает из информации о конкретной
    домашней работе статус этой работы.
    """
    homework_name = homework['homework_name']
    homework_status = homework['status']

    if not HOMEWORK_STATUSES[homework_status]:
        logging.debug('Недокументированный статус домашней '
                      'работы обнаружен в ответе API')
        raise Exception('Недокументированный статус домашней '
                        'работы обнаружен в ответе API')

    verdict = HOMEWORK_STATUSES[homework_status]

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    try:
        if all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
            return True
        raise Exception

    except Exception:
        logging.critical('Отсутствуют обязательные переменные '
                         'окружения во время запуска бота.')


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            check_tokens()
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
