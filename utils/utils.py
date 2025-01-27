

def chunk_tasks(tasks, chunk_size):
    """Splits the task list into groups of fixed size."""
    return [tasks[i:i + chunk_size] for i in range(0, len(tasks), chunk_size)]
