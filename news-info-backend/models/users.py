from datetime import datetime
from typing import Optional

from sqlalchemy import Index, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class User(Base):
    __tablename__ = "user"

    __table__args = (
        Index('username_UNIQUE', 'username'),
        Index('phone_UNIQUE', 'phone'),
        Index('email_UNIQUE', 'email'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='用户ID')
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment='用户名')
    password: Mapped[str] = mapped_column(String(255), comment='密码（加密存储）')
    phone: Mapped[str] = mapped_column(String(20), unique=True, comment='手机号')
    email: Mapped[str] = mapped_column(String(100), unique=True, comment='邮箱')
    gender: Mapped[str] = mapped_column(Enum('male', 'female', 'unknown'), comment='性别', default='unknown')
    bio: Mapped[str] = mapped_column(String(500), comment='个人简介', default='空空如也~')
    avatar: Mapped[str] = mapped_column(String(255), comment='头像URL',
                                        default='https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg')
    nickname: Mapped[Optional[str]] = mapped_column(String(50), comment='昵称')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment='创建时间')
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now,
                                                 comment='更新时间')


class UserToken(Base):
    __tablename__ = "user_token"

    __table_args__ = (
        Index('token_UNIQUE', 'token'),
        Index('fk_user_token_user_idx', 'user_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='令牌ID')
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), comment='用户ID', nullable=False)
    token: Mapped[Optional[str]] = mapped_column(String(255), comment='令牌值', nullable=False, unique=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, comment='过期时间', nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment='创建时间')
