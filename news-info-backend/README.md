# 新闻资讯 App

一个基于 **FastAPI + SQLAlchemy 2.0 + MySQL + Redis** 构建的高性能全异步新闻资讯后端，配套 **Vue 3 + Vant** 移动端。
项目围绕“**用户认证 -> 新闻浏览 -> 收藏 / 历史 -> 找回密码**”构建了完整闭环，重点体现了我在 **异步 Web 开发、缓存设计、认证安全、工程化落地** 方面的能力。

---

## 项目简介

这是一个移动端新闻资讯应用，后端提供完整的内容浏览与用户体系：

- 用户注册 / 登录后获得令牌，凭令牌访问受保护资源
- 浏览新闻分类、分页列表与详情，热点数据走 Redis 缓存
- 对新闻进行收藏、记录浏览历史，并支持分页与清空
- 忘记密码时，通过“图形验证码 + 邮箱 / 短信验证码 + 一次性令牌”安全找回

这个项目不是单一接口 Demo，而是一个包含 **全异步后端、关系型数据库、Redis 缓存、令牌认证、验证码与通知、前后端分离移动端** 的完整工程化项目。

---

## 核心亮点

### 1. 全链路异步

后端从 Web 框架到数据库、缓存全部异步：

- FastAPI + `aiomysql` + `redis.asyncio`，`async/await` 贯穿路由、CRUD、缓存
- 通过 `yield` 依赖统一管理会话生命周期：正常提交、异常回滚、最终关闭
- `expire_on_commit=False`，避免提交后在异步上下文中隐式触发额外 SQL

### 2. Cache-Aside 缓存 + 主动失效

热点读多写少的数据走 Redis 旁路缓存，而不是无脑查库：

- 分类列表、新闻列表先查缓存，未命中再回源 MySQL 并回填
- 分类列表缓存 2 小时、新闻列表缓存 30 分钟，详情不缓存以保证浏览量实时
- 查看详情时浏览量原子 `+1`，并按分类用 `scan_iter` 精准失效该分类的列表缓存，避免脏数据

相比“查库即返回”，这种方式显著降低数据库压力，又通过主动失效保证一致性。

### 3. 数据库 Token 认证（而非 JWT）

认证采用 **服务端存储 Token** 方案，安全更可控：

- 注册 / 登录签发 UUID Token 入库（`user_token`，7 天过期，单用户单令牌）
- `get_current_user` 依赖从 `Authorization: Bearer <token>` 解析并校验有效期
- 相比 JWT，可随时失效、改密后旧令牌自然作废，无需维护黑名单

### 4. 完整的找回密码安全闭环

找回密码不是一个接口，而是一条带多重防护的链路：

- 算术图形验证码（防脚本）-> 邮箱 / 短信验证码（防盗用）-> 一次性 `reset_token`（防重放）
- 发送验证码做 60s 频控；用户不存在时也返回“已发送”，以防账号枚举
- 邮件 / 短信为阻塞式网络调用，交给 `BackgroundTasks` 后台线程池执行，接口立即返回

### 5. 密钥环境变量化

所有敏感配置都迁出代码，便于安全提交与多环境部署：

- 数据库 / Redis / 邮箱 / 阿里云短信密钥全部由 `.env` 提供
- 自研零依赖 `load_env`（`os.environ.setdefault`，不覆盖已有环境变量）
- `.env` 已 gitignore，仅提交占位符模板 `.env.example`；未配置密钥时验证码自动回退控制台打印，便于本地调试

### 6. 清晰分层 + 统一响应 / 异常

项目体现了较完整的工程化思维：

- `config / models / schemas / routers / crud / cache / utils` 七层分工明确
- 统一 `{code, message, data}` 响应格式
- 异常按 `HTTPException -> IntegrityError -> SQLAlchemyError -> Exception` 逐层兜底

---

## 技术栈

### 后端

- FastAPI
- SQLAlchemy 2.0（async）
- Pydantic v2
- Uvicorn（ASGI）

### 数据与缓存

- MySQL 8.0
- aiomysql（异步驱动）
- Redis 7.0（redis.asyncio）

### 安全与通知

- passlib + bcrypt（密码哈希）
- 数据库 Token 认证
- QQ 邮箱 SMTP（验证码邮件）
- 阿里云短信 dypnsapi（验证码短信）

### 前端

- Vue 3 + Vite
- Vant 4（移动端 UI）
- Pinia（+ 持久化）
- Vue Router
- Vue I18n（中英文）
- Axios、marked + DOMPurify

---

## 系统架构

```text
[Vue 3 + Vant 移动端]
   ├─ 新闻浏览 / 分类
   ├─ 收藏 / 历史
   ├─ 登录注册 / 找回密码
   └─ 个人中心 / 设置
        │  HTTP（JSON，Bearer Token）
        ▼
[FastAPI 后端]
   ├─ routers/   接口层：参数校验、组装响应
   ├─ schemas/   Pydantic 请求 / 响应校验
   ├─ crud/      数据操作层：先查缓存，再查库
   ├─ cache/     Redis Key 管理与主动失效
   ├─ utils/     认证 / 加密 / 验证码 / 统一响应 / 异常
   └─ models/    SQLAlchemy ORM 模型
        │                          │
        ▼                          ▼
   MySQL 8.0                  Redis 7.0
   (aiomysql 异步)             (列表缓存 / 验证码 / 重置令牌)
        ▲
        │  后台任务（BackgroundTasks）
        └─ QQ 邮箱 SMTP / 阿里云短信（找回密码验证码）
```

---

## 业务流程

### 1. 注册 / 登录

1. 注册校验用户名唯一，密码经 bcrypt 加密后入库
2. 登录校验用户名 + 密码
3. 签发 7 天 UUID Token 写入 `user_token`（已存在则更新）
4. 返回 `token` 与用户信息

### 2. 新闻浏览（缓存命中链路）

1. 分类 / 列表请求先查 Redis 缓存
2. 命中直接返回；未命中查 MySQL 并回填缓存（带过期时间）
3. 详情接口浏览量原子 `+1`（`update(News).values(views=News.views + 1)`）
4. 失效该分类的列表缓存，并返回同分类相关推荐

### 3. 收藏与历史

1. 收藏：`UniqueConstraint(user_id, news_id)` 在数据库层防止重复收藏
2. 历史：CRUD 层“存在则更新浏览时间、不存在则新建”，实现去重
3. 两者均需 Token 认证，支持分页查询与一键清空

### 4. 找回密码

1. 获取算术图形验证码（`md5` 生成 `captchaId`，答案存 Redis 5 分钟）
2. 提交联系方式（邮箱 / 手机号）+ 图形验证码，后台异步下发 6 位验证码
3. 校验验证码通过后，换取一次性 `reset_token`（UUID，Redis 10 分钟）
4. 携带 `reset_token` 提交新密码，完成重置

---

## 接口概览

所有接口返回统一 JSON 格式：

```json
{
  "code": 200,
  "message": "success",
  "data": { }
}
```

### 用户 `/api/user`

- `POST /register` — 注册（用户名唯一，返回 Token）· 无需认证
- `POST /login` — 登录（返回 7 天 Token）· 无需认证
- `GET /info` — 获取当前用户信息 · 需认证
- `PUT /update` — 修改资料（昵称 / 头像 / 简介 / 性别 / 手机 / 邮箱）· 需认证
- `PUT /password` — 修改密码（校验旧密码）· 需认证
- `GET /captcha` — 获取算术图形验证码 · 无需认证
- `POST /send_code` — 发送邮箱 / 短信验证码 · 无需认证
- `POST /verify_code` — 校验验证码，换取 `reset_token` · 无需认证
- `PUT /reset_password` — 凭 `reset_token` 重置密码 · 无需认证

### 新闻 `/api/news`

- `GET /categories` — 分类列表（缓存）· 无需认证
- `GET /list?categoryId=&page=&pageSize=` — 分页新闻列表（缓存）· 无需认证
- `GET /detail?id=` — 详情（浏览量 +1 + 相关推荐）· 无需认证

### 收藏 `/api/favorite`（均需认证）

- `GET /check?newsId=` — 检查是否已收藏
- `POST /add` — 添加收藏
- `DELETE /remove` — 取消收藏
- `GET /list?page=&pageSize=` — 收藏列表（分页）
- `DELETE /clear` — 清空收藏

### 历史 `/api/history`（均需认证）

- `POST /add` — 添加浏览记录（存在则更新时间）
- `GET /list?page=&pageSize=` — 浏览历史（分页）
- `DELETE /delete/{history_id}` — 删除单条历史
- `DELETE /clear` — 清空历史

---

## 项目结构

```text
FastAPI项目练习/
├─ main.py                       # 应用入口：FastAPI 实例、CORS、路由与异常注册
├─ .env.example                  # 环境变量模板（占位符，可安全提交）
├─ config/                       # 基础设施配置
│  ├─ env.py                     #   零依赖 .env 加载器
│  ├─ db_conf.py                 #   异步 MySQL 引擎 + 会话工厂 + get_db 依赖
│  └─ cache_conf.py              #   异步 Redis 客户端 + 缓存读写工具
├─ models/                       # SQLAlchemy ORM 模型
│  ├─ base.py                    #   DeclarativeBase 基类
│  ├─ users.py                   #   User + UserToken
│  ├─ news.py                    #   Category + News
│  ├─ favorite.py                #   Favorite 收藏表
│  └─ history.py                 #   History 浏览历史表
├─ schemas/                      # Pydantic 请求 / 响应模型
│  ├─ base.py                    #   NewsItemBase 新闻基类
│  ├─ users.py                   #   注册 / 登录 / 信息 / 改密
│  ├─ favorite.py                #   收藏请求 / 响应
│  ├─ history.py                 #   历史请求 / 响应
│  └─ verification.py            #   发送 / 校验验证码、重置密码
├─ routers/                      # API 路由
│  ├─ users.py                   #   /api/user/*（含验证码、找回密码）
│  ├─ news.py                    #   /api/news/*
│  ├─ favorite.py                #   /api/favorite/*
│  └─ history.py                 #   /api/history/*
├─ crud/                         # 数据操作层
│  ├─ users.py                   #   用户增删改查 + Token + 认证 + 改密 / 重置
│  ├─ news.py                    #   新闻查询 + 浏览量原子更新 + 相关推荐
│  ├─ news_cache.py              #   带 Redis 缓存的新闻 / 分类查询
│  ├─ favorite.py                #   收藏增删查
│  └─ history.py                 #   历史增删查（存在则更新时间）
├─ cache/                        # 缓存 Key 管理
│  └─ news_cache_redis.py        #   Key 前缀、读写、列表缓存主动失效
└─ utils/                        # 工具层
   ├─ auth.py                    #   Token 认证依赖（get_current_user）
   ├─ security.py                #   bcrypt 密码加密 / 校验
   ├─ captcha.py                 #   算术图形验证码
   ├─ verification.py            #   邮箱 / 短信验证码、重置令牌
   ├─ response.py                #   统一 JSON 响应
   ├─ exception.py               #   各类异常处理函数
   └─ exception_handlers.py      #   异常处理器注册

xwzx-news/                       # Vue 3 + Vant 移动端
├─ src/views/                    #   首页 / 分类 / 详情 / 收藏 / 历史 / 登录 / 找回密码 / 我的 / 设置 / AI 对话
├─ src/store/                    #   Pinia：news / favorite / history / user / chat / theme / language
├─ src/router/                   #   Vue Router 路由
└─ src/i18n/                     #   中英文国际化
```

---

## 工程化设计亮点

### 分层清晰

后端采用较清晰的分层：

- `routers`：接口层，负责参数校验与响应组装
- `schemas`：请求 / 响应模型与数据校验
- `crud`：业务数据操作层，桥接路由与数据库 / 缓存
- `models`：数据库 ORM 模型
- `cache` / `utils`：缓存 Key 管理与认证、加密、验证码等横切关注点

这样业务逻辑更集中，新闻、用户、收藏、历史、找回密码各模块可独立维护与扩展。

### 异步会话与原子更新

```python
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session            # 交给路由函数
            await session.commit()   # 正常 -> 提交
        except Exception:
            await session.rollback() # 异常 -> 回滚
            raise
        finally:
            await session.close()    # 最终 -> 关闭
```

浏览量更新使用 SQL 表达式在数据库层原子自增，避免并发竞态：

```python
stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
```

### Cache-Aside 与缓存失效

| 数据类型 | 缓存 Key 示例 | 过期时间 | 原因 |
|----------|---------------|----------|------|
| 分类列表 | `news:categories` | 2 小时 | 分类很少变动 |
| 新闻列表 | `news_list:1:1:10` | 30 分钟 | 半实时即可 |
| 新闻详情 | 不缓存 | — | 浏览量需实时 +1 |

- Key 采用 `:` 分层命名（如 `news_list:{分类}:{页}:{每页}`）
- 浏览详情后按分类 `scan_iter` 匹配并删除对应列表缓存，保证一致性

### 统一响应与分层异常处理

- 所有接口经 `success_response` 返回统一 `{code, message, data}`
- 异常处理器按继承关系从具体到通用逐层兜底：

```text
HTTPException（业务异常）   -> 400 / 401 / 404 等
IntegrityError（约束冲突） -> 解析错误 -> 友好中文提示
SQLAlchemyError（库异常）  -> 500 通用错误
Exception（未知异常）      -> 500 兜底
```

### 密钥环境变量化（零依赖 .env）

- 自研 `load_env` 解析项目根目录 `.env`，无需第三方依赖
- 使用 `os.environ.setdefault`，已存在的同名环境变量不被覆盖
- 文件缺失时静默跳过，验证码自动回退控制台打印，保证未配置密钥也能启动联调

### Pydantic 驼峰 / 蛇形映射与按需更新

```python
class NewsItemBase(BaseModel):
    category_id: int = Field(alias="categoryId")          # 前端 camelCase
    publish_time: datetime = Field(None, alias="publishTime")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
```

修改资料时用 `model_dump(exclude_unset=True, exclude_none=True)`，只更新前端实际传入的字段，避免把未传字段误置为 `NULL`。

### 数据模型

```text
┌──────────────┐        ┌──────────────┐
│     User     │        │   Category   │   (news_category)
├──────────────┤        ├──────────────┤
│ id (PK)      │        │ id (PK)      │
│ username (U) │        │ name (U)     │
│ password     │        │ sort_order   │
│ phone (U)    │        └──────┬───────┘
│ email (U)    │               │
│ nickname     │               │
│ gender/bio.. │               ▼
└──────┬───────┘        ┌──────────────┐
       │                │     News     │
       │  ┌─────────────┤ id (PK)      │
       │  │             │ category_id  │
       ▼  ▼             │ title/content│
┌──────────────┐        │ views        │
│  UserToken   │        │ publish_time │
│ token (U)    │        └──────┬───────┘
│ expires_at   │               │
└──────────────┘     ┌─────────┴─────────┐
                     ▼                   ▼
              ┌──────────────┐    ┌──────────────┐
              │   Favorite   │    │   History    │
              │ user_id (FK) │    │ user_id (FK) │
              │ news_id (FK) │    │ news_id (FK) │
              │ (user+news U)│    │ view_time    │
              └──────────────┘    └──────────────┘
```

关键索引：`user.username / phone / email` 唯一；`user_token.token` 唯一（每请求都校验）；`news.category_id`、`news.publish_time`（最频繁的查询与排序）；`favorite (user_id, news_id)` 联合唯一。

---

## 启动方式

### 环境要求

- Python 3.10+
- MySQL 8.0+
- Redis 7.0+

### 1. 配置环境变量

复制模板并填入真实值（`.env` 不会被提交）：

```bash
cp .env.example .env
```

`.env` 涵盖数据库、Redis、QQ 邮箱 SMTP、阿里云短信等密钥。

### 2. 安装依赖并建表

```bash
pip install fastapi "uvicorn[standard]" "sqlalchemy>=2.0" aiomysql "redis[hiredis]" "passlib[bcrypt]" "pydantic>=2.0" python-multipart
```

在 MySQL 中创建数据库后，用 SQLAlchemy 初始化表结构：

```python
import asyncio
from config.db_conf import async_engine
from models.base import Base
import models.users, models.news, models.favorite, models.history  # 注册所有表

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init_db())
```

### 3. 启动后端

```bash
# 开发模式（热重载）
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

启动后访问交互式文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 4. 启动前端

```bash
cd xwzx-news
npm install
npm run dev
```

> 说明：实际运行前需补充 `.env` 配置（数据库、Redis、邮箱、短信等）。未配置邮箱 / 短信密钥时，验证码会自动回退到控制台打印，方便本地联调。
