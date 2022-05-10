class Error(Exception):
    """Базовый класс для исключений."""

    pass


class Error404(Error):
    """Исключение ошибки status_code."""

    def __init__(self, message='Ошибка status_code'):
        """Возвращает сообщение исключения Error404."""
        self.message = message
        super().__init__(self.message)


class MissingVariables(Error):
    """Исключение отсутствия обязательных переменных."""

    def __init__(self, message='Отсутствуют обязательные переменные '
                               'окружения во время запуска бота'):
        """Возвращает сообщение исключения MissingVariables."""
        self.message = message
        super().__init__(self.message)


class ApiResponseIsEmpty(Error):
    """Исключение ответа API."""

    def __init__(self, message='Ответ API содержит пустой словарь'):
        """Возвращает сообщение исключения ApiResponseIsEmpty."""
        self.message = message
        super().__init__(self.message)
