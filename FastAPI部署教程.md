# FastAPI 新闻资讯项目 部署教程

# 写在前面

后端方面
1. 自行准备好 VMware 虚拟机和 Ubuntu 系统（推荐 20.04 / 22.04），VMware 软件、Ubuntu 镜像及安装教程可自行准备或联系项目作者。
2. VMware 网络设置：编辑 → 虚拟网络编辑器 → NAT 模式，确保 DHCP 分配正常。
3. Docker 需要联网拉取基础镜像（python、mysql、redis），国内需配置镜像加速。
4. 初始化数据库后，建议检查表是否成功创建（命令见下方）。

> 本项目后端是 **FastAPI + MySQL 8 + Redis**，全部通过 Docker Compose 一键拉起，**服务器上无需另外安装 MySQL / Redis**。

# 部署简介

```
后端：放在 VMware Ubuntu 虚拟机中，通过 Docker Compose 自行构建镜像并启动容器（FastAPI + MySQL + Redis）
前端：放在 Windows 机器上，直接使用 npm run dev 启动（用户端 + 管理端）
```

整体部署链路：

```text
Windows 保存完整项目
        ↓
VMware 设置 Windows 共享文件夹
        ↓
Ubuntu VM 挂载 Windows 共享目录
        ↓
Ubuntu VM 安装 Docker 和 Docker Compose
        ↓
Ubuntu VM 配置 Docker 镜像加速
        ↓
Ubuntu VM 进入后端目录，cp .env.docker.example .env 并填写
        ↓
Ubuntu VM 执行 docker compose up -d --build
        ↓
Ubuntu VM 执行建表脚本 init_db.py、迁移脚本 run_migration.py
        ↓
Windows 本地分别启动用户端前端和管理端前端
```

---

## 一、环境要求

### Ubuntu VM

| 软件 | 说明 |
|---|---|
| VMware Workstation | 运行 Ubuntu 虚拟机 |
| Ubuntu 20.04+ | 推荐 20.04 或 22.04 |
| Docker | 构建和运行后端容器 |
| Docker Compose V2 | 编排后端、MySQL、Redis |

### Windows（前端）

| 软件 | 说明 |
|---|---|
| Node.js 16+ | 运行两个 Vue/Vite 前端 |
| npm | 安装前端依赖、启动 dev server |

---

## 二、安装 SSH、VMware Tools 和共享文件夹

### 1. 安装 SSH 和 VMware Tools

> SSH 安装完成后，可以在 Windows 上通过终端 SSH 连接 VM，方便复制粘贴命令。
> 建议用编辑器打开项目，在编辑器的终端里 SSH 连接 VM。

在 Ubuntu VM 中执行：

```bash
sudo apt-get update
sudo apt-get install -y openssh-server curl open-vm-tools open-vm-tools-desktop
sudo systemctl start ssh
sudo systemctl enable ssh
sudo reboot
```

查看 VM IP：

```bash
ip addr show
```

Windows 连接 VM：

```bash
ssh 用户名@VM的IP地址
```

### 2. 设置 VMware 共享文件夹

在 VMware 中设置：

```text
虚拟机设置
    ↓
选项
    ↓
共享文件夹
    ↓
添加 Windows 上的 FastAPI项目练习 项目目录
```

Ubuntu 中挂载：

```bash
sudo mkdir -p /mnt/hgfs
sudo vmhgfs-fuse .host:/ /mnt/hgfs -o allow_other,nonempty
```

验证（看到项目内容即成功）：

```bash
cd /mnt/hgfs/FastAPI项目练习/news-info-backend
ls
```

> 下文统一用 `/mnt/hgfs/FastAPI项目练习/news-info-backend` 作为后端目录，若你的共享目录名不同，请自行替换。

---

## 三、安装 Docker 和 Docker Compose（为构建镜像和启动容器做准备）

### 1. 安装 Docker（含 Compose V2 插件，最省心）

```bash
curl -fsSL https://get.docker.com | sudo bash
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

> 执行完 `usermod` 后需要重新登录 VM（退出 SSH 再重连）才能免 sudo 使用 docker。

验证：

```bash
docker --version
docker compose version   # 能显示版本号即说明 Compose V2 已就绪
```

> 注意：本项目用的是 Docker Compose **V2**，命令是 `docker compose`（中间是空格），不是老版的 `docker-compose`。
> 如果你的系统只有老版 `docker-compose`，把下文命令里的 `docker compose` 改成 `docker-compose` 即可。

### 2. 配置 Docker 镜像加速（必须，否则国内拉不到镜像）

```bash
sudo mkdir -p /etc/docker

sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me",
    "https://docker.m.daocloud.io"
  ]
}
EOF

sudo systemctl daemon-reload
sudo systemctl restart docker
```

---

## 四、设置 VM 静态 IP（推荐）

固定 IP 后，前端配置不用反复改 VM 地址（VM 地址默认动态分配，会发生改变）。

先查看当前 IP 和网卡名：

```bash
ip addr show
```

**如果系统使用 NetworkManager（Ubuntu 桌面版常见）：**

```bash
# 查看连接名称
nmcli con show

# 设置静态 IP（根据实际网段和连接名修改）
sudo nmcli con mod "有线连接 1" ipv4.method manual ipv4.addresses 你的IP/24 ipv4.gateway 网关IP ipv4.dns "8.8.8.8,114.114.114.114"
sudo nmcli con up "有线连接 1"
```

**如果系统使用 netplan（Ubuntu Server 常见）：**

```bash
sudo nano /etc/netplan/01-netcfg.yaml
```

```yaml
network:
  version: 2
  ethernets:
    ens33:
      dhcp4: no
      addresses:
        - 你的IP/24
      gateway4: 网关IP
      nameservers:
        addresses: [8.8.8.8, 114.114.114.114]
```

```bash
sudo netplan apply
```

---

## 五、配置后端环境变量

进入后端目录，复制环境变量模板：

```bash
cd /mnt/hgfs/FastAPI项目练习/news-info-backend
cp .env.docker.example .env
nano .env
```

关键配置说明：

| 配置项 | 说明 |
|---|---|
| `API_PORT` | 后端端口，默认 `8000` |
| `DB_USER` | 数据库用户，固定 `root` |
| `DB_PASSWORD` | **同时是 MySQL 容器的 root 密码**，务必改成强密码 |
| `DB_HOST` | Docker 内部服务名，固定 `mysql`（不是 localhost！） |
| `DB_PORT` | Docker 内部端口，固定 `3306` |
| `DB_NAME` | 数据库名，默认 `news_app` |
| `REDIS_HOST` | Docker 内部服务名，固定 `redis` |
| `REDIS_PORT` | 默认 `6379` |
| `REDIS_PASSWORD` | **同时是 Redis 容器的密码**，务必改成强密码 |
| `SMTP_USER` / `SMTP_PASSWORD` | QQ 邮箱及 16 位授权码（发邮件验证码用，可选） |
| `ALIBABA_ACCESS_KEY_ID` 等 | 阿里云短信密钥（发短信验证码用，可选） |

> ⚠️ 最重要的一点：`DB_HOST=mysql`、`REDIS_HOST=redis` 用的是 compose 里的**服务名**，容器之间靠它互相访问。
> 千万不要填成 `localhost`（容器里的 localhost 指的是它自己，连不到数据库）。
> 本项目的 `docker-compose.yml` 已经在 app 服务里强制固定了这两个地址，即使填错也能兜底，但建议按模板填对。

---

## 六、构建镜像并启动后端服务

进入后端目录：

```bash
cd /mnt/hgfs/FastAPI项目练习/news-info-backend
```

构建并启动（用基础配置即可，会把后端暴露在 `0.0.0.0:8000`，方便 Windows 前端访问）：

```bash
sudo docker compose up -d --build
```

> 说明：项目里还有一个 `docker-compose.prod.yml`，那是**正式上线**用的（后端只绑 127.0.0.1、由 nginx 反代）。
> VM + Windows 前端这种调试场景**不要**叠加它，否则 Windows 访问不到后端。

查看容器：

```bash
sudo docker compose ps
```

正常应看到 3 个容器都是 `running / healthy`：

```text
news-info-app
news-info-mysql
news-info-redis
```

---

## 七、初始化数据库

> 本项目应用启动时**不会自动建表**，首次部署必须执行下面的脚本（可重复执行，已存在会自动跳过）。

### 1. 建表 + 创建默认管理员

```bash
sudo docker compose exec app python scripts/init_db.py
```

默认后台管理员（创建完成后请尽快修改密码）：

```text
账号：admin
密码：admin123
```

### 2. 执行幂等迁移（补充 news.status 列）

```bash
sudo docker compose exec app python scripts/run_migration.py
```

### 3. 检查数据表是否创建成功

```bash
sudo docker compose exec mysql sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" news_app -e "show tables;"'
```

正常会看到这些表：

```text
admin
admin_token
favorite
history
news
news_category
user
user_token
```

---

## 八、验证后端

健康检查（返回 `{"message":"Hello FastAPI"}` 即成功）：

```bash
curl http://localhost:8000/
```

Windows 浏览器访问：

```text
http://VM的IP:8000/
http://VM的IP:8000/docs        # API 接口文档
```

> 如果 Windows 访问不到，先在 VM 放行端口：
> ```bash
> sudo ufw allow 8000
> sudo ufw reload
> ```

---

## 九、Windows 启动前端

需要启动两个前端：

```text
news-info-frontend    用户端（移动端，xwzx-news）
news-info-admin       管理端（后台）
```

### 1. 修改前端的后端地址（指向 VM）

**用户端 news-info-frontend：** 打开 `news-info-frontend/src/config/api.js`，把 `baseURL` 改成 VM 后端地址：

```js
export const apiConfig = {
  baseURL: 'http://VM的IP:8000',   // 原来是 http://127.0.0.1:8000
}
```

**管理端 news-info-admin：** 打开 `news-info-admin/vite.config.js`，把 proxy 的 target 改成 VM 后端地址：

```js
proxy: {
  '/api':    { target: 'http://VM的IP:8000', changeOrigin: true },
  '/static': { target: 'http://VM的IP:8000', changeOrigin: true },
}
```

### 2. 启动用户端

Windows 打开终端：

```bash
cd news-info-frontend
npm install
npm run dev
```

默认访问：

```text
http://localhost:5173
```

### 3. 启动管理端

Windows 新开一个终端：

```bash
cd news-info-admin
npm install
npm run dev
```

默认访问：

```text
http://localhost:5174
```

后台默认账号：

```text
账号：admin
密码：admin123
```

---

## 十、故障排查

### 1. Docker 拉取镜像失败

检查镜像加速：

```bash
docker info
```

测试拉取（拉取速度快代表成功）：

```bash
sudo docker pull python:3.12-slim
sudo docker pull mysql:8.0
sudo docker pull redis:7-alpine
```

如果仍失败，换镜像加速地址或配置 HTTP 代理。

### 2. 数据表不存在 / 接口报表不存在

重新执行建表与迁移：

```bash
sudo docker compose exec app python scripts/init_db.py
sudo docker compose exec app python scripts/run_migration.py
```

检查表：

```bash
sudo docker compose exec mysql sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" news_app -e "show tables;"'
```

### 3. 后端连不上数据库（Connection refused / Access denied）

```text
1. 确认 .env 里 DB_HOST=mysql、REDIS_HOST=redis（不是 localhost）
2. 确认 DB_PASSWORD 与 REDIS_PASSWORD 是第一次启动时设置的值
   —— 这两个值在 mysql/redis 容器“第一次创建”时写入数据卷，后面改 .env 不会自动改卷里的密码
3. 若中途改过密码，需重建数据卷：
   sudo docker compose down -v   # 注意：-v 会清空数据库数据！
   sudo docker compose up -d --build
```

### 4. 前端请求后端失败

检查：

```text
1. VM 后端是否启动（docker compose ps）
2. Windows 是否能访问 http://VM的IP:8000/
3. 用户端 src/config/api.js 的 baseURL 是否是 http://VM的IP:8000
4. 管理端 vite.config.js 的 proxy target 是否是 http://VM的IP:8000
5. Ubuntu 防火墙是否拦截 8000 端口
```

Ubuntu 放行端口：

```bash
sudo ufw allow 8000
sudo ufw reload
```

### 5. 修改 .env 后让配置生效

```bash
sudo docker compose down
sudo docker compose up -d --build
```

### 6. 查看后端日志（排错首选）

```bash
sudo docker compose logs -f app
```

---

## 十一、最简部署命令汇总

### 1. 后端（在 VM 上）

```bash
cd /mnt/hgfs/FastAPI项目练习/news-info-backend

cp .env.docker.example .env
nano .env                       # 改 DB_PASSWORD、REDIS_PASSWORD（其余可选）

sudo docker compose up -d --build

sudo docker compose exec app python scripts/init_db.py
sudo docker compose exec app python scripts/run_migration.py

curl http://localhost:8000/     # 返回 {"message":"Hello FastAPI"} 即成功
```

### 2. 前端（在 Windows 上）

用户端：

```bash
cd news-info-frontend
# 先改 src/config/api.js 的 baseURL 为 http://VM的IP:8000
npm install
npm run dev
```

管理端：

```bash
cd news-info-admin
# 先改 vite.config.js 的 proxy target 为 http://VM的IP:8000
npm install
npm run dev
```

访问：

```text
用户端：http://localhost:5173
管理端：http://localhost:5174   （账号 admin / 密码 admin123）
后端健康：http://VM的IP:8000/
后端接口文档：http://VM的IP:8000/docs
```
