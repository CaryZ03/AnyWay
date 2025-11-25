#!/bin/bash
# AnyWay 生产环境部署脚本

set -e

echo "=== AnyWay 生产环境部署 ==="

# 检查环境变量文件（优先使用 .env.prod，其次 .env）
ENV_FILE=".env"
if [ -f ".env.prod" ]; then
    ENV_FILE=".env.prod"
    echo "使用 .env.prod 文件"
elif [ -f ".env" ]; then
    echo "使用 .env 文件"
else
    echo "警告: .env 或 .env.prod 文件不存在，将使用默认配置"
    echo "建议: 创建 .env.prod 文件并配置 SECRET_KEY 等环境变量"
    read -p "是否继续？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 构建并启动服务（使用指定的环境变量文件）
echo "正在构建并启动服务..."
if [ "$ENV_FILE" = ".env.prod" ]; then
    docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
else
    docker-compose -f docker-compose.prod.yml up -d --build
fi

# 等待服务启动
echo "等待服务启动..."
sleep 10

# 检查服务状态
echo "检查服务状态..."
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "=== 部署完成 ==="
echo "前端访问: http://localhost:18080"
echo "后端 API: http://localhost:18080/api/v1/ (通过 Nginx 代理)"
echo "管理后台: http://localhost:18080/admin/ (通过 Nginx 代理)"
echo "API 文档: http://localhost:18080/swagger/ (通过 Nginx 代理)"
echo ""
echo "注意: 后端服务不直接暴露端口，所有请求通过前端 Nginx 代理"
echo "注意: 如果 80 端口被占用，已自动使用 18080 端口"
echo ""
echo "查看日志: docker-compose -f docker-compose.prod.yml logs -f"
echo "停止服务: docker-compose -f docker-compose.prod.yml down"

