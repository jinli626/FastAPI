#!/bin/bash

# news-info-backend 生产部署脚本
# 在服务器的 news-info-backend/ 目录下执行： bash scripts/deploy.sh
# 前置条件：已安装 Docker + Docker Compose，且已 cp .env.docker.example .env 并填好真实值

set -e

COMPOSE_FILES="${COMPOSE_FILES:-"-f docker-compose.yml -f docker-compose.prod.yml"}"
API_PORT="${API_PORT:-8000}"
HEALTH_ENDPOINT="http://localhost:${API_PORT}/"
TIMEOUT=120

echo "==> 开始部署 news-info-backend"
echo "    Compose 文件: $COMPOSE_FILES"
echo "    API 端口:     $API_PORT"
echo "    健康检查:     $HEALTH_ENDPOINT"

if [ ! -f .env ]; then
    echo "错误：当前目录没有 .env 文件。请先执行： cp .env.docker.example .env 并填入真实值。"
    exit 1
fi

check_health() {
    local timeout=$1
    echo "==> 等待应用健康检查..."
    while [ "$timeout" -gt 0 ]; do
        if curl -fs "$HEALTH_ENDPOINT" >/dev/null 2>&1; then
            echo "    应用已就绪。"
            return 0
        fi
        sleep 5
        timeout=$((timeout - 5))
        echo "    仍在等待... 剩余 ${timeout}s"
    done
    echo "    应用未在规定时间内就绪。"
    return 1
}

show_logs() {
    echo "==> 最近的服务日志："
    docker compose $COMPOSE_FILES logs --tail=80
}

main() {
    echo "==> 构建并启动容器..."
    docker compose $COMPOSE_FILES up -d --build

    echo "==> 初始化数据库（建表 + 播种管理员，可重复执行）..."
    docker compose $COMPOSE_FILES exec -T app python scripts/init_db.py

    echo "==> 执行幂等迁移（补充 news.status 列等）..."
    docker compose $COMPOSE_FILES exec -T app python scripts/run_migration.py

    echo "==> 容器状态："
    docker compose $COMPOSE_FILES ps

    if ! check_health "$TIMEOUT"; then
        show_logs
        exit 1
    fi

    echo "==> 部署完成。"
}

trap 'echo "部署失败。"; show_logs; exit 1' ERR

main "$@"
