

def chunk_tasks(tasks, chunk_size):
    """Разбивает список задач на группы фиксированного размера."""
    return [tasks[i:i + chunk_size] for i in range(0, len(tasks), chunk_size)]


class TaskValidator:
    """Класс для проверки ограничений на поля задачи"""
    FIELD_CONSTRAINTS = {
        "name": {"max_length": 50, "error_msg": "Task name is too long. The allowed number of characters - 50"},
    }

    @classmethod
    def validate(cls, field: str, value: str) -> tuple[bool, str | None]:
        """Проверяет переданное значение на соответствие ограничениям.
        Возвращает кортеж (успешность проверки, сообщение об ошибке).
        """
        constraints = cls.FIELD_CONSTRAINTS.get(field)
        if constraints:
            max_length = constraints.get("max_length")
            if max_length and len(value) > max_length:
                return False, constraints["error_msg"]
        return True, None
