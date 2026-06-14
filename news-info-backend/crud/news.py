from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.news import News
from schemas.news_admin import NewsCreateRequest, NewsUpdateRequest


async def get_news_detail(db: AsyncSession, news_id: int):
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_news_count(db: AsyncSession, category_id: int):
    # 用户端列表计数：仅统计已发布
    stmt = select(func.count(News.id)).where(
        News.category_id == category_id, News.status == 'published'
    )
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
        News.id != news_id,
        News.status == 'published'
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


# ==================== 管理端：新闻增删改查 ====================

async def get_news_admin_list(db: AsyncSession, category_id: int | None = None,
                              keyword: str | None = None, status: str | None = None,
                              offset: int = 0, limit: int = 10):
    conditions = []
    if category_id is not None:
        conditions.append(News.category_id == category_id)
    if status:
        conditions.append(News.status == status)
    if keyword:
        conditions.append(News.title.like(f"%{keyword}%"))

    stmt = select(News)
    if conditions:
        stmt = stmt.where(*conditions)
    stmt = stmt.order_by(News.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_news_admin_count(db: AsyncSession, category_id: int | None = None,
                               keyword: str | None = None, status: str | None = None):
    conditions = []
    if category_id is not None:
        conditions.append(News.category_id == category_id)
    if status:
        conditions.append(News.status == status)
    if keyword:
        conditions.append(News.title.like(f"%{keyword}%"))

    stmt = select(func.count(News.id))
    if conditions:
        stmt = stmt.where(*conditions)
    result = await db.execute(stmt)
    return result.scalar_one()


async def create_news(db: AsyncSession, data: NewsCreateRequest):
    values = data.model_dump(by_alias=False)
    # publish_time 留空时交给模型默认值（当前时间）
    if values.get('publish_time') is None:
        values.pop('publish_time', None)
    news = News(**values)
    db.add(news)
    await db.commit()
    await db.refresh(news)
    return news


async def update_news(db: AsyncSession, news_id: int, data: NewsUpdateRequest):
    values = data.model_dump(by_alias=False, exclude_unset=True)
    if not values:
        return await get_news_detail(db, news_id)
    stmt = update(News).where(News.id == news_id).values(**values)
    result = await db.execute(stmt)
    await db.commit()
    if result.rowcount == 0:
        return None
    return await get_news_detail(db, news_id)


async def update_news_status(db: AsyncSession, news_id: int, status: str):
    stmt = update(News).where(News.id == news_id).values(status=status)
    result = await db.execute(stmt)
    await db.commit()
    if result.rowcount == 0:
        return None
    return await get_news_detail(db, news_id)


async def delete_news(db: AsyncSession, news_id: int):
    news = await get_news_detail(db, news_id)
    if not news:
        return None
    category_id = news.category_id
    await db.delete(news)
    await db.commit()
    return category_id
