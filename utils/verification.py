import random
import smtplib
import uuid
from email.mime.text import MIMEText

from config.cache_conf import get_str_cache, set_cache, redis_client

CODE_EXPIRE = 300
RESET_TOKEN_EXPIRE = 600
SEND_INTERVAL = 60

# ==================== 邮箱配置 ====================
# QQ邮箱 SMTP：登录QQ邮箱 → 设置 → 账户 → 开启POP3/SMTP服务 → 获取授权码
SMTP_HOST = 'smtp.qq.com'
SMTP_PORT = 587
SMTP_USER = 'SMTP_USER'  # ← 改这里
SMTP_PASSWORD = 'SMTP_PASSWORD'  # ← 改这里（16位授权码，不是QQ密码）

# ==================== 阿里云短信配置 ====================
# 开通流程：aliyun.com → 短信服务 → 申请签名+模板 → 获取AccessKey
ALIBABA_ACCESS_KEY_ID = 'ALIBABA_ACCESS_KEY_ID '  # ← 改这里
ALIBABA_ACCESS_KEY_SECRET = 'ALIBABA_ACCESS_KEY_SECRET'  # ← 改这里
ALIBABA_SMS_SIGN_NAME = '新闻资讯'  # ← 短信签名
ALIBABA_SMS_TEMPLATE_CODE = 'SMS_XXXXXXXXX'  # ← 模板CODE


def generate_code():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])


async def can_send_code(key: str) -> bool:
    last = await get_str_cache(f"send_limit:{key}")
    return last is None


async def mark_send_code(key: str):
    await set_cache(f"send_limit:{key}", '1', SEND_INTERVAL)


async def store_verify_code(key: str, code: str):
    await set_cache(f"send_limit:{key}", code, CODE_EXPIRE)


async def verify_code(key: str, code: str) -> bool:
    stored = await get_str_cache(f"verify_code:{key}")
    if stored and stored == str(code):
        await redis_client.delete(f"verify_code:{key}")
        return True
    return False


async def generate_reset_token_by_contact(contact: str) -> str:
    token = str(uuid.uuid4())
    await set_cache(f"reset_token:{token}", contact, RESET_TOKEN_EXPIRE)
    return token


async def get_contact_by_reset_token(token: str) -> str | None:
    contact = await get_str_cache(f"reset_token:{token}")
    if contact:
        await redis_client.delete(f"reset_token:{token}")
        return contact
    return None


def _sms_configured() -> bool:
    return ALIBABA_ACCESS_KEY_ID not in ('your_access_key_id', '')


async def send_sms(phone: str, code: str) -> bool:
    """
    发送短信验证码（阿里云短信服务）
    """
    if not _sms_configured():
        # 未配置时打印到控制台，方便开发调试
        print(f"[SMS] 发送验证码 {code} 到手机号 {phone}（未配置阿里云短信）", flush=True)
        return True

    try:
        from alibabacloud_dysmsapi20170525.client import Client as SmsClient
        from alibabacloud_dysmsapi20170525 import models as sms_models
        from alibabacloud_tea_openapi import models as open_api_models

        config = open_api_models.Config(
            access_key_id=ALIBABA_ACCESS_KEY_ID,
            access_key_secret=ALIBABA_ACCESS_KEY_SECRET,
        )
        config.endpoint = 'dysmsapi.aliyuncs.com'
        client = SmsClient(config)

        request = sms_models.SendSmsRequest(
            phone_numbers=phone,
            sign_name=ALIBABA_SMS_SIGN_NAME,
            template_code=ALIBABA_SMS_TEMPLATE_CODE,
            template_param=f'{{"code":"{code}"}}',
        )
        response = client.send_sms(request)

        if response.body.code == 'OK':
            print(f"[SMS] 发送验证码 {code} 到手机号 {phone} 成功", flush=True)
            return True
        else:
            print(f"[SMS] 发送失败: {response.body.message}", flush=True)
            return False
    except Exception as e:
        print(f"[SMS] 发送异常: {e}", flush=True)
        return False


def _email_configured() -> bool:
    return SMTP_USER not in ('your_email@qq.com', '')


async def send_email(to_email: str, code: str) -> bool:
    """发送邮箱验证码（QQ邮箱SMTP）"""
    if not _email_configured():
        print(f"[EMAIL] 发送验证码 {code} 到邮箱 {to_email}（未配置邮箱）", flush=True)
        return True

    msg = MIMEText(
        f'<p>您的验证码是：<b style="font-size:24px;color:#1989fa;">{code}</b></p>'
        f'<p>验证码 {CODE_EXPIRE // 60} 分钟内有效，请勿泄露给他人。</p>',
        'html', 'utf-8'
    )
    msg['Subject'] = '新闻资讯 - 找回密码验证码'
    msg['From'] = SMTP_USER
    msg['To'] = to_email

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.sendmail(SMTP_USER, [to_email], msg.as_string())
        print(f"[EMAIL] 发送验证码 {code} 到邮箱 {to_email}", flush=True)
        return True
    except Exception as e:
        print(f"[EMAIL] 发送失败: {e}", flush=True)
        return False
