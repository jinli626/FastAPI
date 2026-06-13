import os
import random
import smtplib
import uuid
from email.mime.text import MIMEText

from config.cache_conf import get_str_cache, set_cache, redis_client
from config.env import load_env

# 启动时把项目根目录的 .env 读入环境变量（密钥等敏感信息不写入代码）
load_env()

CODE_EXPIRE = 300
RESET_TOKEN_EXPIRE = 600
SEND_INTERVAL = 60

# ==================== 邮箱配置（QQ邮箱 SMTP）====================
# 在 .env 中配置：SMTP_USER / SMTP_PASSWORD（16位授权码，不是QQ密码）
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.qq.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')

# ==================== 阿里云短信配置 ====================
# 在 .env 中配置：ALIBABA_ACCESS_KEY_ID / ALIBABA_ACCESS_KEY_SECRET / 签名 / 模板
ALIBABA_ACCESS_KEY_ID = os.getenv('ALIBABA_ACCESS_KEY_ID', '')
ALIBABA_ACCESS_KEY_SECRET = os.getenv('ALIBABA_ACCESS_KEY_SECRET', '')
ALIBABA_SMS_SIGN_NAME = os.getenv('ALIBABA_SMS_SIGN_NAME', '')
ALIBABA_SMS_TEMPLATE_CODE = os.getenv('ALIBABA_SMS_TEMPLATE_CODE', '')


def generate_code():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])


async def can_send_code(key: str) -> bool:
    last = await get_str_cache(f"send_limit:{key}")
    return last is None


async def mark_send_code(key: str):
    await set_cache(f"send_limit:{key}", '1', SEND_INTERVAL)


async def store_verify_code(key: str, code: str):
    await set_cache(f"verify_code:{key}", code, CODE_EXPIRE)


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


def send_sms(phone: str, code: str) -> bool:
    """
    发送短信验证码（阿里云 短信认证服务 dypnsapi）
    内部为阻塞式网络调用，应通过 BackgroundTasks 在后台线程池中执行
    """
    if not _sms_configured():
        print(f"[SMS] 发送验证码 {code} 到手机号 {phone}（未配置阿里云短信）", flush=True)
        return True

    try:
        from aliyunsdkcore.client import AcsClient
        from aliyunsdkcore.request import CommonRequest

        # 初始化客户端
        client = AcsClient(ALIBABA_ACCESS_KEY_ID, ALIBABA_ACCESS_KEY_SECRET, "cn-hangzhou")
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain("dypnsapi.aliyuncs.com")
        request.set_method("POST")
        request.set_protocol_type("https")
        request.set_version("2017-05-25")
        request.set_action_name("SendSmsVerifyCode")

        # 全部必填参数
        request.add_query_param("PhoneNumber", phone)
        request.add_query_param("SignName", ALIBABA_SMS_SIGN_NAME)
        request.add_query_param("TemplateCode", ALIBABA_SMS_TEMPLATE_CODE)
        request.add_query_param("TemplateParam", f'{{"code":"{code}","min":"5"}}')

        response = client.do_action_with_exception(request)
        print(f"[SMS] 阿里云返回：{response.decode('utf-8')}", flush=True)
        return True

    except Exception as e:
        print(f"[SMS] 发送异常: {e}", flush=True)
        return False


def _email_configured() -> bool:
    return SMTP_USER not in ('your_email@qq.com', '')


def send_email(to_email: str, code: str) -> bool:
    """发送邮箱验证码（QQ邮箱SMTP）

    内部为阻塞式 SMTP 调用，应通过 BackgroundTasks 在后台线程池中执行。
    """
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
