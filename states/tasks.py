

class TaskState:
    """
    Класс, представляющий возможные состояния и этапы управления задачами.
    Атрибуты:
        CREATE_TASK_STAGE (dict): Словарь с текстами сообщений для этапов создания задачи.
            - "waiting_for_name": Сообщение для запроса имени задачи.
            - "waiting_for_description": Сообщение для запроса описания задачи.
        WAITING_FOR_NAME (str): Состояние, при котором ожидается ввод имени задачи.
        WAITING_FOR_DESCRIPTION (str): Состояние, при котором ожидается ввод описания задачи.
        CREATE_TASK_STEP (list): Последовательность состояний для создания задачи.
        CHANGE_TASK_DATA (str): Состояние для изменения списка задач.
        CHANGE_DETAIL_TASK (str): Шаблон состояния для изменения деталей задачи с указанием ID задачи.
        CHANGE_TASK_FIELD (str): Состояние для изменения поля задачи (сейчас используется для имени и описания).
    """
    CREATE_TASK_STAGE = {
        "waiting_for_name": "Enter the name of the task (length maximum 50 characters):",
        "waiting_for_description": "Enter a description of the task:"
    }
    WAITING_FOR_NAME = "waiting_for_name"
    WAITING_FOR_DESCRIPTION = "waiting_for_description"
    CREATE_TASK_STEP = [
        WAITING_FOR_NAME,
        WAITING_FOR_DESCRIPTION
    ]
    CHANGE_TASK_DATA = "my_tasks:0"
    CHANGE_DETAIL_TASK = "detail_task:{taskId}"
    CHANGE_TASK_FIELD = "change_task_field"