from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data.models import Base

engine = create_engine("sqlite:///cashbrain.db", echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Создаёт таблицы, если их ещё нет."""
    Base.metadata.create_all(engine)


def get_session():
    """Возвращает новую сессию для работы с БД."""
    return SessionLocal()