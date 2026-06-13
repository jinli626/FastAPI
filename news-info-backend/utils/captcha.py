import hashlib
import random

from config.cache_conf import set_cache, get_str_cache


async def generate_captcha():
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    op = random.choice(['+', '-', '*'])
    if op == '+':
        answer = a + b
    elif op == '-':
        answer = a - b
    else:
        answer = a * b
    expression = f"{a} {op} {b} = ?"
    captcha_id = hashlib.md5(f"{a}{op}{b}".encode()).hexdigest()[:12]
    await set_cache(f"captcha:{captcha_id}", str(answer), 300)
    return captcha_id, expression


async def verify_captcha(captcha_id: str, answer: str) -> bool:
    stored = await get_str_cache(f"captcha:{captcha_id}")
    if stored and stored == str(answer):
        return True
    return False
