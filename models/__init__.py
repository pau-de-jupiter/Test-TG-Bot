
from .users import User
from .tasks import Task

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

__all__ = ["User", "Task"]
