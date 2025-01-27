
from sqlalchemy import Column, Integer, String, BigInteger, TIMESTAMP, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False)
    tg_user_id = Column(BigInteger, unique=True, nullable=False)
    status = Column(String(6), nullable=False, default="PROG")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
