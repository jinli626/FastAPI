from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, DateTime, Index, Text, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Category(Base):
    __tablename__ = 'news_category'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='分类ID')
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, comment='分类名称')
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment='排序顺序')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment='创建时间')
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now,
                                                 comment='更新时间')


class News(Base):
    __tablename__ = 'news'

    __table_args__ = (
        Index('fk_news_category_idx', 'category_id'),
        Index('idx_publish_time', 'publish_time')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='新闻ID')
    title: Mapped[str] = mapped_column(String(255), comment='新闻标题')
    description: Mapped[str] = mapped_column(String(255), comment='新闻简介')
    content: Mapped[str] = mapped_column(Text, comment='新闻内容', nullable=False)
    image: Mapped[Optional[str]] = mapped_column(String(255), comment='封面图片URL')
    author: Mapped[Optional[str]] = mapped_column(String(255), comment='作者')
    views: Mapped[int] = mapped_column(Integer, comment='浏览量', default=0, nullable=False)
    status: Mapped[str] = mapped_column(Enum('draft', 'published', 'offline'), comment='状态：草稿/已发布/已下架',
                                        default='published', nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('news_category.id'), comment='分类ID', nullable=False)
    publish_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment='发布时间')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment='创建时间')
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now,
                                                 comment='更新时间')
