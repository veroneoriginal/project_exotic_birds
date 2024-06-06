from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func

from .database import db


class User(db.Model):
    # Этот класс представляет пользователя моего сайта
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    date_of_registration: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
