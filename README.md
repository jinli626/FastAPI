# 📰 FastAPI 新闻 APP

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7.0-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

一个基于 **FastAPI + SQLAlchemy 2.0 + MySQL + Redis** 构建的高性能异步新闻后端 API 服务。

[✨ 功能](#-功能)
·
[🚀 快速开始](#-快速开始)
·
[📖 API 文档](#-api-概览)
·
[🏗️ 架构](#-项目架构)
·
[📝 设计笔记](#-核心设计)

</div>

---

## 📋 目录

- [✨ 功能](#-功能)
- [🛠️ 技术栈](#️-技术栈)
- [📁 项目结构](#-项目结构)
- [🚀 快速开始](#-快速开始)
- [📖 API 概览](#-api-概览)
- [🏗️ 项目架构](#-项目架构)
- [🔐 认证流程](#-认证流程)
- [⚡ 缓存策略](#-缓存策略)
- [🗄️ 数据库设计](#️-数据库设计)
- [🧩 核心设计](#-核心设计)
- [🆚 与 DRF 对比](#-与-django-drf-对比)
- [📄 License](#-license)

---

## ✨ 功能

| 模块 | 功能 | 认证要求 |
|------|------|----------|
| 🔐 **用户** | 注册、登录、获取信息、修改资料、修改密码 | 部分需要 |
| 📰 **新闻** | 分类列表、分页新闻列表、新闻详情（浏览量 +1 + 相关推荐） | 无需认证 |
| ⭐ **收藏** | 收藏/取消收藏、检查收藏状态、收藏列表、清空收藏 | 需要认证 |
| 🕐 **历史** | 添加浏览历史、历史列表、删除/清空历史 | 需要认证 |

---

## 🛠️ 技术栈

| 组件 | 选型 | 说明 |
|------|------|------|
| **Web 框架** | FastAPI | 高性能异步框架，自动生成 OpenAPI 文档 |
| **ORM** | SQLAlchemy 2.0+ | Data Mapper 模式，支持异步操作 |
| **数据库** | MySQL 8.0 | 关系型数据库 |
| **数据库驱动** | aiomysql | 异步 MySQL 驱动，配合 asyncio 事件循环 |
| **数据校验** | Pydantic v2 | 类型驱动的数据校验与序列化 |
| **缓存** | Redis 7.0 | 热点数据缓存，减少数据库压力 |
| **密码加密** | passlib + bcrypt | 自带盐值的密码哈希算法，抗暴力破解 |
| **服务器** | uvicorn | ASGI 服务器，支持异步并发 |

---

## 📁 项目结构

```
FastAPI01/
├── main.py                       # 🚀 应用入口：FastAPI 实例、中间件、路由注册
├── config/                       # ⚙️  基础设施配置
│   ├── db_conf.py                #   异步 MySQL 引擎 + 会话工厂 + 依赖注入
│   └── cache_conf.py             #   异步 Redis 客户端 + 缓存读写工具
├── models/                       # 🗄️ ORM 模型定义
│   ├── users.py                  #   User 表 + UserToken 表
│   ├── news.py                   #   Category 表 + News 表
│   ├── favorite.py               #   Favorite 收藏关联表
│   └── history.py                #   History 浏览历史表
├── schemas/                      # ✅ Pydantic 请求/响应模型
│   ├── base.py                   #   NewsItemBase 新闻基类
│   ├── users.py                  #   用户注册/登录/信息响应
│   ├── favorite.py               #   收藏请求/响应
│   └── history.py                #   历史请求/响应
├── routers/                      # 🌐 API 路由
│   ├── users.py                  #   /api/user/*
│   ├── news.py                   #   /api/news/*
│   ├── favorite.py               #   /api/favorite/*
│   └── history.py                #   /api/history/*
├── crud/                         # 📦 数据操作层
│   ├── users.py                  #   用户增删改查 + Token 管理 + 认证
│   ├── news.py                   #   新闻查询 + 浏览量更新
│   ├── news_cache.py             #   新闻查询（带 Redis 缓存）
│   ├── favorite.py               #   收藏增删查
│   └── history.py                #   历史增删查
├── cache/                        # ⚡ 缓存 Key 管理
│   └── news_cache.py             #   Redis Key 前缀 + 读写方法
└── utils/                        # 🔧 工具层
    ├── auth.py                   #   Token 认证依赖注入
    ├── security.py               #   密码加密/验证
    ├── response.py               #   统一 JSON 响应格式
    ├── exception.py              #   各类异常处理函数
    └── exception_handlers.py     #   异常处理器注册
```

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- MySQL 8.0+
- Redis 7.0+

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/fastapi-news-app.git
cd fastapi-news-app
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

核心依赖：
```
fastapi>=0.100.0
uvicorn[standard]
sqlalchemy>=2.0
aiomysql
redis[hiredis]
passlib[bcrypt]
pydantic>=2.0
python-multipart
```

### 3. 配置数据库

修改 `config/db_conf.py` 中的数据库连接信息：

```python
ASYNC_DATABASE_URL = "mysql+aiomysql://用户名:密码@主机:端口/数据库名?charset=utf8mb4"
```

修改 `config/cache_conf.py` 中的 Redis 连接信息：

```python
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_PASSWORD = 'your_password'
```

### 4. 创建数据库表

```bash
# 启动 MySQL 后，创建数据库
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS news_app DEFAULT CHARACTER SET utf8mb4;"

# 启动应用后，访问 /init 端点创建表（或使用 SQLAlchemy）：
python -c "from models.users import Base, async_engine; import asyncio; asyncio.run(async_engine.connect())"
```

或者手动初始化：

```python
# 在 Python 交互环境中运行
from models.users import Base as UserBase
from models.news import Base as NewsBase
from config.db_conf import async_engine
import asyncio

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(UserBase.metadata.create_all)
        await conn.run_sync(NewsBase.metadata.create_all)

asyncio.run(init_db())
```

### 5. 启动服务

```bash
# 开发模式（热重载）
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 6. 访问 API 文档

启动后打开浏览器访问：

- 🎨 **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- 📄 **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- ✅ **健康检查**: [http://localhost:8000/](http://localhost:8000/)

---

## 📖 API 概览

### 🔐 用户模块 `/api/user`

| 方法 | 端点 | 说明 | 认证 |
|------|------|------|------|
| `POST` | `/register` | 用户注册 | ❌ |
| `POST` | `/login` | 用户登录，返回 7 天有效 Token | ❌ |
| `GET` | `/info` | 获取当前用户信息 | ✅ |
| `PUT` | `/update` | 修改个人信息（昵称/头像/简介等） | ✅ |
| `PUT` | `/password` | 修改密码（需旧密码验证） | ✅ |

### 📰 新闻模块 `/api/news`

| 方法 | 端点 | 说明 | 认证 |
|------|------|------|------|
| `GET` | `/categories` | 获取新闻分类列表 | ❌ |
| `GET` | `/list?categoryId=1&page=1&pageSize=10` | 分页新闻列表 | ❌ |
| `GET` | `/detail?id=123` | 新闻详情（浏览量+1 + 相关推荐） | ❌ |

### ⭐ 收藏模块 `/api/favorite`

| 方法 | 端点 | 说明 | 认证 |
|------|------|------|------|
| `GET` | `/check?newsId=1` | 检查某条新闻是否已收藏 | ✅ |
| `POST` | `/add` | 添加收藏 | ✅ |
| `DELETE` | `/remove?newsId=1` | 取消收藏 | ✅ |
| `GET` | `/list?page=1&pageSize=10` | 收藏列表（分页） | ✅ |
| `DELETE` | `/clear` | 清空所有收藏 | ✅ |

### 🕐 历史模块 `/api/history`

| 方法 | 端点 | 说明 | 认证 |
|------|------|------|------|
| `POST` | `/add` | 添加浏览记录（存在则更新时间） | ✅ |
| `GET` | `/list?page=1&pageSize=10` | 浏览历史列表（分页） | ✅ |
| `DELETE` | `/delete/{history_id}` | 删除单条历史记录 | ✅ |
| `DELETE` | `/clear` | 清空所有历史记录 | ✅ |

### 📦 统一响应格式

所有接口返回统一 JSON 格式：

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

- `code`：业务状态码（200 表示成功）
- `message`：人类可读的提示信息
- `data`：实际的业务数据（可为 `null`）

---

## 🏗️ 项目架构

### 请求处理流程

```
客户端请求
    │
    ▼
┌─────────────────────────────────────────────────┐
│  main.py（CORS 中间件 + 异常处理器）               │
└─────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────┐
│  routers/（路由层）                                │
│  接收请求 → 校验参数 → 调用 CRUD → 组装响应         │
└─────────────────────────────────────────────────┘
    │                    │
    ▼                    ▼
┌──────────────┐  ┌──────────────┐
│  schemas/    │  │  utils/      │
│  Pydantic    │  │  认证/加密    │
│  数据校验     │  │  异常处理     │
└──────────────┘  └──────────────┘
    │
    ▼
┌─────────────────────────────────────────────────┐
│  crud/（数据操作层）                               │
│  封装 SQL 操作 → 先查 Redis 缓存 → 再查 MySQL       │
└─────────────────────────────────────────────────┘
    │                    │
    ▼                    ▼
┌──────────────┐  ┌──────────────┐
│  models/     │  │  cache/       │
│  SQLAlchemy  │  │  Redis Key    │
│  ORM 模型     │  │  管理          │
└──────────────┘  └──────────────┘
    │                    │
    ▼                    ▼
   MySQL              Redis
```

### 分层职责

| 层级 | 目录 | 职责 |
|------|------|------|
| **配置层** | `config/` | 数据库连接池、Redis 客户端等基础设施 |
| **模型层** | `models/` | 定义数据库表结构（ORM 映射） |
| **校验层** | `schemas/` | 定义 API 请求/响应的数据格式与校验规则 |
| **路由层** | `routers/` | 定义 API 端点，组装请求参数和响应数据 |
| **数据操作层** | `crud/` | 封装数据库 CRUD 操作，桥接路由与数据库 |
| **缓存层** | `cache/` | 管理 Redis 缓存 Key 的读写 |
| **工具层** | `utils/` | 认证、加密、响应格式化、异常处理等横切关注点 |

---

## 🔐 认证流程

本项目采用 **数据库存储 Token** 的认证方案（而非 JWT）。

### 为什么不用 JWT？

| 方案 | 优点 | 缺点 |
|------|------|------|
| **数据库 Token**（本项目） | 可随时失效、修改密码后旧 Token 自动作废 | 每次请求需查数据库 |
| **JWT** | 无状态、不需要查数据库 | 无法主动失效（除非维护黑名单） |

### 认证流程

```
注册/登录成功
    │
    ▼
生成 UUID Token ──► 存入 user_token 表（7天过期）
    │
    ▼
客户端存储 Token ──► 后续请求携带 Authorization: Bearer <token>
    │
    ▼
get_current_user 依赖项：
  ① 从请求头提取 Token
  ② 查 user_token 表验证有效性
  ③ 检查是否过期
  ④ 查 user 表返回用户对象
    │
    ▼
路由函数获得 User 对象
```

### 需要认证的接口写法

```python
from utils.auth import get_current_user

@router.get("/info")
async def get_user_info(user: User = Depends(get_current_user)):
    # user 已是通过 Token 验证的用户对象
    return success_response(data=UserInfoResponse.model_validate(user))
```

只需在路由函数参数中加上 `user: User = Depends(get_current_user)` 即可实现认证保护。

---

## ⚡ 缓存策略

采用 **Cache-Aside（旁路缓存）** 模式：

```
请求数据
    │
    ▼
查 Redis 缓存
    │
    ├── 命中（Hit）──► 直接返回缓存数据
    │
    └── 未命中（Miss）
        │
        ▼
    查 MySQL 数据库
        │
        ▼
    写入 Redis 缓存（设置过期时间）
        │
        ▼
    返回数据
```

### 缓存时间配置

| 数据类型 | 缓存 Key 示例 | 过期时间 | 原因 |
|----------|---------------|----------|------|
| 分类列表 | `news:categories` | 2 小时 | 分类数据很少变动 |
| 新闻列表 | `news_list:1:1:10` | 30 分钟 | 新闻更新较频繁，半实时即可 |
| 新闻详情 | 不缓存 | — | 每次查看浏览量需要实时 +1 |

### Redis Key 命名规范

采用 `:` 分隔的层级命名结构：

```
news:categories              # 分类列表
news_list:1:1:10             # 分类1，第1页，每页10条
news_list:all:2:20           # 全部分类，第2页，每页20条
```

---

## 🗄️ 数据库设计

### ER 图

```
┌──────────────┐       ┌──────────────┐
│     User     │       │   Category   │
├──────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)      │
│ username (U) │       │ name (U)     │
│ password     │       │ sort_order   │
│ nickname     │       │ created_at   │
│ avatar       │       │ updated_at   │
│ gender       │       └──────┬───────┘
│ bio          │              │
│ phone (U)    │              │
│ created_at   │              │
│ updated_at   │              │
└──────┬───────┘              │
       │                      │
       │  ┌───────────────────┘
       │  │
       ▼  ▼
┌──────────────┐       ┌──────────────┐
│  UserToken   │       │    News      │
├──────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)      │
│ user_id (FK) │       │ title        │
│ token (U)    │       │ description  │
│ expires_at   │       │ content      │
│ created_at   │       │ image        │
└──────────────┘       │ author       │
                       │ category_id(FK)
       ┌───────────────┤ views        │
       │               │ publish_time │
       │               │ created_at   │
       │               │ updated_at   │
       │               └──────┬───────┘
       │                      │
       ▼                      ▼
┌──────────────┐       ┌──────────────┐
│   Favorite   │       │   History    │
├──────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)      │
│ user_id (FK) │       │ user_id (FK) │
│ news_id (FK) │       │ news_id (FK) │
│ created_at   │       │ view_time    │
│ (user+news U)│       └──────────────┘
└──────────────┘
```

### 索引设计

| 表 | 索引 | 用途 |
|----|------|------|
| User | `username_UNIQUE` | 加速用户名查询（登录/注册唯一性检查） |
| User | `phone_UNIQUE` | 加速手机号查询 |
| UserToken | `token_UNIQUE` | 加速 Token 验证（每次请求都需查） |
| UserToken | `fk_user_token_user_idx` | 加速按用户查 Token |
| News | `fk_news_category_idx` | 加速按分类查新闻（最频繁的查询） |
| News | `idx_publish_time` | 加速按发布时间排序 |
| Favorite | `user_news_unique` | 联合唯一约束 + 加速收藏状态查询 |
| Favorite | `fk_favorite_user_idx` | 加速查询用户收藏列表 |
| History | `fk_history_user_idx` | 加速查询用户历史 |
| History | `idx_view_time` | 加速按浏览时间排序 |

---

## 🧩 核心设计

### 1. 异步数据库会话管理

使用 FastAPI 的 `yield` 依赖注入管理数据库会话的完整生命周期：

```python
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session                    # 交给路由函数
            await session.commit()           # 正常 → 提交
        except Exception:
            await session.rollback()         # 异常 → 回滚
            raise
        finally:
            await session.close()            # 最终 → 关闭连接
```

> **关键设置：** `expire_on_commit=False` — commit 后 ORM 对象的属性保持有效，避免异步上下文中隐式触发额外 SQL 查询。

### 2. 密码安全

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 加密：每次生成不同的盐值，同一密码的哈希结果也不同
def get_hash_password(password: str):
    return pwd_context.hash(password)

# 验证：从已有哈希中提取盐值后重算比较
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
```

bcrypt 哈希示例：
```
$2b$12$LJ3m4ys3Lk0TSwMOPGDMZO5.jHxP3UYl8GYL3gMnNL.9tVPOkAG6
 ─┬─  ─┬─  ──────────────┬────────────── ──────┬──────
 算法  成本     22位随机盐值                    哈希结果
```

### 3. 浏览量原子更新

使用 SQL 表达式避免并发竞态条件：

```python
# ✅ 正确：数据库层面原子操作
stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
await db.execute(stmt)

# ❌ 错误：Python 层面计算，并发时可能丢失更新
# news.views = news.views + 1
```

### 4. 统一异常处理

按异常类型的继承关系从具体到通用逐层兜底：

```
HTTPException（业务异常）→ 400/401/404 等
    ↓
IntegrityError（约束冲突）→ 解析错误消息 → 友好中文提示
    ↓
SQLAlchemyError（数据库异常）→ 500 通用错误
    ↓
Exception（未知异常）→ 500 兜底
```

### 5. Pydantic 驼峰/蛇形命名映射

前端（JavaScript/驼峰） ↔ 后端（Python/蛇形）自动转换：

```python
class NewsItemBase(BaseModel):
    category_id: int = Field(alias="categoryId")    # JSON: categoryId
    publish_time: datetime = Field(None, alias="publishTime")

    model_config = ConfigDict(
        from_attributes=True,    # 允许从 ORM 对象直接创建
        populate_by_name=True    # 同时接受 category_id 和 categoryId
    )
```

### 6. 批量更新时区分"未传"与"传了 None"

```python
# 前端只传了昵称
{"nickname": "新昵称"}

# CRUD 层使用 exclude_unset 只更新实际传了的字段
user_data.model_dump(exclude_unset=True, exclude_none=True)
# 结果：{"nickname": "新昵称"}  ← 不会把 avatar 等设成 NULL
```

### 7. 浏览历史去重

收藏表用 `UniqueConstraint` 防止重复收藏，浏览历史表虽然不限制重复记录，但在 CRUD 层做了"存在则更新时间、不存在则新建"的处理：

```python
async def add_history(db, user_id, news_id):
    existing = await db.execute(
        select(History).where(History.user_id == user_id, History.news_id == news_id)
    )
    if history := existing.scalar_one_or_none():
        history.view_time = datetime.now()  # 更新时间
    else:
        db.add(History(user_id=user_id, news_id=news_id))  # 新建
    await db.commit()
```

---

## 🆚 与 Django DRF 对比

| 维度 | Django DRF | FastAPI（本项目） |
|------|------------|-------------------|
| **异步支持** | 同步为主（4.1+ 部分异步） | ✅ **全异步** async/await |
| **ORM** | Django ORM（Active Record） | SQLAlchemy 2.0（Data Mapper） |
| **数据校验** | Serializer（校验+序列化耦合） | Pydantic（纯校验层，与 ORM 分离） |
| **路由** | `urls.py` + ViewSet（集中配置） | 装饰器 + APIRouter（分散定义） |
| **认证** | 自定义 Authentication 类 | `Depends(get_current_user)` 函数组合 |
| **密码加密** | 需手动集成 | passlib + bcrypt（自带盐值） |
| **API 文档** | 需额外安装 drf-spectacular | ✅ **自动生成** `/docs` + `/redoc` |
| **依赖注入** | ❌ 无内置支持 | ✅ 强大的 `Depends` 系统 |
| **分页** | PageNumberPagination（全局自动） | 手动 offset/limit（更灵活） |
| **缓存** | django-redis（高集成度） | redis.asyncio（底层封装） |
| **数据库驱动** | mysqlclient（同步） | aiomysql（异步非阻塞） |
| **并发性能** | 中等 | ✅ **极高**（接近 Go/Node.js） |

---

## 📄 License

本项目基于 [MIT License](LICENSE) 开源。

---

<div align="center">

### ⭐ 如果这个项目对你有帮助，欢迎 Star！

**技术栈**: FastAPI · SQLAlchemy 2.0 · MySQL · Redis · Pydantic v2 · bcrypt

</div>
