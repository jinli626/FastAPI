from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, ConfigDict

from schemas.base import NewsItemBase


class FavoriteCheckResponse(BaseModel):
    isFavorite: bool = Field(..., description="是否收藏", alias='isFavorite')


class FavoriteAddRequest(BaseModel):
    news_id: int = Field(..., description="新闻ID", alias='newsId')
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class FavoriteNewsItemResponse(NewsItemBase):
    favorite_id: int = Field(..., description="收藏ID", alias='favoriteId')
    favorite_time: datetime = Field(..., description="收藏时间", alias='favoriteTime')
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class FavoriteListResponse(BaseModel):
    list: List[FavoriteNewsItemResponse] = Field(..., description="收藏列表", alias='list')
    total: int = Field(..., description="收藏总数", alias='total')
    has_more: bool = Field(..., description="是否有更多数据", alias='hasMore')
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
