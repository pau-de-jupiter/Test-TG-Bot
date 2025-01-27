

class TaskState:
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
    CHANGE_TASK_STEP = [
        CHANGE_TASK_DATA,
        CHANGE_DETAIL_TASK,
    ]