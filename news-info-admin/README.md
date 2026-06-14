# 新闻管理后台（news-info-admin）

基于 **Vue 3 + Vite + Vue Router + Pinia + Axios + Element Plus** 的新闻信息管理端，对接 `news-info-backend` 的管理接口。

## 功能

- 管理员登录 / 鉴权（Token，路由守卫，401 自动退出）
- 数据看板：新闻总数 / 各状态数 / 总浏览量 / 分类数 / 今日新增 + 分类分布饼图 + 热门新闻柱图（ECharts）
- 新闻管理：列表（分页 + 标题搜索 + 分类/状态筛选）、发布、编辑、删除、一键发布 / 下架
- 分类管理：新增 / 编辑 / 删除（含排序，分类下有新闻时禁止删除）
- 富文本正文（WangEditor）+ 封面图上传

## 技术约定

- 富文本编辑器：WangEditor v5，正文以 HTML 存入后端 `content` 字段
- 统一响应：后端返回 `{ code, message, data }`，axios 拦截器自动解包 `data`、统一错误提示、401 跳登录
- 开发态走 Vite 代理：`/api`、`/static` 转发到 `http://127.0.0.1:8000`（见 `vite.config.js`），生产环境改 `.env.production` 的 `VITE_API_BASE_URL`

## 目录结构

```
src/
├── api/        # 接口封装（auth/news/category/upload/stats）
├── components/ # 公共组件（RichEditor 富文本、ImageUpload 封面上传）
├── config/     # api 基础地址
├── layout/     # 后台布局（侧边栏/顶栏/面包屑）
├── router/     # 路由 + 守卫
├── store/      # Pinia（admin 模块）
├── utils/      # request 封装、auth-token、format
└── views/      # 页面（login/dashboard/news/category/error）
```

## 启动

> 前提：先启动后端，并完成管理员初始化（见 `news-info-backend` 下的脚本）。

```bash
# 1. 初始化后端（在 news-info-backend 目录，仅首次）
python scripts/init_admin.py            # 创建 admin 表 + 种子账号 admin / admin123
#    并在 MySQL 中执行 scripts/add_news_status.sql 给 news 表加 status 字段

# 2. 启动后端
uvicorn main:app --reload               # http://127.0.0.1:8000

# 3. 启动管理端（在 news-info-admin 目录）
npm install
npm run dev                             # 默认 http://127.0.0.1:5174
```

默认登录账号：**admin / admin123**（请尽快修改）。

## 构建

```bash
npm run build       # 产物在 dist/
npm run preview     # 本地预览构建产物
```
