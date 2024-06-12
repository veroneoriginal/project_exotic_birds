from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, String, DateTime, Boolean, Table
from .database import db


# Таблица связи между постами и тегами
class PostTag(db.Model):
    __tablename__ = 'post_tags'
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey('posts.id'), primary_key=True)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey('tags.id'), primary_key=True)


class Post(db.Model):
    __tablename__ = 'posts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    date_posted: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='posts')
    tags = relationship('Tag', secondary='post_tags', back_populates='posts')


class Tag(db.Model):
    __tablename__ = 'tags'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    posts = relationship('Post', secondary='post_tags', back_populates='tags')
