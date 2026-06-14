from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status as http_status

from cache.news_cache_redis import invalidate_news_list_cache
from config.db_conf import get_db
from crud import news as news_crud
from models.admin import Admin
from schemas.news_admin import (
    NEWS_STATUS,
    NewsCreateRequest,
    NewsUpdateRequest,
    NewsStatusUpdateRequest,
    NewsAdminListItem,
    NewsAdminDetail,
)
from utils.auth import get_current_admin
from utils.response import success_response

router = APIRouter(prefix="/api/admin/news", tags=["admin-news"])


def _check_status(value: str):
    if value not in NEWS_STATUS:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"非法的状态值，仅支持：{', '.join(NEWS_STATUS)}"
        )


@router.get("/list")
async def get_news_list(
    page: int = 1,
    page_size: int = Query(10, alias="pageSize", le=100),
    category_id: int | None = Query(None, alias="categoryId"),
    keyword: str | None = None,
    status: str | None = None,
    _admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size
    rows = await news_crud.get_news_admin_list(db, category_id, keyword, status, offset, page_size)
    total = await news_crud.get_news_admin_count(db, category_id, keyword, status)
    items = [NewsAdminListItem.model_validate(n) for n in rows]
    return success_response(message="获取新闻列表成功", data={"list": items, "total": total})


@router.get("/detail")
async def get_news_detail(
    news_id: int = Query(..., alias="id"),
    _admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    news = await news_crud.get_news_detail(db, news_id)
    if not news:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="新闻不存在")
    return success_response(data=NewsAdminDetail.model_validate(news))


@router.post("")
async def create_news(
    data: NewsCreateRequest,
    _admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    _check_status(data.status)
    news = await news_crud.create_news(db, data)
    await invalidate_news_list_cache(news.category_id)
    return success_response(message="新闻创建成功", data=NewsAdminDetail.model_validate(news))


@router.put("/{news_id}")
async def update_news(
    news_id: int,
    data: NewsUpdateRequest,
    _admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    if data.status is not None:
        _check_status(data.status)
    existing = await news_crud.get_news_detail(db, news_id)
    if not existing:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="新闻不存在")
    old_category_id = existing.category_id

    updated = await news_crud.update_news(db, news_id, data)
    # 旧分类与新分类的列表缓存都要失效
    await invalidate_news_list_cache(old_category_id)
    if updated.category_id != old_category_id:
        await invalidate_news_list_cache(updated.category_id)
    return success_response(message="新闻更新成功", data=NewsAdminDetail.model_validate(updated))


@router.patch("/{news_id}/status")
async def update_news_status(
    news_id: int,
    data: NewsStatusUpdateRequest,
    _admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    _check_status(data.status)
    updated = await news_crud.update_news_status(db, news_id, data.status)
    if not updated:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="新闻不存在")
    await invalidate_news_list_cache(updated.category_id)
    return success_response(message="状态更新成功", data=NewsAdminDetail.model_validate(updated))


@router.delete("/{news_id}")
async def delete_news(
    news_id: int,
    _admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    category_id = await news_crud.delete_news(db, news_id)
    if category_id is None:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="新闻不存在")
    await invalidate_news_list_cache(category_id)
    return success_response(message="新闻删除成功")
