from datetime import datetime

from sqlalchemy import Index, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class History(Base):
    __tablename__ = 'history'

    __table_args__ = (
        Index('fx_history_user_idx', 'user_id'),
        Index('fx_history_news_idx', 'news_id'),
        Index('idx_view_time', 'view_time')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='历史记录ID')
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False, comment='用户ID')
    news_id: Mapped[int] = mapped_column(Integer, ForeignKey('news.id'), nullable=False, comment='新闻ID')
    view_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, comment='浏览时间')
