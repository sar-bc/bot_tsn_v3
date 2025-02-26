from sqlalchemy import (ForeignKey, String, BigInteger,
                        TIMESTAMP, Column, func, Integer,
                        Text, CheckConstraint, Date, DateTime, Boolean, JSON)
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass

####################################

class UserState(Base):
    __tablename__ = 'UserState'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    last_message_ids = Column(JSON, default=list)  # Поддержка JSON
    kv = Column(Integer, default=0)
    ls = Column(Integer, default=0)
    home = Column(Integer, default=0)

    def __repr__(self):
        return (f"<UserState(id={self.id}, user_id={self.user_id}, "
                f"last_message_ids={self.last_message_ids}, "
                f"kv={self.kv}, ls={self.ls}, home={self.home})>")

####################################


class Logs(Base):
    __tablename__ = 'Logs'  # Имя таблицы в базе данных

    id = Column(Integer, primary_key=True, autoincrement=True)  # Уникальный идентификатор
    timestamp = Column(DateTime, nullable=False)  # Временная метка
    name = Column(Text, nullable=False)  # Имя логгера
    level = Column(Text, nullable=False)  # Уровень логирования
    message = Column(Text, nullable=False)  # Сообщение лога

    def __repr__(self):
        return (f"<Log(id={self.id}, timestamp='{self.timestamp}', "
                f"name='{self.name}', level='{self.level}', "
                f"message='{self.message}')>")

