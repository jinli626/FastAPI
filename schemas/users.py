from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class UserRequest(BaseModel):
    username: str = Field(..., max_length=50, description='用户名')
    password: str = Field(..., max_length=255, description='密码')
    phone: Optional[str] = Field(None, max_length=20, description='手机号')
    email: Optional[str] = Field(None, max_length=100, description='邮箱')


class UserInfoBase(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50, description='昵称')
    bio: Optional[str] = Field(None, max_length=500, description='个人简介')
    avatar: Optional[str] = Field(None, max_length=255, description='头像URL')
    gender: Optional[str] = Field(None, max_length=10, description='性别')


class UserInfoResponse(UserInfoBase):
    id: int = Field(..., description='用户ID')
    username: str = Field(..., description='用户名', max_length=50)
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class UserAuthResponse(BaseModel):
    token: str = Field(..., description='令牌值')
    user_info: UserInfoResponse = Field(..., description='用户信息', alias='userInfo')
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class UserUpdateRequest(UserInfoBase):
    phone: Optional[str] = Field(None, max_length=20, description='手机号')
    email: Optional[str] = Field(None, max_length=100, description='邮箱')


class UserChangePasswordRequest(BaseModel):
    old_password: str = Field(..., max_length=255, description='旧密码', alias='oldPassword')
    new_password: str = Field(..., max_length=255, description='新密码', alias='newPassword')
