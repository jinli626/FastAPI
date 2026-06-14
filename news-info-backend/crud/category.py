from sqlalchemy import select, func, update

from sqlalchemy.ext.asyncio import AsyncSession

from models.news import Category, News
from schemas.category import CategoryCreateRequest, CategoryUpdateRequest


async def get_all_categories(db: AsyncSession):
    stmt = select(Category).order_by(Category.sort_order.asc(), Category.id.asc())
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_category_by_id(db: AsyncSession, category_id: int):
    stmt = select(Category).where(Category.id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_category_by_name(db: AsyncSession, name: str):
    stmt = select(Category).where(Category.name == name)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def count_news_in_category(db: AsyncSession, category_id: int):
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()


async def get_news_counts_by_category(db: AsyncSession):
    stmt = select(News.category_id, func.count(News.id)).group_by(News.category_id)
    result = await db.execute(stmt)
    return {row[0]: row[1] for row in result.all()}


async def create_category(db: AsyncSession, data: CategoryCreateRequest):
    category = Category(name=data.name, sort_order=data.sort_order)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def update_category(db: AsyncSession, category_id: int, data: CategoryUpdateRequest):
    values = data.model_dump(by_alias=False, exclude_unset=True)
    if not values:
        return await get_category_by_id(db, category_id)
    stmt = update(Category).where(Category.id == category_id).values(**values)
    result = await db.execute(stmt)
    await db.commit()
    if result.rowcount == 0:
        return None
    return await get_category_by_id(db, category_id)


async def delete_category(db: AsyncSession, category_id: int):
    category = await get_category_by_id(db, category_id)
    if not category:
        return None
    await db.delete(category)
    await db.commit()
    return True
