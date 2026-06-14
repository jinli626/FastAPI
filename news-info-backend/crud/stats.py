from datetime import datetime, date, time

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.news import News, Category


async def get_overview(db: AsyncSession):
    # 新闻总数
    news_total = (await db.execute(select(func.count(News.id)))).scalar_one()

    # 各状态数量
    status_rows = (await db.execute(
        select(News.status, func.count(News.id)).group_by(News.status)
    )).all()
    status_map = {row[0]: row[1] for row in status_rows}

    # 分类总数
    category_total = (await db.execute(select(func.count(Category.id)))).scalar_one()

    # 总浏览量
    total_views = (await db.execute(select(func.coalesce(func.sum(News.views), 0)))).scalar_one()

    # 今日新增
    today_start = datetime.combine(date.today(), time.min)
    today_new = (await db.execute(
        select(func.count(News.id)).where(News.created_at >= today_start)
    )).scalar_one()

    return {
        "newsTotal": news_total,
        "publishedTotal": status_map.get("published", 0),
        "draftTotal": status_map.get("draft", 0),
        "offlineTotal": status_map.get("offline", 0),
        "categoryTotal": category_total,
        "totalViews": int(total_views),
        "todayNew": today_new,
    }


async def get_category_distribution(db: AsyncSession):
    stmt = (
        select(Category.id, Category.name, func.count(News.id))
        .outerjoin(News, News.category_id == Category.id)
        .group_by(Category.id, Category.name)
        .order_by(Category.sort_order.asc(), Category.id.asc())
    )
    rows = (await db.execute(stmt)).all()
    return [{"categoryId": r[0], "categoryName": r[1], "count": r[2]} for r in rows]


async def get_hot_news(db: AsyncSession, limit: int = 10):
    stmt = select(News.id, News.title, News.views).order_by(News.views.desc()).limit(limit)
    rows = (await db.execute(stmt)).all()
    return [{"id": r[0], "title": r[1], "views": r[2]} for r in rows]
