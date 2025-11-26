#!/bin/bash

# =================================================================
# AnyWay AI Agent Platform - 一键部署脚本
# =================================================================
# 用途: 在Ubuntu云服务器上一键部署前后端服务
# 使用方法: 
#   chmod +x deploy.sh
#   ./deploy.sh
# =================================================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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
    echo "    AnyWay AI Agent Platform - 一键部署脚本"
    echo "================================================================="
    echo -e "${NC}"
}

# 检查是否为root用户
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        log_warning "建议使用 sudo 运行此脚本以避免权限问题"
        echo -n "是否继续? (y/n): "
        read -r continue
        if [ "$continue" != "y" ]; then
            log_info "部署已取消"
            exit 0
        fi
    fi
}

# 检查系统类型
check_system() {
    log_info "检查操作系统..."
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
        log_success "检测到系统: $OS $VER"
    else
        log_error "无法检测操作系统类型"
        exit 1
    fi
    
    if [ "$OS" != "ubuntu" ]; then
        log_warning "此脚本针对Ubuntu系统优化，其他系统可能需要调整"
    fi
}

# 检查并安装Docker
install_docker() {
    log_info "检查Docker安装状态..."
    
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version)
        log_success "Docker已安装: $DOCKER_VERSION"
    else
        log_warning "Docker未安装，开始安装..."
        log_info "使用清华大学镜像源加速安装..."
        
        # 更新包索引
        sudo apt-get update
        
        # 安装依赖
        sudo apt-get install -y \
            ca-certificates \
            curl \
            gnupg \
            lsb-release
        
        # 添加Docker GPG密钥（使用清华镜像）
        sudo mkdir -p /etc/apt/keyrings
        curl -fsSL https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        
        # 设置Docker仓库（使用清华镜像）
        echo \
          "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/ubuntu \
          $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # 安装Docker Engine
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        
        # 配置Docker镜像加速器（针对中国大陆网络优化）
        log_info "配置Docker Hub镜像加速器..."
        sudo mkdir -p /etc/docker
        sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "registry-mirrors": [
    "https://dockerproxy.com",
    "https://docker.registry.cyou",
    "https://docker-cf.registry.cyou",
    "https://dockercf.jsdelivr.fyi"
  ],
  "dns": ["8.8.8.8", "8.8.4.4", "114.114.114.114"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "max-concurrent-downloads": 10
}
EOF
        
        # 启动Docker服务
        sudo systemctl daemon-reload
        sudo systemctl start docker
        sudo systemctl enable docker
        
        # 将当前用户添加到docker组
        sudo usermod -aG docker $USER
        
        log_success "Docker安装完成"
        log_success "已配置国内镜像加速器"
        log_warning "请注销并重新登录以使Docker组权限生效，然后重新运行此脚本"
        exit 0
    fi
}

# 配置Docker镜像加速（如果已安装Docker但未配置）
configure_docker_mirror() {
    log_info "检查Docker镜像加速配置..."
    
    if [ ! -f /etc/docker/daemon.json ]; then
        log_warning "未检测到Docker镜像加速配置，正在配置..."
        sudo mkdir -p /etc/docker
        sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "registry-mirrors": [
    "https://dockerproxy.com",
    "https://docker.registry.cyou",
    "https://docker-cf.registry.cyou",
    "https://dockercf.jsdelivr.fyi"
  ],
  "dns": ["8.8.8.8", "8.8.4.4", "114.114.114.114"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "max-concurrent-downloads": 10
}
EOF
        sudo systemctl daemon-reload
        sudo systemctl restart docker
        log_success "Docker镜像加速已配置"
        sleep 3
    else
        log_success "Docker镜像加速已配置"
    fi
}

# 检查Docker Compose
check_docker_compose() {
    log_info "检查Docker Compose..."
    
    if docker compose version &> /dev/null; then
        COMPOSE_VERSION=$(docker compose version)
        log_success "Docker Compose已安装: $COMPOSE_VERSION"
    else
        log_error "Docker Compose未安装或版本过旧"
        log_info "请升级Docker到最新版本"
        exit 1
    fi
}

# 预拉取基础镜像
pull_base_images() {
    log_info "预拉取基础镜像（使用国内镜像源）..."
    log_warning "这可能需要5-15分钟，取决于网络速度..."
    
    # 定义需要的基础镜像
    IMAGES=(
        "python:3.11-slim"
        "node:20-alpine"
        "nginx:alpine"
        "mysql:8.0"
        "redis:alpine"
    )
    
    for image in "${IMAGES[@]}"; do
        log_info "拉取镜像: $image"
        if docker pull $image; then
            log_success "✓ $image 拉取成功"
        else
            log_error "✗ $image 拉取失败"
            log_warning "将在构建时重试..."
        fi
    done
    
    log_success "基础镜像拉取完成"
}

# 检查端口占用
check_ports() {
    log_info "检查端口占用情况..."
    
    PORTS=(18080 3306 6379)
    PORT_NAMES=("前端服务" "MySQL" "Redis")
    
    for i in "${!PORTS[@]}"; do
        PORT=${PORTS[$i]}
        NAME=${PORT_NAMES[$i]}
        
        if sudo lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
            log_warning "端口 $PORT ($NAME) 已被占用"
            echo -n "是否停止占用该端口的进程? (y/n): "
            read -r stop_process
            if [ "$stop_process" = "y" ]; then
                sudo lsof -ti:$PORT | xargs sudo kill -9 || true
                log_success "已停止端口 $PORT 上的进程"
            fi
        else
            log_success "端口 $PORT ($NAME) 可用"
        fi
    done
}

# 配置环境变量
setup_env() {
    log_info "配置环境变量..."
    
    if [ -f .env ]; then
        log_warning "检测到现有的 .env 文件"
        echo -n "是否重新配置? (y/n): "
        read -r reconfig
        if [ "$reconfig" != "y" ]; then
            log_info "使用现有配置"
            return
        fi
        mv .env .env.backup.$(date +%Y%m%d%H%M%S)
        log_info "已备份现有配置"
    fi
    
    if [ ! -f env.example ]; then
        log_error "env.example 文件不存在"
        exit 1
    fi
    
    cp env.example .env
    log_success "已创建 .env 文件"
    
    # 生成随机密钥
    log_info "生成安全密钥..."
    SECRET_KEY=$(openssl rand -base64 50 | tr -d '\n/')
    MYSQL_ROOT_PASS=$(openssl rand -base64 24 | tr -d '\n/')
    MYSQL_APP_PASS=$(openssl rand -base64 24 | tr -d '\n/')
    
    # 更新.env文件
    sed -i "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env
    sed -i "s|MYSQL_ROOT_PASSWORD=.*|MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASS|" .env
    sed -i "s|MYSQL_PASSWORD=.*|MYSQL_PASSWORD=$MYSQL_APP_PASS|" .env
    
    # 获取服务器IP
    SERVER_IP=$(curl -s ifconfig.me || echo "localhost")
    log_info "检测到服务器IP: $SERVER_IP"
    
    # 配置ALLOWED_HOSTS
    sed -i "s|ALLOWED_HOSTS=.*|ALLOWED_HOSTS=localhost,127.0.0.1,$SERVER_IP|" .env
    sed -i "s|CORS_ALLOWED_ORIGINS=.*|CORS_ALLOWED_ORIGINS=http://localhost:18080,http://$SERVER_IP:18080|" .env
    
    log_success "环境变量配置完成"
    log_warning "请编辑 .env 文件配置 OPENAI_API_KEY 等其他参数"
    
    echo ""
    echo -e "${YELLOW}=== 重要配置信息 ===${NC}"
    echo -e "MySQL Root 密码: ${GREEN}$MYSQL_ROOT_PASS${NC}"
    echo -e "MySQL 应用密码: ${GREEN}$MYSQL_APP_PASS${NC}"
    echo -e "Django Secret Key: ${GREEN}[已生成]${NC}"
    echo ""
    log_warning "请妥善保存以上信息！"
    echo ""
    
    echo -n "按回车键继续..."
    read
}

# 检查OpenAI API Key
check_openai_key() {
    log_info "检查OpenAI API配置..."
    
    if grep -q "OPENAI_API_KEY=sk-" .env; then
        log_success "检测到OpenAI API Key配置"
    else
        log_warning "未配置OpenAI API Key，AI功能将无法使用"
        echo -n "是否现在配置? (y/n): "
        read -r config_key
        if [ "$config_key" = "y" ]; then
            echo -n "请输入OpenAI API Key: "
            read -r api_key
            sed -i "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=$api_key|" .env
            log_success "API Key已配置"
        fi
    fi
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p backend/logs
    mkdir -p backend/media
    mkdir -p backend/staticfiles
    
    log_success "目录创建完成"
}

# 停止并清理旧容器
cleanup_old_containers() {
    log_info "清理旧的容器..."
    
    if docker ps -a | grep -q "aiagent-"; then
        log_warning "检测到运行中的容器"
        echo -n "是否停止并删除旧容器? (y/n): "
        read -r cleanup
        if [ "$cleanup" = "y" ]; then
            docker compose -f docker-compose.prod.yml down -v || true
            log_success "已清理旧容器"
        fi
    fi
}

# 构建并启动服务
build_and_start() {
    log_info "开始构建Docker镜像..."
    log_warning "首次构建可能需要10-20分钟，请耐心等待..."
    
    # 构建镜像（不使用缓存，确保使用最新镜像源）
    log_info "正在构建镜像，请稍候..."
    if timeout 1800 docker compose -f docker-compose.prod.yml build 2>&1 | tee build.log; then
        log_success "镜像构建完成"
    else
        log_error "镜像构建失败"
        log_error "详细日志已保存到 build.log"
        log_info "常见问题："
        log_info "1. 网络超时：请检查网络连接，或稍后重试"
        log_info "2. 磁盘空间不足：运行 df -h 检查磁盘空间"
        log_info "3. 内存不足：确保至少有 4GB 可用内存"
        
        echo -n "是否重试构建? (y/n): "
        read -r retry
        if [ "$retry" = "y" ]; then
            log_info "重新构建..."
            if docker compose -f docker-compose.prod.yml build; then
                log_success "镜像构建完成"
            else
                log_error "构建再次失败，请检查日志"
                exit 1
            fi
        else
            exit 1
        fi
    fi
    
    log_info "启动服务..."
    
    # 启动服务
    if docker compose -f docker-compose.prod.yml up -d; then
        log_success "服务启动完成"
    else
        log_error "服务启动失败"
        log_info "查看错误日志: docker compose -f docker-compose.prod.yml logs"
        exit 1
    fi
}

# 等待服务就绪
wait_for_services() {
    log_info "等待服务启动..."
    
    # 等待MySQL就绪
    log_info "等待MySQL数据库启动..."
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
    
    # 等待Redis就绪
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
    
    # 等待后端服务
    log_info "等待后端服务启动..."
    sleep 10
}

# 初始化数据库
init_database() {
    log_info "初始化数据库..."
    
    # 运行数据库迁移
    log_info "执行数据库迁移..."
    if docker exec aiagent-backend python manage.py migrate; then
        log_success "数据库迁移完成"
    else
        log_error "数据库迁移失败"
        docker logs aiagent-backend
        exit 1
    fi
    
    # 创建超级用户
    log_info "创建管理员账号..."
    echo -e "${YELLOW}请按提示输入管理员信息:${NC}"
    docker exec -it aiagent-backend python manage.py createsuperuser || true
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

# 显示部署信息
show_deployment_info() {
    SERVER_IP=$(curl -s ifconfig.me || echo "localhost")
    
    echo ""
    echo -e "${GREEN}"
    echo "================================================================="
    echo "               部署成功！"
    echo "================================================================="
    echo -e "${NC}"
    echo ""
    echo -e "${BLUE}访问地址:${NC}"
    echo -e "  前端页面:    http://$SERVER_IP:18080"
    echo -e "  后端API:     http://$SERVER_IP:18080/api/v1/"
    echo -e "  API文档:     http://$SERVER_IP:18080/swagger/"
    echo -e "  管理后台:    http://$SERVER_IP:18080/admin/"
    echo ""
    echo -e "${BLUE}常用命令:${NC}"
    echo -e "  查看日志:    docker compose -f docker-compose.prod.yml logs -f"
    echo -e "  查看状态:    docker compose -f docker-compose.prod.yml ps"
    echo -e "  停止服务:    docker compose -f docker-compose.prod.yml stop"
    echo -e "  启动服务:    docker compose -f docker-compose.prod.yml start"
    echo -e "  重启服务:    docker compose -f docker-compose.prod.yml restart"
    echo -e "  删除服务:    docker compose -f docker-compose.prod.yml down"
    echo ""
    echo -e "${YELLOW}注意事项:${NC}"
    echo -e "  1. 首次访问可能需要等待1-2分钟"
    echo -e "  2. 请确保防火墙已开放18080端口"
    echo -e "  3. 配置文件位于: .env"
    echo -e "  4. 数据库密码已保存在 .env 文件中"
    echo ""
    echo -e "${GREEN}祝使用愉快！${NC}"
    echo ""
}

# 配置防火墙
configure_firewall() {
    log_info "检查防火墙配置..."
    
    if command -v ufw &> /dev/null; then
        log_info "检测到UFW防火墙"
        echo -n "是否配置防火墙规则? (y/n): "
        read -r config_fw
        if [ "$config_fw" = "y" ]; then
            sudo ufw allow 18080/tcp comment 'AnyWay Frontend'
            sudo ufw allow 22/tcp comment 'SSH'
            log_success "防火墙规则已添加"
            log_warning "请确保UFW已启用: sudo ufw enable"
        fi
    elif command -v firewall-cmd &> /dev/null; then
        log_info "检测到firewalld防火墙"
        echo -n "是否配置防火墙规则? (y/n): "
        read -r config_fw
        if [ "$config_fw" = "y" ]; then
            sudo firewall-cmd --permanent --add-port=18080/tcp
            sudo firewall-cmd --reload
            log_success "防火墙规则已添加"
        fi
    else
        log_warning "未检测到防火墙，请手动开放18080端口"
    fi
}

# 主函数
main() {
    show_banner
    check_root
    check_system
    install_docker
    configure_docker_mirror  # 配置镜像加速
    check_docker_compose
    check_ports
    setup_env
    check_openai_key
    create_directories
    cleanup_old_containers
    pull_base_images  # 预拉取基础镜像
    build_and_start
    wait_for_services
    init_database
    
    if check_services; then
        configure_firewall
        show_deployment_info
    else
        log_error "部署过程中出现错误，请检查日志"
        echo "查看日志命令: docker compose -f docker-compose.prod.yml logs"
        exit 1
    fi
}

# 执行主函数
main

