# Telegram бот-ассистент

## Что делает бот
* раз в 10 минут опрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы
* при обновлении статуса анализирует ответ API и отправляет вам соответствующее уведомление в Telegram
* логирует свою работу и сообщает о важных проблемах сообщением в Telegram

## Функции
* **Функция main()**: в ней описана основная логика работы программы. Все остальные функции должны запускаться из неё. Последовательность действий должна быть примерно такой:
    * Сделать запрос к API.
    * Проверить ответ.
    * Если есть обновления — получить статус работы из обновления и отправить сообщение в Telegram.
    * Подождать некоторое время и сделать новый запрос.
* **Функция check_tokens()** проверяет доступность переменных окружения, которые необходимы для работы программы. Если отсутствует хотя бы одна переменная окружения — функция должна вернуть False, иначе — True.
* **Функция get_api_answer()** делает запрос к единственному эндпоинту API-сервиса. В качестве параметра функция получает временную метку. В случае успешного запроса должна вернуть ответ API, преобразовав его из формата JSON к типам данных Python.
* **Функция check_response()** проверяет ответ API на корректность. В качестве параметра функция получает ответ API, приведенный к типам данных Python. Если ответ API соответствует ожиданиям, то функция должна вернуть список домашних работ (он может быть и пустым), доступный в ответе API по ключу 'homeworks'.
* **Функция parse_status()** извлекает из информации о конкретной домашней работе статус этой работы. В качестве параметра функция получает только один элемент из списка домашних работ. В случае успеха, функция возвращает подготовленную для отправки в Telegram строку, содержащую один из вердиктов словаря HOMEWORK_STATUSES.
* **Функция send_message()** отправляет сообщение в Telegram чат, определяемый переменной окружения TELEGRAM_CHAT_ID. Принимает на вход два параметра: экземпляр класса Bot и строку с текстом сообщения.

## Примеры логирования
```
2022-05-02 20:46:37,958 CRITICAL Отсутствуют обязательные переменные окружения во время запуска бота
2022-05-02 20:46:38,202 ERROR Недокументированный статус домашней работы обнаружен в ответе API
```
