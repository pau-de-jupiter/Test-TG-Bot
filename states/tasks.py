

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
        CHANGE_TASK_NAME (str): Состояние для изменения имени задачи.
        CHANGE_TASK_DESCRIPTION (str): Состояние для изменения описания задачи.
        DICT_WITH_TASK_FIELDS (dict): Словарь, связывающий названия полей задачи с состояниями их изменения.
            - "name": Состояние изменения имени задачи.
            - "description": Состояние изменения описания задачи.
    """
    CREATE_TASK_STAGE = {
        "waiting_for_name": "Enter the name of the task:",
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

    CHANGE_TASK_NAME = "change_task_name"
    CHANGE_TASK_DESCRIPTION = "change_task_description"
    DICT_WITH_TASK_FIELDS = {
        "name": CHANGE_TASK_NAME,
        "description": CHANGE_TASK_DESCRIPTION,
    }