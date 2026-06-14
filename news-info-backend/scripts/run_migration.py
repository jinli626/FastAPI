"""幂等迁移：给 news 表补充 status 列（草稿/已发布/已下架）。

用法（在 news-info-backend 目录下执行）：
    python scripts/run_migration.py

- 自动检测列/索引是否已存在，已存在则跳过，可重复运行。
- 现有数据 status 默认 published，移动端可见性不变。
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

from config.db_conf import async_engine, DB_NAME


async def column_exists(conn, table, column):
    result = await conn.execute(
        text(
            "SELECT COUNT(*) FROM information_schema.columns "
            "WHERE table_schema = :db AND table_name = :t AND column_name = :c"
        ),
        {"db": DB_NAME, "t": table, "c": column},
    )
    return result.scalar() > 0


async def index_exists(conn, table, index):
    result = await conn.execute(
        text(
            "SELECT COUNT(*) FROM information_schema.statistics "
            "WHERE table_schema = :db AND table_name = :t AND index_name = :i"
        ),
        {"db": DB_NAME, "t": table, "i": index},
    )
    return result.scalar() > 0


async def main():
    async with async_engine.begin() as conn:
        # 1. 添加 status 列
        if await column_exists(conn, "news", "status"):
            print("[1/2] news.status 列已存在，跳过")
        else:
            await conn.execute(text(
                "ALTER TABLE `news` "
                "ADD COLUMN `status` ENUM('draft','published','offline') "
                "NOT NULL DEFAULT 'published' "
                "COMMENT '状态：草稿/已发布/已下架' AFTER `views`"
            ))
            print("[1/2] 已添加 news.status 列（现有数据默认 published）")

        # 2. 添加状态索引
        if await index_exists(conn, "news", "idx_news_status"):
            print("[2/2] idx_news_status 索引已存在，跳过")
        else:
            await conn.execute(text("ALTER TABLE `news` ADD INDEX `idx_news_status` (`status`)"))
            print("[2/2] 已添加 idx_news_status 索引")

    await async_engine.dispose()
    print("迁移完成。请重启后端（或它已热重载），刷新移动端即可正常加载。")


if __name__ == "__main__":
    asyncio.run(main())
