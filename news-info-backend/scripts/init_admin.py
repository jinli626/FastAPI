"""初始化管理员：创建 admin / admin_token 表并插入一个种子管理员。

用法（在 news-info-backend 目录下执行）：
    python scripts/init_admin.py                 # 使用默认账号 admin / admin123
    python scripts/init_admin.py myname mypwd     # 自定义账号与密码

说明：
- 仅创建 Admin / AdminToken 两张新表（create_all 默认 checkfirst，已存在的表会跳过）。
- 若同名管理员已存在则不会重复插入。
"""
import asyncio
import os
import sys

# 让脚本可直接以 `python scripts/init_admin.py` 运行：把后端根目录加入模块搜索路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from config.db_conf import async_engine, AsyncSessionLocal
from models.base import Base
from models.admin import Admin  # noqa: F401  仅为把 Admin/AdminToken 注册到 Base.metadata
from utils import security


async def init_admin(username: str, password: str):
    # 1. 创建新表（已存在的表会被自动跳过）
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[1/2] admin / admin_token 表已就绪")

    # 2. 插入种子管理员（若不存在）
    async with AsyncSessionLocal() as session:
        existing = await session.execute(select(Admin).where(Admin.username == username))
        if existing.scalar_one_or_none():
            print(f"[2/2] 管理员 '{username}' 已存在，跳过创建")
            return
        admin = Admin(
            username=username,
            password=security.get_hash_password(password),
            nickname="超级管理员",
        )
        session.add(admin)
        await session.commit()
        print(f"[2/2] 已创建管理员：账号={username}  密码={password}")


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "admin"
    pwd = sys.argv[2] if len(sys.argv) > 2 else "admin123"
    asyncio.run(init_admin(name, pwd))
    print("完成。请用该账号在管理端登录，并尽快修改默认密码。")
