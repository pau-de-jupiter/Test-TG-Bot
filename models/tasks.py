
from sqlalchemy import Column, Integer, String, Text, BigInteger, TIMESTAMP, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Task(Base):
    """Модель для представления задач в базе данных."""
    __tablename__ = "Tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    tg_user_id = Column(BigInteger, nullable=False)
    status = Column(String(6), nullable=False, default="PROG")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    last_update = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"), onupdate=text("now()"))
