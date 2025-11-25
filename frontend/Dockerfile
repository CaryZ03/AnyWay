# 多阶段构建 - Vue 3前端
# 使用 Node.js 20 LTS（Vite 7.2.2 需要 Node.js 20.19+ 或 22.12+）
FROM node:20-alpine as builder

# 设置工作目录
WORKDIR /app

# 复制package文件
COPY package*.json ./

# 配置npm使用淘宝镜像源（加速安装）
RUN npm config set registry https://registry.npmmirror.com

# 安装依赖
RUN npm ci

# 复制项目文件
COPY . .

# 构建参数（用于注入环境变量）
ARG VITE_API_BASE_URL=/api/v1

# 设置环境变量（Vite 在构建时需要）
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# 构建生产版本
RUN npm run build

# 生产阶段 - 使用nginx提供静态文件
FROM nginx:alpine

# 复制构建产物到nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]
