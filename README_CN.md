# AnyWay AI Agent Platform - 使用说明

## 📋 项目简介

AnyWay 是一个现代化的 AI 智能体管理平台，支持智能体的创建、配置、测试和部署。平台集成了火山引擎（豆包）AI 服务，提供完整的对话功能。

## 🚀 快速开始

### 一键启动服务

```bash
cd /root/pku_hlw/AnyWay
./start.sh
```

### 手动启动

```bash
cd /root/pku_hlw/AnyWay
docker compose -f docker-compose.prod.yml up -d
```

## 🌐 访问地址

- **前端页面**: http://106.12.174.161:18080
- **API文档**: http://106.12.174.161:18080/swagger/
- **管理后台**: http://106.12.174.161:18080/admin/

## 📖 主要功能

### 1. 创建智能体

1. 访问前端页面
2. 点击右上角 **"+ 项目"** 按钮
3. 填写智能体信息：
   - **名称**（必填）：智能体名称
   - **功能介绍**（选填）：会展示给用户
   - **系统提示词**（必填）：定义智能体的角色和能力
   - **模型选择**：doubao-seed-1-6-251015（默认）
   - **温度系数**：0-2，控制回复的创造性
   - **图标**：选择智能体头像
4. 点击 **"确认"** 创建

### 2. 发布智能体

1. 点击智能体卡片进入对话页面
2. 如果状态为草稿，右上角会显示 **"📢 发布智能体"** 按钮
3. 点击发布按钮，确认发布
4. 发布成功后显示 **"✓ 已发布"** 绿色徽章

### 3. 与智能体对话

1. 点击已发布的智能体卡片
2. 在底部输入框输入消息
3. 按 **Enter** 发送，**Shift + Enter** 换行
4. AI 会实时回复你的消息

## ⚙️ 配置说明

### 环境变量

配置文件位置：`/root/pku_hlw/AnyWay/.env`

**重要配置项**：

```bash
# 火山引擎（豆包）API Key
ARK_API_KEY=17ef8338-0d89-4ba2-aa16-c6e526022af3

# 火山引擎 API Base URL
ARK_API_BASE=https://ark.cn-beijing.volces.com/api/v3

# Django 密钥
SECRET_KEY=your-secret-key

# 数据库密码
MYSQL_ROOT_PASSWORD=your-root-password
MYSQL_PASSWORD=your-app-password

# 允许访问的主机
ALLOWED_HOSTS=localhost,127.0.0.1,106.12.174.161

# CORS 配置
CORS_ALLOWED_ORIGINS=http://localhost:18080,http://106.12.174.161:18080
```

## 🛠️ 常用命令

### 服务管理

```bash
# 启动所有服务
docker compose -f docker-compose.prod.yml up -d

# 停止所有服务
docker compose -f docker-compose.prod.yml stop

# 重启服务
docker compose -f docker-compose.prod.yml restart

# 查看服务状态
docker compose -f docker-compose.prod.yml ps

# 查看日志
docker compose -f docker-compose.prod.yml logs -f

# 查看后端日志
docker logs -f aiagent-backend

# 查看前端日志
docker logs -f aiagent-frontend
```

### 数据库操作

```bash
# 进入MySQL
docker exec -it aiagent-mysql mysql -u root -p

# 备份数据库
docker exec aiagent-mysql mysqldump -u root -p aiagent > backup.sql

# 创建管理员账号
docker exec -it aiagent-backend python manage.py createsuperuser
```

### 更新代码

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker compose -f docker-compose.prod.yml up -d --build

# 执行数据库迁移
docker exec aiagent-backend python manage.py migrate
```

## 🔧 故障排查

### 问题1：无法访问网页

**检查清单**：
1. 服务是否运行：`docker compose -f docker-compose.prod.yml ps`
2. 防火墙是否开放：`sudo ufw status | grep 18080`
3. 云服务器安全组是否配置（开放18080端口）

### 问题2：AI不回复

**检查清单**：
1. 智能体是否已发布（右上角显示"✓ 已发布"）
2. API Key是否配置：`cat .env | grep ARK_API_KEY`
3. 查看后端日志：`docker logs aiagent-backend --tail 50`

### 问题3：发布按钮不显示

**原因**：智能体已经是发布状态  
**解决**：右上角应该显示"✓ 已发布"绿色徽章

### 问题4：服务启动失败

```bash
# 查看详细日志
docker compose -f docker-compose.prod.yml logs

# 检查端口占用
sudo lsof -i :18080
sudo lsof -i :3306
sudo lsof -i :6379

# 重启服务
docker compose -f docker-compose.prod.yml restart
```

## 📁 项目结构

```
AnyWay/
├── backend/              # Django 后端
│   ├── apps/            # 应用模块
│   │   ├── agent/       # 智能体模块
│   │   ├── llm/         # LLM服务集成
│   │   └── ...
│   └── aiagent/         # 项目配置
├── frontend/            # Vue 3 前端
│   └── src/
│       ├── components/  # 组件
│       ├── api/         # API接口
│       └── ...
├── docker-compose.prod.yml  # 生产环境配置
├── start.sh             # 一键启动脚本
├── deploy.sh            # 一键部署脚本
└── README_CN.md        # 本文档
```

## 🔐 安全建议

1. **修改默认密码**：确保数据库密码足够强
2. **配置防火墙**：只开放必要端口
3. **定期备份**：备份数据库和配置文件
4. **更新依赖**：定期更新Docker镜像和系统包

## 📚 相关文档

- **README.md** - 项目主文档（英文）
- **DEPLOYMENT.md** - 详细部署文档
- **QUICKSTART.md** - 快速开始指南

## 🆘 获取帮助

如遇问题，请：
1. 查看日志：`docker compose -f docker-compose.prod.yml logs`
2. 检查服务状态：`docker compose -f docker-compose.prod.yml ps`
3. 查看本文档的故障排查部分

---

**最后更新**: 2025-11-26  
**版本**: v1.0

