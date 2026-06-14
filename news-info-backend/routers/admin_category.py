from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status as http_status

from cache.news_cache_redis import invalidate_categories_cache
from config.db_conf import get_db
from crud import category as category_crud
from models.admin import Admin
from schemas.category import CategoryCreateRequest, CategoryUpdateRequest, CategoryAdminItem
from utils.auth import get_current_admin
from utils.response import success_response

router = APIRouter(prefix="/api/admin/categories", tags=["admin-category"])


@router.get("")
async def get_categories(
    _admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    categories = await category_crud.get_all_categories(db)
    counts = await category_crud.get_news_counts_by_category(db)
    items = []
    for c in categories:
        item = CategoryAdminItem.model_validate(c)
        item.news_count = counts.get(c.id, 0)
        items.append(item)
    return success_response(message="获取分类列表成功", data=items)


@router.post("")
async def create_category(
    data: CategoryCreateRequest,
    _admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    if await category_crud.get_category_by_name(db, data.name):
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail="分类名称已存在")
    category = await category_crud.create_category(db, data)
    await invalidate_categories_cache()
    return success_response(message="分类创建成功", data=CategoryAdminItem.model_validate(category))


@router.put("/{category_id}")
async def update_category(
    category_id: int,
    data: CategoryUpdateRequest,
    _admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    if not await category_crud.get_category_by_id(db, category_id):
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="分类不存在")
    # 改名时校验名称是否与其它分类重复
    if data.name is not None:
        same_name = await category_crud.get_category_by_name(db, data.name)
        if same_name and same_name.id != category_id:
            raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail="分类名称已存在")
    category = await category_crud.update_category(db, category_id, data)
    await invalidate_categories_cache()
    return success_response(message="分类更新成功", data=CategoryAdminItem.model_validate(category))


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    _admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    if not await category_crud.get_category_by_id(db, category_id):
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="分类不存在")
    news_count = await category_crud.count_news_in_category(db, category_id)
    if news_count > 0:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"该分类下还有 {news_count} 条新闻，请先移除或改归类后再删除"
        )
    await category_crud.delete_category(db, category_id)
    await invalidate_categories_cache()
    return success_response(message="分类删除成功")
