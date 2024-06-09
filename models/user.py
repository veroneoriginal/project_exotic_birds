from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, func
from .database import db


class User(db.Model, UserMixin):
    # Этот класс представляет пользователя моего сайта
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=False, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    date_of_registration: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    posts = relationship('Post', back_populates='user')
