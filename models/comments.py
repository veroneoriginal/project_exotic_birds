from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, String, DateTime
from .database import db
from .user import User
from .post_and_tags import Post


class Comment(db.Model):
    __tablename__ = 'comments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(String, nullable=False)
    date_posted: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey('posts.id'), nullable=False)
    parent_comment_id: Mapped[int] = mapped_column(Integer, ForeignKey('comments.id'), nullable=True)

    user = relationship('User', back_populates='comments')
    post = relationship('Post', back_populates='comments')
    # replies устанавливает связь "один ко многим" между комментарием и его дочерними комментариями
    replies = relationship('Comment', back_populates='parent_comment', remote_side=[id])


# избегаем циклического импорта
User.comments = relationship('Comment', back_populates='user')
Post.comments = relationship('Comment', back_populates='post')
# parent_comment устанавливает обратную связь - каждый коммент может ссылаться на свой родительский коммент
Comment.parent_comment = relationship('Comment', back_populates='replies', remote_side=[id])
