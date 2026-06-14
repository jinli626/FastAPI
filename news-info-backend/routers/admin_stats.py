from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import stats as stats_crud
from models.admin import Admin
from utils.auth import get_current_admin
from utils.response import success_response

router = APIRouter(prefix="/api/admin/stats", tags=["admin-stats"])


@router.get("/overview")
async def overview(
    _admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    data = await stats_crud.get_overview(db)
    return success_response(message="获取概览成功", data=data)


@router.get("/category-distribution")
async def category_distribution(
    _admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    data = await stats_crud.get_category_distribution(db)
    return success_response(message="获取分类分布成功", data=data)


@router.get("/hot-news")
async def hot_news(
    limit: int = Query(10, le=50),
    _admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    data = await stats_crud.get_hot_news(db, limit)
    return success_response(message="获取热门新闻成功", data=data)
