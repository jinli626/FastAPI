from pydantic import BaseModel, Field, ConfigDict

from schemas.base import NewsItemBase


class HistoryAddRequest(BaseModel):
    news_id: int = Field(..., description="新闻ID", alias='newsId')
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class HistoryNewsItemResponse(NewsItemBase):
    history_id: int = Field(..., description="收藏ID", alias='historyId')
    view_time: int = Field(..., description="查看时间", alias='viewTime')
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class HistoryListResponse(BaseModel):
    list: list[HistoryNewsItemResponse]
    total: int
    has_more: bool = Field(alias='hasMore')
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
