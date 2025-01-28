

def chunk_tasks(tasks, chunk_size):
    """Разбивает список задач на группы фиксированного размера."""
    return [tasks[i:i + chunk_size] for i in range(0, len(tasks), chunk_size)]
