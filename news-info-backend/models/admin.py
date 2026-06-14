from datetime import datetime
from typing import Optional

from sqlalchemy import Index, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Admin(Base):
    __tablename__ = "admin"

    __table_args__ = (
        Index('admin_username_UNIQUE', 'username'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='管理员ID')
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment='管理员账号')
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment='密码（加密存储）')
    nickname: Mapped[Optional[str]] = mapped_column(String(50), comment='昵称')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment='创建时间')
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now,
                                                 comment='更新时间')


class AdminToken(Base):
    __tablename__ = "admin_token"

    __table_args__ = (
        Index('admin_token_UNIQUE', 'token'),
        Index('fk_admin_token_admin_idx', 'admin_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='令牌ID')
    admin_id: Mapped[int] = mapped_column(Integer, ForeignKey('admin.id'), comment='管理员ID', nullable=False)
    token: Mapped[Optional[str]] = mapped_column(String(255), comment='令牌值', nullable=False, unique=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, comment='过期时间', nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment='创建时间')
