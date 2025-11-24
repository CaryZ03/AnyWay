#!/bin/bash

# AI智能体创作平台 - 部署脚本
set -e

echo "🚀 开始部署AI智能体创作平台..."

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查环境变量文件
if [ ! -f .env.prod ]; then
    echo -e "${YELLOW}⚠️  未找到 .env.prod 文件${NC}"
    echo "请复制 .env.prod.example 为 .env.prod 并填写配置"
    exit 1
fi

# 1. 拉取最新代码
echo -e "${GREEN}📥 拉取最新代码...${NC}"
git pull origin main || echo "跳过git pull（可能不在git仓库中）"

# 2. 构建Docker镜像
echo -e "${GREEN}🔨 构建Docker镜像...${NC}"
docker-compose -f docker-compose.prod.yml build

# 3. 停止旧容器
echo -e "${GREEN}🛑 停止旧容器...${NC}"
docker-compose -f docker-compose.prod.yml down

# 4. 启动新容器
echo -e "${GREEN}▶️  启动新容器...${NC}"
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# 5. 等待服务就绪
echo -e "${GREEN}⏳ 等待服务就绪...${NC}"
sleep 15

# 6. 检查服务状态
echo -e "${GREEN}✅ 检查服务状态...${NC}"
docker-compose -f docker-compose.prod.yml ps

# 7. 显示日志
echo -e "${GREEN}📋 最近的日志:${NC}"
docker-compose -f docker-compose.prod.yml logs --tail=50

echo ""
echo -e "${GREEN}🎉 部署完成！${NC}"
echo ""
echo "服务地址:"
echo "  - 前端: http://localhost"
echo "  - 后端API: http://localhost:8000"
echo "  - API文档: http://localhost:8000/swagger/"
echo ""
echo "查看日志: docker-compose -f docker-compose.prod.yml logs -f"
echo "停止服务: docker-compose -f docker-compose.prod.yml down"
