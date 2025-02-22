
from sqlalchemy import Column, Integer, String, BigInteger, TIMESTAMP, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    """Модель для представления пользователей в базе данных."""
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False)
    tg_user_id = Column(BigInteger, unique=True, nullable=False)
    status = Column(String(10), nullable=False, default="Active")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
