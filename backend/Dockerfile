# 多阶段构建 - Django后端
FROM python:3.11-slim as builder

# 设置工作目录
WORKDIR /app

# 注意：使用 PyMySQL 替代 mysqlclient，无需编译依赖
# PyMySQL 是纯 Python 实现，不需要 gcc、MySQL 客户端库等

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖（使用清华镜像源加速）
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 运行阶段
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 注意：使用 PyMySQL 无需 MySQL 客户端库
# 如果需要其他系统依赖，可以在这里添加

# 从构建阶段复制Python包
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p logs media staticfiles

# 注意：collectstatic 需要在运行时执行，因为需要数据库连接和配置
# 这里只创建目录，实际收集在 docker-compose 的 command 中执行

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "aiagent.wsgi:application"]
