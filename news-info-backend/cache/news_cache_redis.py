from config.cache_conf import get_json_cache, set_cache, redis_client

CATEGORIES_KEY = 'news:categories'
NEWS_LIST_PREFIX = "news_list:"


async def get_cache_categories():
    return await get_json_cache(CATEGORIES_KEY)


async def set_cache_categories(data, expire: int = 7200):
    return await set_cache(CATEGORIES_KEY, data, expire)


async def get_cache_news_list(category_id, page, size):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"
    return await get_json_cache(key)


async def set_cache_news_list(category_id, page, size, news_list, expire: int = 1800):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"
    return await set_cache(key, news_list, expire)


async def invalidate_news_list_cache(category_id: int):
    pattern = f"{NEWS_LIST_PREFIX}{category_id}:*"
    try:
        async for key in redis_client.scan_iter(match=pattern):
            await redis_client.delete(key)
    except Exception as e:
        print(f"清除新闻列表缓存失败：{e}")
