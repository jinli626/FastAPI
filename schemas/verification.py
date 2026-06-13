from pydantic import BaseModel, Field, ConfigDict


class SendCodeRequest(BaseModel):
    contact: str = Field(..., max_length=100, description='手机号或邮箱')
    captcha_id: str = Field(..., description='图形验证码ID', alias='captchaId')
    captcha_code: str = Field(..., max_length=10, description='图形验证码答案', alias='captchaCode')
    model_config = ConfigDict(
        populate_by_name=True
    )


class VerifyCodeRequest(BaseModel):
    contact: str = Field(..., max_length=100, description='手机号或邮箱')
    code: str = Field(..., max_length=10, description='验证码')
    model_config = ConfigDict(
        populate_by_name=True
    )


class ResetPasswordRequest(BaseModel):
    reset_token: str = Field(..., max_length=100, description='验证通过后获取的重置token')
    new_password: str = Field(..., min_length=6, max_length=255, description='新密码', alias='newPassword')
    model_config = ConfigDict(
        populate_by_name=True
    )
