from enum import Enum


class ErrorMessages(Enum):
    """Error messages."""

    USER_ALREADY_REGISTERED: str = (
        "Пользователь с таким email уже зарегистрирован!"
    )
    INVALID_EMAIL: str = "Пользователя с таким email не существует!"
    NOT_REAL_EMAIL: str = "Некорректный email!"
    INVALID_DATA: str = "Пользователь с такими данными не зарегистрирован!"

    PASSWORDS_DO_NOT_MATCH: str = "Пароли не совпадают!"

    INVALID_TOKEN: str = "Неверный токен!"
    BAD_CREDENTIALS: str = "Не удалось подтвердить учетные данные!"


class SuccessMessages(Enum):
    """Success messages."""

    SUCCESS_SENT_EMAIL: str = "Email успешно отправлен!"
    SUCCESS_RESET_PASSWORD: str = "Пароль изменен!"
    SUCCESS_CREATED_USER: str = "Пользователь создан!"
