#!/bin/bash

# =================================================================
# AnyWay AI Agent Platform - 一键启动脚本
# =================================================================
# 用途: 快速启动所有服务
# 使用方法: ./start.sh
# =================================================================

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示欢迎信息
show_banner() {
    echo -e "${GREEN}"
    echo "================================================================="
    echo "    AnyWay AI Agent Platform - 一键启动"
    echo "================================================================="
    echo -e "${NC}"
}

# 检查Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
}

# 检查配置文件
check_config() {
    if [ ! -f .env ]; then
        log_warning ".env 文件不存在"
        if [ -f env.example ]; then
            log_info "从 env.example 创建 .env 文件"
            cp env.example .env
            log_warning "请编辑 .env 文件配置必要的参数"
        else
            log_error "env.example 文件也不存在，无法创建配置"
            exit 1
        fi
    fi
}

# 检查端口占用
check_ports() {
    log_info "检查端口占用..."
    
    if sudo lsof -Pi :18080 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        log_warning "端口 18080 已被占用"
        echo -n "是否停止占用该端口的进程? (y/n): "
        read -r stop_process
        if [ "$stop_process" = "y" ]; then
            sudo lsof -ti:18080 | xargs sudo kill -9 || true
            log_success "已停止端口 18080 上的进程"
        fi
    fi
}

# 构建前端镜像
build_frontend() {
    log_info "构建前端镜像（确保代码更新生效）..."
    
    cd "$(dirname "$0")"
    
    # 重新构建前端镜像以确保代码更新生效
    if docker compose -f docker-compose.prod.yml build frontend; then
        log_success "前端镜像构建成功"
    else
        log_warning "前端镜像构建失败，将尝试使用现有镜像"
        return 1
    fi
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    cd "$(dirname "$0")"
    
    # 启动所有服务
    if docker compose -f docker-compose.prod.yml up -d; then
        log_success "服务启动成功"
    else
        log_error "服务启动失败"
        exit 1
    fi
}

# 等待服务就绪
wait_for_services() {
    log_info "等待服务启动..."
    
    # 等待MySQL
    log_info "等待MySQL启动..."
    for i in {1..30}; do
        if docker exec aiagent-mysql mysqladmin ping -h localhost --silent 2>/dev/null; then
            log_success "MySQL已就绪"
            break
        fi
        if [ $i -eq 30 ]; then
            log_error "MySQL启动超时"
            exit 1
        fi
        sleep 2
    done
    
    # 等待Redis
    log_info "等待Redis启动..."
    for i in {1..30}; do
        if docker exec aiagent-redis redis-cli ping | grep -q PONG; then
            log_success "Redis已就绪"
            break
        fi
        if [ $i -eq 30 ]; then
            log_error "Redis启动超时"
            exit 1
        fi
        sleep 2
    done
    
    # 等待后端
    log_info "等待后端服务启动..."
    sleep 10
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    echo ""
    docker compose -f docker-compose.prod.yml ps
    echo ""
    
    # 检查各个服务
    SERVICES=("aiagent-mysql" "aiagent-redis" "aiagent-backend" "aiagent-celery-worker" "aiagent-frontend")
    ALL_RUNNING=true
    
    for service in "${SERVICES[@]}"; do
        if docker ps --format '{{.Names}}' | grep -q "^$service$"; then
            log_success "$service 运行正常"
        else
            log_error "$service 未运行"
            ALL_RUNNING=false
        fi
    done
    
    if [ "$ALL_RUNNING" = false ]; then
        log_warning "部分服务未正常启动，请检查日志"
        return 1
    fi
    
    return 0
}

# 显示访问信息
show_access_info() {
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")
    
    echo ""
    echo -e "${GREEN}"
    echo "================================================================="
    echo "               服务启动成功！"
    echo "================================================================="
    echo -e "${NC}"
    echo ""
    echo -e "${BLUE}访问地址:${NC}"
    echo -e "  前端页面:    http://$SERVER_IP:18080"
    echo -e "  API文档:     http://$SERVER_IP:18080/swagger/"
    echo -e "  管理后台:    http://$SERVER_IP:18080/admin/"
    echo ""
    echo -e "${BLUE}常用命令:${NC}"
    echo -e "  查看日志:    docker compose -f docker-compose.prod.yml logs -f"
    echo -e "  查看状态:    docker compose -f docker-compose.prod.yml ps"
    echo -e "  停止服务:    docker compose -f docker-compose.prod.yml stop"
    echo -e "  重启服务:    docker compose -f docker-compose.prod.yml restart"
    echo ""
    echo -e "${YELLOW}注意事项:${NC}"
    echo -e "  1. 首次访问可能需要等待1-2分钟"
    echo -e "  2. 请确保防火墙已开放18080端口"
    echo -e "  3. 配置文件位于: .env"
    echo ""
    echo -e "${GREEN}祝使用愉快！${NC}"
    echo ""
}

# 主函数
main() {
    show_banner
    check_docker
    check_config
    check_ports
    build_frontend
    start_services
    wait_for_services
    
    if check_services; then
        show_access_info
    else
        log_error "启动过程中出现错误，请检查日志"
        echo "查看日志命令: docker compose -f docker-compose.prod.yml logs"
        exit 1
    fi
}

# 执行主函数
main

