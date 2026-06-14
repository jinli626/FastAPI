"""初始化数据库：创建全部业务表，并播种一个种子管理员。

用法（在 news-info-backend 目录下，或容器内执行）：
    python scripts/init_db.py                 # 默认管理员 admin / admin123
    python scripts/init_db.py myname mypwd     # 自定义管理员账号/密码

说明：
- App 启动时不会自动建表，首次部署需跑一次本脚本。
- create_all 默认 checkfirst，已存在的表会自动跳过，可重复运行。
- 这里显式导入全部模型，确保它们都注册到 Base.metadata 后再统一建表。
"""
import asyncio
import os
import sys

# 让脚本可直接以 `python scripts/init_db.py` 运行：把后端根目录加入模块搜索路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from config.db_conf import async_engine, AsyncSessionLocal
from models.base import Base
# 显式导入所有模型，把每张表都注册到 Base.metadata（顺序无所谓）
from models import news        # noqa: F401  Category / News
from models import users       # noqa: F401  User / UserToken
from models import favorite    # noqa: F401  Favorite
from models import history     # noqa: F401  History
from models.admin import Admin  # noqa: F401  Admin / AdminToken
from utils import security


async def init_db(username: str, password: str):
    # 1. 创建全部表（已存在的表会被自动跳过）
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[1/2] 全部业务表已就绪")

    # 2. 插入种子管理员（若不存在）
    async with AsyncSessionLocal() as session:
        existing = await session.execute(select(Admin).where(Admin.username == username))
        if existing.scalar_one_or_none():
            print(f"[2/2] 管理员 '{username}' 已存在，跳过创建")
        else:
            admin = Admin(
                username=username,
                password=security.get_hash_password(password),
                nickname="超级管理员",
            )
            session.add(admin)
            await session.commit()
            print(f"[2/2] 已创建管理员：账号={username}  密码={password}")

    await async_engine.dispose()


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "admin"
    pwd = sys.argv[2] if len(sys.argv) > 2 else "admin123"
    asyncio.run(init_db(name, pwd))
    print("完成。请用该账号在管理端登录，并尽快修改默认密码。")
