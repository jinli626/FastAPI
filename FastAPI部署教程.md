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

> 报错如何解决： 错误:1 http://mirrors.tuna.tsinghua.edu.cn/ubuntu   清华源返回 403 禁止访问 
>
> ★ 换源即可解决，按顺序执行下面命令：https://www.doubao.com/thread/x8fccc25a6edb8145b3a526a8df4a5418

1.备份原有源文件 

```bash
sudo cp /etc/apt/sources.list /etc/apt/sources.list.bak
```

2.替换为 Ubuntu 官方源

```bash
sudo tee /etc/apt/sources.list << EOF
deb http://archive.ubuntu.com/ubuntu/ jammy main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu/ jammy-updates main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu/ jammy-security main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu/ jammy-backports main restricted universe multiverse
EOF
```

> 注意：手动输入的时候要原封不动地输入 不能带任何符号 比如"<"  改完记得拍快照 命名为"替换为 Ubuntu 官方源"

3.更新软件源并修复依赖

```bash
sudo apt update
sudo apt --fix-broken install -y
```

4.再次验证安装 

```bash
sudo apt install -y openssh-server curl open-vm-tools open-vm-tools-desktop
```

> 先执行：sudo apt install net-tools  然后ifconfig

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
sudo vmhgfs-fuse .host:/ /mnt/hgfs -o allow_other
```

验证（看到项目内容即成功）：

```bash
cd /mnt/hgfs/news-info/news-info-backend
ls
```

> 下文统一用 `/mnt/hgfs/news-info/news-info-backend` 作为后端目录，若你的共享目录名不同，请自行替换。

---

## 三、安装 Docker 和 Docker Compose（为构建镜像和启动容器做准备）

### 1. 安装 Docker

```bash
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

> 执行完 `usermod` 后需要重新登录 VM（退出 SSH 再重连）才能免 sudo 使用 docker。

### 2. 安装 Docker Compose V2

Ubuntu 18.04 的 apt 源中 docker-compose 版本太旧（1.17），不支持本项目的配置语法。需要手动安装新版。

**安装方法：从项目中复制（作者已提供二进制文件）**

项目目录中已包含 `docker-compose-linux-x86_64` 文件，直接复制即可：

```bash
sudo cp /mnt/hgfs/news-info/news-info-backend/docker-compose-linux-x86_64 /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

> 如果系统中已有旧版 docker-compose，先卸载：`sudo apt-get remove -y docker-compose`，然后执行 `hash -r` 刷新命令缓存。

```bash
docker-compose --version
```

应显示 **Docker Compose version v2.24.0**

### 3.配置 Docker 镜像加速

> （必须，否则无法拉取镜像），国内网络无法直接访问 Docker Hub，必须配置镜像加速：

```bash
sudo mkdir -p /etc/docker

sudo tee /etc/docker/daemon.json <<-'EOF'
{
    "registry-mirrors": [
        "https://docker.1ms.run",
        "https://docker.1panel.live",
        "https://docker.m.ixdev.cn",
        "https://hub.rat.dev",
        "https://docker.xuanyuan.me"
    ]
}
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker
```

> 换镜像源的网站：https://status.1panel.top/   参考资料：https://bbs.fit2cloud.com/t/topic/5886

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

> sudo apt install -y vim 

1.编辑Netplan配置文件

方法一：

```shell
sudo vim /etc/netplan/01-network-manager-all.yaml 
```

或者直接FinalShell打开

```sheel
sudo chmod 777 01-network-manager-all.yaml 
```

复制下列配置格式到01-network-manager-all.yaml

需要变动2个选项

- ens33下的addresses

  - ![image-20260116201958436](C:/Users/刘祥兴/Desktop/Linux/Linux/static/imgs/image-20260116201958436.png)
  - 虚拟网络编辑器
  - ![image-20260116202028742](C:/Users/刘祥兴/Desktop/Linux/Linux/static/imgs/image-20260116202028742.png)

  - addresses中的ip前3必须和NAT保持一致：192.168.x.y/24
  - x和NAT中的一致
  - y自己定，不要选0,255，物理机相同的数

- ens33下的gateway4

  - 固定192.168.x.2
  - x和NAT一样

```yaml
network:
  version: 2  # Netplan 版本（固定为 2）
  renderer: NetworkManager  # 显式指定使用 NetworkManager（可选，但推荐）
  ethernets:
    ens33:  # 替换为你的实际网卡名称（通过 ifconfig 查看）
      dhcp4: no  # 禁用 DHCP，启用静态 IP（必须）
      addresses: 
        - 192.168.16.99/24  # 静态 IP + 子网掩码（24 对应 255.255.255.0）
      gateway4: 192.168.16.2  # 网关
      nameservers:  # DNS 服务器（用于解析域名）
          addresses: [114.114.114.114, 8.8.8.8]  # 国内常用 DNS（可选替换为其他）
```

方法二：

> 解决办法（直接用一键写入命令，彻底避免格式问题）
>
> 不用再手动复制粘贴了，直接在终端执行下面这条命令，就能把格式完全正确的配置一次性写入文件

```bash
sudo tee /etc/netplan/01-network-manager-all.yaml <<-'EOF'
# Let NetworkManager manage all devices on this system
network:
  version: 2
  renderer: NetworkManager
  ethernets:
    ens33:
      dhcp4: no
      addresses:
        - 192.168.248.99/24
      routes:
        - to: default
          via: 192.168.248.2
      nameservers:
        addresses:
          - 114.114.114.114
          - 8.8.8.8
EOF
```

![1781500570607](C:\Users\刘祥兴\AppData\Roaming\Typora\typora-user-images\1781500570607.png)

网络适配器改为NAT模式

2.应用配置

```shell
sudo netplan apply
```

> ★ 注意： 执行 `sudo netplan apply` 时，系统会**重新配置网络接口**   连接会突然断开
>
> 答疑链接：https://www.doubao.com/thread/xc9e3824487aa8f8fa76ad1f0aa4968bf

- 恢复连接的方法

1. **关闭当前断开的 SSH 窗口**，重新打开 FinalShell
2. 新建一个连接，用**新的静态 IP `192.168.248.99`** 连接你的虚拟机
3. 输入你的用户名和密码，就能重新连上了

- 为什么会断开？

   你执行 `sudo netplan apply` 时，系统会**重新配置网络接口**：

1. 你的旧 IP `192.168.248.131` 会被断开
2. 新配置的静态 IP `192.168.248.99` 会生效
3. 配置生效的瞬间，SSH 连接就会被强制断开，这是完全正常的

3.测试

```shell
ifconfig查看ens33已经改变
ping www.baidu.com
```

---

## 五、配置后端环境变量

进入后端目录，复制环境变量模板：

```bash
cd /mnt/hgfs/news-info/news-info-backend
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

> ★ 注意requirements.txt只需要包含项目所需的依赖 多余的不需要 否则会影响构建镜像的速度

### Q：输入什么命令才能提取准确的requirements.txt 

#### A：用 `pipreqs` 自动提取（不会包含无关依赖）

这个工具只会扫描你项目代码里 `import` 过的库，自动生成 `requirements.txt`，不会把虚拟环境里所有库都导出来。

1. **安装 `pipreqs`**

   ```powershell
   pip install pipreqs
   ```

2. **进入你的项目目录**

   ```
   cd D:\项目练习\FastAPI项目练习\news-info-backend
   ```

3. **生成 `requirements.txt`**

   ```
   pipreqs . --encoding=utf8 --force
   ```

   - `.` 表示在当前目录生成
   
   - `--force` 表示如果文件已存在则覆盖
   
   - `--encoding=utf8` 避免中文乱码
   
     > ★ 注意：要用claude模型检查一些依赖是否正确  缺了什么 少了什么 多了什么 并进行修改

进入后端目录：

```bash
cd /mnt/hgfs/news-info/news-info-backend
```

构建并启动（用基础配置即可，会把后端暴露在 `0.0.0.0:8000`，方便 Windows 前端访问）：

```bash
sudo docker-compose up -d --build
```

> 说明：项目里还有一个 `docker-compose.prod.yml`，那是**正式上线**用的（后端只绑 127.0.0.1、由 nginx 反代）。
> VM + Windows 前端这种调试场景**不要**叠加它，否则 Windows 访问不到后端。

查看容器：

```bash
sudo docker-compose ps
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
sudo docker-compose exec app python scripts/init_db.py
```

默认后台管理员（创建完成后请尽快修改密码）：

```text
账号：admin
密码：admin123
```

### 2. 执行幂等迁移（补充 news.status 列）

```bash
sudo docker-compose exec app python scripts/run_migration.py
```

### 3. 检查数据表是否创建成功

```bash
sudo docker-compose exec mysql sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" news_app -e "show tables;"'
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
sudo docker pull m.daocloud.io/docker.io/python:3.12-slim
sudo docker pull m.daocloud.io/docker.io/mysql:8.0
sudo docker pull m.daocloud.io/docker.io/redis:7-alpine
```

> 彻底重置 Docker 构建环境： sudo docker system prune -a 
>
> 最后要： sudo docker-compose up -d --build  
>
> ★ 要在对应文件修改名称 eg：FROM m.daocloud.io/docker.io/python:3.12-slim

如果仍失败，换镜像加速地址或配置 HTTP 代理。

https://www.doubao.com/thread/x26583b077aa48af29410abdf35abf5ec

https://www.doubao.com/thread/x6004e3f607f488e8a406e9d5cc82994d

![1781594038301](C:\Users\刘祥兴\AppData\Roaming\Typora\typora-user-images\1781594038301.png)

### 2. 数据表不存在 / 接口报表不存在

重新执行建表与迁移：

```bash
sudo docker-compose exec app python scripts/init_db.py
sudo docker-compose exec app python scripts/run_migration.py
```

检查表：

```bash
sudo docker-compose exec mysql sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" news_app -e "show tables;"'
```

### 3. 后端连不上数据库（Connection refused / Access denied）

```text
1. 确认 .env 里 DB_HOST=mysql、REDIS_HOST=redis（不是 localhost）
2. 确认 DB_PASSWORD 与 REDIS_PASSWORD 是第一次启动时设置的值
   —— 这两个值在 mysql/redis 容器“第一次创建”时写入数据卷，后面改 .env 不会自动改卷里的密码
3. 若中途改过密码，需重建数据卷：
   sudo docker-compose down -v   # 注意：-v 会清空数据库数据！
   sudo docker-compose up -d --build
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
sudo docker-compose down
sudo docker-compose up -d --build
```

### 6. 查看后端日志（排错首选）

```bash
sudo docker-compose logs -f app
```

### 7. 使用docker拉取MySQL镜像很慢或者总是超时

> 解决方法：https://blog.csdn.net/Really_gxy/article/details/145591987

但是还会报错，如图

![1781536561946](C:\Users\刘祥兴\AppData\Roaming\Typora\typora-user-images\1781536561946.png)

出错原因以及解决方法：https://www.doubao.com/thread/x793237dc4d2e83148252cf38985f7edf

重点看第一步：强制修复 DNS（核心必做）

复制整条命令执行，覆盖系统 DNS 配置，使用国内稳定公共 DNS

```bash
sudo tee /etc/resolv.conf <<-'EOF'
nameserver 223.5.5.5
nameserver 114.114.114.114
nameserver 8.8.8.8
EOF
```

 验证解析是否恢复正常： 

```bash
nslookup baidu.com
```

 能返回 IP 代表 DNS 修复完成

最后再执行：

```bash
docker pull m.daocloud.io/docker.io/mysql:8
```

后面有什么相同类型的报错

都用：docker pull m.daocloud.io/docker.io/...前缀

比如：docker pull m.daocloud.io/docker.io/python:3.12-slim

> 先单独下载好 Python 镜像，再执行 compose 构建，避免构建时临时下载超时

> ★★★ 非常重要的一步：
>
> 在docker-compose.yaml里面将image: mysql:8 改为 image: m.daocloud.io/docker.io/mysql:8

### 8. 版本不兼容，pip依赖解析失败 

>  一次性列出所有问题 + 完整修正后的 requirements.txt 

##### eg：现存 4 个致命问题

1. **ConfigParser 仅 Python2 库，Python3 内置 configparser，包名冲突无法安装**

2. **HTMLParser==0.0.2 是废弃冷门包，Python3 自带 html.parser 标准库，没必要安装**

3. **thread==2.0.6 为 Python2 旧库，Python3 用内置_thread，此包会报错**

4. 已修复：docutils==0.22 兼容 Sphinx==9.1.0；已删除 xmlrpclib；无 jnius 冲突

    修正完成、无冲突可用完整清单（直接全替换你的文件） 

   ```txt
   aliyun_python_sdk_core==2.16.0
   attr==0.3.2
   contextlib2==21.6.0
   cryptography==49.0.0
   docutils==0.22
   fastapi==0.137.0
   importlib_metadata==8.7.1
   ipython==8.12.3
   ...
   ```

   > https://www.doubao.com/thread/xa75648a5361986d89bf0c09ff1436569

![1781596107140](C:\Users\刘祥兴\AppData\Roaming\Typora\typora-user-images\1781596107140.png)

- 这是什么意思 这六个 

> 解答：https://www.doubao.com/thread/x3643b6ad16af8c7299f2df3ec0f09d3f

### 9. 后端启动时报 No module named 'cache'

> 解决方案：https://www.doubao.com/thread/xc5ca80a5673b8fb9a4764534c4bea4a6

最后执行：

```bash
sudo docker-compose down 
sudo docker-compose up -d --build 
```

### 10. 部署完之后 发现之前的代码报错 

解决方案：在编译器改完之后 在VM中执行：docker-compose up -d --build  重启后端 

改完的代码即可生效

---

## 十一、最简部署命令汇总

### 1. 后端（在 VM 上）

```bash
cd /mnt/hgfs/FastAPI项目练习/news-info-backend

cp .env.docker.example .env
nano .env                       # 改 DB_PASSWORD、REDIS_PASSWORD（其余可选）

sudo docker-compose up -d --build

sudo docker-compose exec app python scripts/init_db.py
sudo docker-compose exec app python scripts/run_migration.py

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

------

## 十二、取消部署命令汇总

### 1. 后端（VM 虚拟机内执行，项目目录不变）

先进入后端项目根目录

```bash
cd /mnt/hgfs/news-info/news-info-backend
```

#### ① 临时停止服务（保留容器、数据库数据，可快速重启）

```bash
sudo docker-compose stop
```

恢复上线：`sudo docker-compose up -d --build`

#### ② 销毁容器 / 网络（保留数据库持久化数据，常用重置）

```bash
sudo docker-compose down
```

#### ③ 彻底清理部署（删除容器、镜像、全部数据库数据，不可逆）

> 操作前建议先备份数据库，所有用户、收藏数据会全部清空

```bash
sudo docker-compose down -v --rmi all --remove-orphans
```

#### 补充：单独停止 / 重启后端应用容器（不影响 Redis、MySQL）

```bash
# 仅停止后端服务
sudo docker-compose stop app
# 重启后端加载新代码
sudo docker-compose up -d --build app
```

------

### 2. 前端（Windows 本地终端）

#### 用户端停止

1. 找到运行 `npm run dev` 的终端窗口
2. 快捷键 `Ctrl + C` 终止前端开发服务

#### 管理端停止

1. 找到运行管理端的终端窗口
2. 快捷键 `Ctrl + C` 终止开发服务

#### 彻底清理前端依赖（可选，后续重新 install）

```bash
# 用户端清理
cd news-info-frontend
rmdir /s /q node_modules package-lock.json

# 管理端清理
cd news-info-admin
rmdir /s /q node_modules package-lock.json
```

------

### 3. 完整永久下线整套项目（全流程）

​    1.执行后端彻底清理命令：

```
cd /mnt/hgfs/news-info/news-info-backend
sudo docker-compose down -v --rmi all --remove-orphans
```

​    2.Windows 端关闭所有前端 `npm run dev` 终端

​    3.额外线上收尾（云服务器公网部署时）

- 删除域名解析记录，禁止外网访问
- 若做过 ICP 备案，前往云厂商后台注销网站备案
- 不需要服务器时，在云控制台释放 ECS 实例停止扣费

------

### 4. 查看容器运行状态完整命令

#### 1. 基础查看：列出**正在运行**的容器

在 VM 虚拟机终端执行：

```bash
sudo docker ps
```

判断规则：

- 有 `news-info-app`、`news-info-mysql`、`news-info-redis` 出现 → 容器**还在运行**，没关闭
- 列表空白 / 无这三个容器 → 容器已经停止并销毁

#### 2. 查看所有容器（包含已停止的）

如果执行 `docker-compose down` 后想确认旧容器是否彻底删除：

```bash
sudo docker ps -a
```

- `-a` 参数：显示全部容器（运行中 + 已停止）
- 看不到 `news-info-xxx` 相关容器 = 彻底销毁成功

#### 3. 只看你项目的容器（精准过滤，推荐）

进入后端项目目录后执行，只筛选当前 compose 管理的容器：

```bash
cd /mnt/hgfs/FastAPI项目练习/news-info-backend
sudo docker-compose ps
```

状态标识解读：

- `Up xx seconds`：正在运行
- `Exited (0) x minutes ago`：已停止但未删除
- 无任何输出：容器全部销毁干净

#### 4. 实时查看后端日志（辅助验证服务是否关停）

```bash
sudo docker logs -f news-info-app
```

- 报错 `No such container` = 后端容器已删除
- 持续输出日志 = 容器仍在后台运行

------

#### 配套操作对照

1. 执行 

   ```bash
   sudo docker-compose stop
   ```

   ```bash
   docker ps
   ```

    看不到容器，

   ```
   docker ps -a
   ```

    还能看到（只是停止，未删除）

2. 执行 

   ```bash
   sudo docker-compose down
   ```

    后：

   ```bash
   docker ps
   ```

   ```bash
   docker ps -a
   ```

    都看不到项目容器，完全关闭销毁