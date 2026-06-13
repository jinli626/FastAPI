from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.news import News


async def get_news_detail(db: AsyncSession, news_id: int):
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_news_count(db: AsyncSession, category_id: int):
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()


async def increase_news_views(db: AsyncSession, news_id: int):
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def get_related_news(db: AsyncSession, news_id: int, category_id: int, limit: int = 5):
    stmt = select(News).where(
        News.category_id == category_id,
        News.id != news_id
    ).order_by(News.views.desc(), News.publish_time.desc()).limit(limit)
    result = await db.execute(stmt)
    related_news = result.scalars().all()
    return [{
        "id": n.id,
        "title": n.title,
        "content": n.content,
        "publishTime": n.publish_time,
        "views": n.views,
        "image": n.image,
        "author": n.author,
        "categoryId": n.category_id,
    } for n in related_news]
