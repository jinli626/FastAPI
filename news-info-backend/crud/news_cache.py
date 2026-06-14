from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cache.news_cache_redis import get_cache_categories, set_cache_categories, get_cache_news_list, set_cache_news_list
from models.news import Category, News
from schemas.base import NewsItemBase


async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    cache_categories = await get_cache_categories()
    if cache_categories:
        return cache_categories

    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories = result.scalars().all()

    if categories:
        categories = jsonable_encoder(categories)
        await set_cache_categories(categories)

    return categories


async def get_news_list(db: AsyncSession, category_id: int, skip: int = 0, limit: int = 100):
    page = skip // limit + 1
    cache_list = await get_cache_news_list(category_id, page, limit)
    if cache_list:
        return [News(**item) for item in cache_list]

    stmt = select(News).where(
        News.category_id == category_id, News.status == 'published'
    ).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list = result.scalars().all()

    if news_list:
        news_data = [NewsItemBase.model_validate(item).model_dump(mode="json", by_alias=False) for item in news_list]
        await set_cache_news_list(category_id, page, limit, news_data)

    return news_list
