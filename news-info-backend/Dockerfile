# 使用官方 Python 3.12 slim 作为基础镜像 使用DaoCloud加速镜像 Python 3.12 slim
FROM m.daocloud.io/docker.io/python:3.12-slim

# 设置工作目录
WORKDIR /app

# 环境变量
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 使用国内镜像加速（在国内服务器上构建更快，可在 build 时用 --build-arg 覆盖）
ARG APT_MIRROR=https://mirrors.aliyun.com
ARG PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
ARG PIP_TRUSTED_HOST=mirrors.aliyun.com

# 把 Debian 软件源切到国内镜像
RUN if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        sed -i "s|http://deb.debian.org/debian|${APT_MIRROR}/debian|g" /etc/apt/sources.list.d/debian.sources && \
        sed -i "s|http://security.debian.org/debian-security|${APT_MIRROR}/debian-security|g" /etc/apt/sources.list.d/debian.sources; \
    elif [ -f /etc/apt/sources.list ]; then \
        sed -i "s|http://deb.debian.org/debian|${APT_MIRROR}/debian|g" /etc/apt/sources.list && \
        sed -i "s|http://security.debian.org/debian-security|${APT_MIRROR}/debian-security|g" /etc/apt/sources.list; \
    fi

# 安装系统依赖（aiomysql / cryptography 等编译需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    pkg-config \
    default-libmysqlclient-dev \
    default-jdk \
    && rm -rf /var/lib/apt/lists/*

# 先拷贝依赖文件并安装，充分利用 Docker 层缓存
COPY requirements.txt .
RUN pip config set global.index-url ${PIP_INDEX_URL} \
    && pip config set global.trusted-host ${PIP_TRUSTED_HOST} \
    && pip install --no-cache-dir --upgrade pip cython \
    && pip install --no-cache-dir -r requirements.txt

# 拷贝应用代码
COPY . .

# 创建运行期需要的目录（日志、上传文件落地）
RUN mkdir -p logs static/uploads

# 创建非 root 用户运行应用
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# 暴露端口
EXPOSE 8000

# 健康检查（根路由返回 200；slim 镜像无 curl，用 python urllib）
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${API_PORT:-8000}/')" || exit 1

# 启动命令（main.py 仅暴露 app 对象，用 uvicorn 拉起）
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${API_PORT:-8000}"]
