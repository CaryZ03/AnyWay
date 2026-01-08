# 🚀 AnyWay 快速部署指南

## Ubuntu云服务器一键部署

### 📋 前置条件

- ✅ Ubuntu 20.04+ 服务器
- ✅ 至少 4GB 内存
- ✅ 至少 20GB 磁盘空间
- ✅ root 或 sudo 权限

### ⚡ 一键部署（推荐）

```bash
# 1. 进入项目目录
cd /root/pku_hlw/AnyWay

# 2. 执行一键部署脚本
./deploy.sh
```

**就这么简单！** 脚本会自动完成所有配置和部署工作。

### 📝 部署过程

脚本会自动执行以下操作：

1. ✅ 检查系统环境
2. ✅ 安装 Docker（如未安装）
3. ✅ 配置环境变量（自动生成密钥）
4. ✅ 构建并启动所有服务
5. ✅ 初始化数据库
6. ✅ 创建管理员账号

**预计耗时**: 10-20分钟（首次部署）

### 🎯 部署完成后

#### 访问地址

假设你的服务器IP是 `123.45.67.89`：

- **前端页面**: http://123.45.67.89:18080
- **API文档**: http://123.45.67.89:18080/swagger/
- **管理后台**: http://123.45.67.89:18080/admin/

#### 重要信息

部署完成后，请记录以下信息（脚本会显示）：

- MySQL Root 密码
- MySQL 应用密码
- 管理员账号和密码

### ⚙️ 配置 OpenAI API Key

为了使用 AI 功能，你需要配置 OpenAI API Key：

```bash
# 编辑配置文件
nano .env

# 找到这一行并修改：
OPENAI_API_KEY=sk-your-actual-api-key-here

# 保存后重启服务
docker compose -f docker-compose.prod.yml restart backend celery-worker
```

### 🔥 防火墙配置

确保开放必要端口：

```bash
# Ubuntu (UFW)
sudo ufw allow 18080/tcp
sudo ufw allow 22/tcp
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-port=18080/tcp
sudo firewall-cmd --reload
```

**云服务器安全组**：
- 在云服务商控制台添加安全组规则
- 开放入站端口：18080 (HTTP)
- 开放入站端口：22 (SSH)

## 🛠️ 常用命令

### 服务管理

```bash
# 查看服务状态
docker compose -f docker-compose.prod.yml ps

# 查看日志
docker compose -f docker-compose.prod.yml logs -f

# 重启服务
docker compose -f docker-compose.prod.yml restart

# 停止服务
docker compose -f docker-compose.prod.yml stop

# 启动服务
docker compose -f docker-compose.prod.yml start
```

### 数据库管理

```bash
# 进入MySQL
docker exec -it aiagent-mysql mysql -u root -p

# 备份数据库
docker exec aiagent-mysql mysqldump -u root -p aiagent > backup.sql

# 恢复数据库
docker exec -i aiagent-mysql mysql -u root -p aiagent < backup.sql
```

### 查看日志

```bash
# 查看后端日志
docker compose -f docker-compose.prod.yml logs -f backend

# 查看前端日志
docker compose -f docker-compose.prod.yml logs -f frontend

# 查看所有日志
docker compose -f docker-compose.prod.yml logs -f
```

## 🆘 故障排查

### 问题1：无法访问网页

**检查清单**：

1. ✅ 服务是否运行：`docker compose -f docker-compose.prod.yml ps`
2. ✅ 防火墙是否开放：`sudo ufw status`
3. ✅ 云服务器安全组是否配置
4. ✅ 端口是否被占用：`sudo lsof -i :18080`

### 问题2：后端连接数据库失败

```bash
# 检查MySQL容器状态
docker logs aiagent-mysql

# 检查数据库连接
docker exec aiagent-mysql mysqladmin ping -h localhost -u root -p

# 重启MySQL
docker compose -f docker-compose.prod.yml restart mysql
```

### 问题3：前端无法加载数据

```bash
# 检查后端服务
docker logs aiagent-backend

# 检查CORS配置
cat .env | grep CORS

# 重启后端服务
docker compose -f docker-compose.prod.yml restart backend
```

### 获取帮助

如果遇到问题，请：

1. 查看详细文档：`cat DEPLOYMENT.md`
2. 查看服务日志：`docker compose -f docker-compose.prod.yml logs`
3. 提交 Issue：[GitHub Issues](https://github.com/your-repo/AnyWay/issues)

## 🔄 更新部署

当代码更新后，执行以下命令：

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 重新构建并启动
docker compose -f docker-compose.prod.yml up -d --build

# 3. 执行数据库迁移（如有）
docker exec aiagent-backend python manage.py migrate
```

## 🔐 安全建议

### 生产环境必做项

1. ✅ **修改默认密码**
   - MySQL root 密码
   - MySQL 应用密码
   - Django SECRET_KEY

2. ✅ **配置防火墙**
   - 只开放必要端口
   - 限制访问 IP（如果可能）

3. ✅ **启用 HTTPS**（推荐）
   ```bash
   # 安装 Certbot
   sudo apt-get install certbot python3-certbot-nginx
   
   # 配置域名并获取证书
   sudo certbot --nginx -d your-domain.com
   ```

4. ✅ **定期备份**
   - 数据库备份
   - 配置文件备份
   - 媒体文件备份

5. ✅ **定期更新**
   ```bash
   # 更新系统
   sudo apt-get update && sudo apt-get upgrade -y
   
   # 更新Docker镜像
   docker compose -f docker-compose.prod.yml pull
   docker compose -f docker-compose.prod.yml up -d
   ```

## 📊 性能优化建议

### 服务器配置建议

| 用户规模 | CPU | 内存 | 磁盘 |
|---------|-----|------|------|
| 小型（<100用户） | 2核 | 4GB | 20GB |
| 中型（100-1000用户） | 4核 | 8GB | 50GB |
| 大型（>1000用户） | 8核+ | 16GB+ | 100GB+ |

### 性能调优

1. **增加 Gunicorn workers**（根据CPU核心数）
2. **配置 Redis 缓存**
3. **启用 Nginx Gzip 压缩**
4. **配置 CDN**（用于静态资源）

详细优化方案请参考：[DEPLOYMENT.md](./DEPLOYMENT.md)

## 📚 更多文档

- **详细部署文档**: [DEPLOYMENT.md](./DEPLOYMENT.md)
- **项目说明**: [README.md](./README.md)
- **API文档**: 访问 http://your-server-ip:18080/swagger/

---

## 💡 小贴士

### 快速测试

部署完成后，可以快速测试：

```bash
# 测试前端
curl http://localhost:18080

# 测试后端API
curl http://localhost:18080/api/v1/

# 测试数据库
docker exec aiagent-mysql mysqladmin ping -h localhost --silent && echo "OK"

# 测试Redis
docker exec aiagent-redis redis-cli ping
```

### 常见端口说明

- **18080**: 前端访问端口（对外开放）
- **3306**: MySQL 端口（仅内网，不对外开放）
- **6379**: Redis 端口（仅内网，不对外开放）
- **8000**: 后端服务端口（仅内网，通过Nginx代理）

### 系统要求检查

```bash
# 检查内存
free -h

# 检查磁盘空间
df -h

# 检查CPU
nproc

# 检查Ubuntu版本
lsb_release -a
```

---

**祝你部署顺利！🎉**

如有问题，请查看 [DEPLOYMENT.md](./DEPLOYMENT.md) 获取更详细的说明。

