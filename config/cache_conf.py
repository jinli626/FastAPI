import json
from typing import Any

import redis.asyncio as async_redis

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_PASSWORD = '123123'
REDIS_DB = 0

redis_client = async_redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    db=REDIS_DB
)


async def get_str_cache(key: str):
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f'获取str缓存失败: {e}')
        raise e


async def get_json_cache(key: str):
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f'获取json缓存失败: {e}')
        raise e


async def set_cache(key: str, value: Any, expire: int = 3600):
    try:
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        await redis_client.setex(key, expire, value)
        return True
    except Exception as e:
        print(f'设置缓存失败: {e}')
        return False
