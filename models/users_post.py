from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, String, DateTime
from .database import db


class Post(db.Model):
    __tablename__ = 'posts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    date_posted: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='posts')
