import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from crud import users
from models.users import User
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, UserUpdateRequest, UserChangePasswordRequest
from schemas.verification import SendCodeRequest, VerifyCodeRequest, ResetPasswordRequest
from utils.auth import get_current_user
from utils.captcha import generate_captcha, verify_captcha
from utils.response import success_response
from utils.verification import can_send_code, generate_code, store_verify_code, send_email, send_sms, mark_send_code, \
    verify_code, generate_reset_token_by_contact, get_contact_by_reset_token

router = APIRouter(prefix="/api/user", tags=["users"])


@router.post("/register")
async def register(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    existing_user = await users.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
    user = await users.create_user(db, user_data)
    token = await users.create_token(db, user.id)
    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="注册成功", data=response_data)


@router.post("/login")
async def login(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    user = await users.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    token = await users.create_token(db, user.id)
    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="登录成功", data=response_data)


@router.get("/info")
async def get_user_info(user: User = Depends(get_current_user)):
    return success_response(message="获取用户信息成功", data=UserInfoResponse.model_validate(user))


@router.put("/update")
async def update_user_info(
    user_data: UserUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user = await users.update_user(db, user.username, user_data)
    return success_response(message="用户信息更新成功", data=UserInfoResponse.model_validate(user))


@router.put("/password")
async def update_password(
    password_data: UserChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res_change_pwd = await users.change_password(db, user, password_data.old_password, password_data.new_password)
    if not res_change_pwd:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="旧密码不正确")
    return success_response(message="密码修改成功")


def _is_email(contact: str) -> bool:
    return re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9._]+\.[a-zA-Z]{2,}$", contact) is not None


@router.get("/captcha")
async def get_captcha():
    captcha_id, expression = await generate_captcha()
    return success_response(data={
        "captchaId": captcha_id,
        "expression": expression
    })


@router.post("/send_code")
async def send_verify_code(data: SendCodeRequest, db: AsyncSession = Depends(get_db)):
    if not await verify_captcha(data.captcha_id, data.captcha_code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="图形验证码错误")

    is_email = _is_email(data.contact)

    if not await can_send_code(data.contact):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="发送过于频繁，请稍后再重试")

    if is_email:
        user = await users.get_user_by_email(db, data.contact)
    else:
        user = await users.get_user_by_phone(db, data.contact)

    if not user:
        return success_response(message="验证码已发送")

    code = generate_code()
    await store_verify_code(data.contact, code)

    if is_email:
        await send_email(data.contact, code)
    else:
        await send_sms(data.contact, code)

    await mark_send_code(data.contact)
    return success_response(message="验证码已发送")


@router.post("/verify_code")
async def verify_identify_code(data: VerifyCodeRequest):
    if not await verify_code(data.contact, data.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码错误或已失效")
    reset_token = await generate_reset_token_by_contact(data.contact)
    return success_response(data={'resetToken': reset_token})


@router.put("/reset_password")
async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    contact = await get_contact_by_reset_token(data.reset_token)
    if not contact:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="令牌已失效，请重新验证")

    is_email = _is_email(contact)
    if is_email:
        user = await users.get_user_by_email(db, contact)
    else:
        user = await users.get_user_by_phone(db, contact)

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户不存在")

    await users.reset_password(db, user.id, data.new_password)
    return success_response(message="密码重置成功，请使用新密码登录")
