#!/bin/bash

# =================================================================
# 快速更新脚本 - 只更新代码，不重新安装依赖
# =================================================================
# 使用方法: ./quick-update.sh
# =================================================================

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

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

# 检查前端是否已构建
check_frontend_build() {
    if [ ! -d "frontend/dist" ]; then
        log_warning "前端 dist 目录不存在，需要先构建前端"
        echo -n "是否现在构建前端? (y/n): "
        read -r build_frontend
        if [ "$build_frontend" = "y" ]; then
            build_frontend_only
        else
            log_error "前端未构建，无法继续"
            exit 1
        fi
    fi
}

# 只构建前端（不安装依赖，假设 node_modules 已存在）
build_frontend_only() {
    log_info "构建前端（使用现有 node_modules）..."
    
    cd frontend
    
    # 检查 node_modules 是否存在
    if [ ! -d "node_modules" ]; then
        log_warning "node_modules 不存在，需要先安装依赖"
        echo -n "是否现在安装依赖? (y/n): "
        read -r install_deps
        if [ "$install_deps" = "y" ]; then
            npm install
        else
            log_error "无法继续，请先安装依赖: cd frontend && npm install"
            exit 1
        fi
    fi
    
    # 构建前端
    log_info "执行 npm run build..."
    npm run build
    
    if [ $? -eq 0 ]; then
        log_success "前端构建成功"
    else
        log_error "前端构建失败"
        exit 1
    fi
    
    cd ..
}

# 更新后端（只需重启）
update_backend() {
    log_info "更新后端服务..."
    
    # 重启后端和 Celery
    docker compose -f docker-compose.quick-update.yml restart backend celery-worker
    
    log_success "后端服务已重启"
}

# 更新前端（重新挂载）
update_frontend() {
    log_info "更新前端服务..."
    
    # 重新构建前端（只构建，不安装依赖）
    build_frontend_only
    
    # 重启前端容器（重新挂载 dist 目录）
    docker compose -f docker-compose.quick-update.yml restart frontend
    
    log_success "前端服务已更新"
}

# 主函数
main() {
    log_info "开始快速更新..."
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装"
        exit 1
    fi
    
    # 检查前端构建
    check_frontend_build
    
    # 选择更新内容
    echo ""
    echo "请选择更新内容:"
    echo "1) 只更新后端"
    echo "2) 只更新前端"
    echo "3) 更新前后端"
    echo -n "请输入选项 (1-3): "
    read -r choice
    
    case $choice in
        1)
            update_backend
            ;;
        2)
            update_frontend
            ;;
        3)
            update_backend
            update_frontend
            ;;
        *)
            log_error "无效选项"
            exit 1
            ;;
    esac
    
    echo ""
    log_success "更新完成！"
    log_info "查看服务状态: docker compose -f docker-compose.quick-update.yml ps"
    log_info "查看日志: docker compose -f docker-compose.quick-update.yml logs -f"
}

# 执行主函数
main

