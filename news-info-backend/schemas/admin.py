from pydantic import BaseModel, Field, ConfigDict


class AdminLoginRequest(BaseModel):
    username: str = Field(..., max_length=50, description='管理员账号')
    password: str = Field(..., max_length=255, description='密码')


class AdminInfoResponse(BaseModel):
    id: int = Field(..., description='管理员ID')
    username: str = Field(..., max_length=50, description='管理员账号')
    nickname: str | None = Field(None, max_length=50, description='昵称')

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class AdminAuthResponse(BaseModel):
    token: str = Field(..., description='令牌值')
    admin_info: AdminInfoResponse = Field(..., description='管理员信息', alias='adminInfo')

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class AdminChangePasswordRequest(BaseModel):
    old_password: str = Field(..., max_length=255, description='原密码', alias='oldPassword')
    new_password: str = Field(..., min_length=6, max_length=255, description='新密码', alias='newPassword')

    model_config = ConfigDict(populate_by_name=True)
