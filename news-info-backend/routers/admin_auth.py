from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from crud import admin as admin_crud
from models.admin import Admin
from schemas.admin import (
    AdminLoginRequest,
    AdminAuthResponse,
    AdminInfoResponse,
    AdminChangePasswordRequest,
)
from utils.auth import get_current_admin
from utils.response import success_response

router = APIRouter(prefix="/api/admin", tags=["admin-auth"])


@router.post("/login")
async def login(login_data: AdminLoginRequest, db: AsyncSession = Depends(get_db)):
    admin = await admin_crud.authenticate_admin(db, login_data.username, login_data.password)
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号或密码错误")
    token = await admin_crud.create_admin_token(db, admin.id)
    response_data = AdminAuthResponse(token=token, admin_info=AdminInfoResponse.model_validate(admin))
    return success_response(message="登录成功", data=response_data)


@router.get("/info")
async def get_admin_info(admin: Admin = Depends(get_current_admin)):
    return success_response(message="获取管理员信息成功", data=AdminInfoResponse.model_validate(admin))


@router.put("/password")
async def change_password(
    data: AdminChangePasswordRequest,
    admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    ok = await admin_crud.change_admin_password(db, admin, data.old_password, data.new_password)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="原密码不正确")
    return success_response(message="密码修改成功")
