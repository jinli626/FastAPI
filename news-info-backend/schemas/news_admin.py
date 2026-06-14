from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

# 允许的新闻状态
NEWS_STATUS = ('draft', 'published', 'offline')


class NewsCreateRequest(BaseModel):
    title: str = Field(..., max_length=255, description='新闻标题')
    description: str = Field(..., max_length=255, description='新闻简介')
    content: str = Field(..., description='新闻正文（HTML）')
    image: Optional[str] = Field(None, max_length=255, description='封面图片URL')
    author: Optional[str] = Field(None, max_length=255, description='作者')
    category_id: int = Field(..., alias='categoryId', description='分类ID')
    status: str = Field('draft', description='状态：draft/published/offline')
    publish_time: Optional[datetime] = Field(None, alias='publishTime', description='发布时间，留空则取当前时间')

    model_config = ConfigDict(populate_by_name=True)


class NewsUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=255, description='新闻标题')
    description: Optional[str] = Field(None, max_length=255, description='新闻简介')
    content: Optional[str] = Field(None, description='新闻正文（HTML）')
    image: Optional[str] = Field(None, max_length=255, description='封面图片URL')
    author: Optional[str] = Field(None, max_length=255, description='作者')
    category_id: Optional[int] = Field(None, alias='categoryId', description='分类ID')
    status: Optional[str] = Field(None, description='状态：draft/published/offline')
    publish_time: Optional[datetime] = Field(None, alias='publishTime', description='发布时间')

    model_config = ConfigDict(populate_by_name=True)


class NewsStatusUpdateRequest(BaseModel):
    status: str = Field(..., description='状态：draft/published/offline')


class NewsAdminListItem(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    image: Optional[str] = None
    author: Optional[str] = None
    views: int
    status: str
    category_id: int = Field(alias='categoryId')
    publish_time: Optional[datetime] = Field(None, alias='publishTime')
    created_at: Optional[datetime] = Field(None, alias='createdAt')
    updated_at: Optional[datetime] = Field(None, alias='updatedAt')

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class NewsAdminDetail(NewsAdminListItem):
    content: Optional[str] = None
