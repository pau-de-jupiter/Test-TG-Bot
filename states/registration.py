
class RegistrationState:
    """
    Класс, представляющий возможные состояния процесса регистрации пользователя.
    Атрибуты:
        WAITING_FOR_USERNAME (str): Состояние, при котором ожидается ввод имени пользователя.
        WAITING_FOR_LOGIN (str): Состояние, при котором ожидается ввод логина пользователя.
    """
    WAITING_FOR_USERNAME = "waiting_for_username"
    WAITING_FOR_LOGIN = "waiting_for_login"