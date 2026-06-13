from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import history
from models.users import User
from schemas.history import HistoryAddRequest, HistoryNewsItemResponse, HistoryListResponse
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/history", tags=["history"])


@router.post("/add")
async def add_history(
    data: HistoryAddRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await history.add_history(db, user.id, data.news_id)
    return success_response(message="添加历史记录成功", data=result)


@router.get("/list")
async def get_history_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    rows, total = await history.get_history_list(db, user.id, page, page_size)
    has_more = total > page * page_size
    history_list = [HistoryNewsItemResponse(
        id=news.id,
        title=news.title,
        description=news.description,
        image=news.image,
        author=news.author,
        views=news.views,
        history_id=history_id,
        view_time=view_time,
        category_id=news.category_id,
        publish_time=news.publish_time,
    ) for news, view_time, history_id in rows]
    data = HistoryListResponse(
        list=history_list,
        total=total,
        has_more=has_more,
    )
    return success_response(data=data)


@router.delete("/delete/{history_id}")
async def delete_history(
    history_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await history.delete_history(db, user.id, history_id)
    if not result:
        raise HTTPException(status_code=404, detail="历史记录不存在")
    return success_response(message="删除历史记录成功")


@router.delete("/clear")
async def clear_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await history.clear_history(db, user.id)
    if not result:
        raise HTTPException(status_code=404, detail="历史记录不存在")
    return success_response(message="清空历史记录成功")
