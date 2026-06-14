from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class CategoryCreateRequest(BaseModel):
    name: str = Field(..., max_length=50, description='分类名称')
    sort_order: int = Field(0, alias='sortOrder', description='排序顺序')

    model_config = ConfigDict(populate_by_name=True)


class CategoryUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=50, description='分类名称')
    sort_order: Optional[int] = Field(None, alias='sortOrder', description='排序顺序')

    model_config = ConfigDict(populate_by_name=True)


class CategoryAdminItem(BaseModel):
    id: int
    name: str
    sort_order: int = Field(alias='sortOrder')
    created_at: Optional[datetime] = Field(None, alias='createdAt')
    updated_at: Optional[datetime] = Field(None, alias='updatedAt')
    news_count: Optional[int] = Field(None, alias='newsCount', description='该分类下新闻数量')

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
