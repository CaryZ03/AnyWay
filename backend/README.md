# AnyWay 后端本地开发指南 (Windows)

本指南仅针对 **backend 目录 (Django 后端)** 的本地开发和启动，假设你在 **Windows** 环境下开发。

---

## 1. 环境准备

- 操作系统：Windows 10/11
- 必备软件：
  - Python 3.11+（并加入环境变量 PATH）
  - Docker Desktop（用于 MySQL / Redis）
  - Git（可选，用于拉取代码）

推荐但可选：
- PowerShell 7+
- 虚拟环境工具：`python -m venv`

目录结构（后端相关）：

```text
AnyWay/
├── docker-compose.yml     # 启动 MySQL / Redis
└── backend/
    ├── aiagent/           # Django 项目配置
    ├── apps/              # 业务应用 (agent / workflow / knowledge / plugin / llm)
    ├── manage.py
    ├── requirements.txt
    ├── start.ps1          # 本地启动脚本 (本文件一起创建)
    └── README.md          # 当前说明文档
```

---

## 2. 配置环境变量

在 `backend` 目录下创建 `.env` 文件（如果还没有），可以参考 `backend/.env.example`：

```bash
# 在 backend 目录
copy .env.example .env
```

然后用编辑器打开 `.env`，至少确认：
- 数据库端口为 **3308**（与项目根目录的 `docker-compose.yml` 保持一致）
- 数据库密码与你在 `.env` 或 `.env.prod` 中的设置一致

典型配置示例（仅示意，按你的实际为准）：

```env
DB_NAME=aiagent
DB_USER=root
DB_PASSWORD=root_password
DB_HOST=localhost
DB_PORT=3308

REDIS_HOST=localhost
REDIS_PORT=6379

OPENAI_API_KEY=your-openai-api-key
```

---

## 3. 一键本地启动 (推荐)

在 `backend` 目录下我们提供了一个脚本：`start.ps1`，用于一键完成：

1. 启动 Docker 中的 MySQL、Redis
2. 安装 Python 依赖
3. 执行数据库迁移
4. 启动 Django 开发服务器

### 3.1 第一次使用 PowerShell 脚本的执行策略

如果你第一次在本机运行自定义 PowerShell 脚本，可能会遇到：

> 无法加载文件 xxx.ps1，因为在此系统上禁止运行脚本

可以在 **管理员 PowerShell** 中临时放宽执行策略（只对当前用户）：

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

如需恢复更严格策略，可以之后改回：

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Restricted
```

> 提示：公司安全策略严格时，请先确认是否允许修改执行策略。

### 3.2 使用脚本一键启动

在 **backend 目录** 打开 PowerShell：

```powershell
cd path\to\AnyWay\backend

# 一键启动 (推荐)
./start.ps1
```

脚本会：
- 在项目根目录执行 `docker-compose up -d` 启动 MySQL 和 Redis
- 在 `backend` 内执行 `pip install -r requirements.txt`
- 执行 `python manage.py makemigrations ...` 和 `python manage.py migrate`
- 最后执行 `python manage.py runserver`

### 3.3 绕过执行策略（临时方法）

如果不想修改系统执行策略，可以用一次性方式运行：

```powershell
cd path\to\AnyWay\backend
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

---

## 4. 手动本地启动（不用脚本也可以）

如果你更喜欢手动执行命令，可以按下面步骤操作。

### 4.1 启动 MySQL 和 Redis (Docker)

在 **项目根目录 AnyWay** 下：

```powershell
cd path\to\AnyWay

# 后台启动 MySQL 和 Redis
docker-compose up -d

# 查看状态
docker-compose ps
```

### 4.2 创建并激活虚拟环境（可选）

在 **backend 目录** 下：

```powershell
cd path\to\AnyWay\backend

# 创建虚拟环境（可选）
python -m venv .venv

# 激活虚拟环境
./.venv/Scripts/Activate.ps1
```

> 不想用虚拟环境也可以直接用系统 Python，但不推荐在长期开发中这么做。

### 4.3 安装依赖

```powershell
cd path\to\AnyWay\backend
pip install -r requirements.txt
```

### 4.4 数据库迁移

```powershell
cd path\to\AnyWay\backend

python manage.py makemigrations agent workflow knowledge plugin llm
python manage.py migrate
```

### 4.5 创建管理员用户

建议使用非交互方式创建/检查管理员：

```powershell
cd path\to\AnyWay\backend

python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"
```

### 4.6 启动开发服务器

```powershell
cd path\to\AnyWay\backend
python manage.py runserver
```

默认访问地址：
- 后端 API: http://localhost:8000
- 管理后台: http://localhost:8000/admin/  (admin / admin123)
- Swagger 文档: http://localhost:8000/swagger/

---

## 5. 常见问题排查

### 5.1 端口 8000 被占用

现象：启动 `manage.py runserver` 报错端口占用。

处理：
- 关闭占用 8000 端口的进程，或
- 改用其他端口，例如：
  ```powershell
  python manage.py runserver 8001
  ```

### 5.2 数据库连接错误

常见报错：`Access denied for user 'root'` 或 `Can't connect to MySQL server`。

检查：
- `docker-compose ps` 中 MySQL 容器是否是 `Up` 状态
- `backend/.env` 中 `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` 是否与 Docker 配置一致
- 端口是否为 **3308**（对宿主机暴露端口）

### 5.3 迁移时提示找不到表或模型

确认是否按顺序执行了：

```powershell
python manage.py makemigrations agent workflow knowledge plugin llm
python manage.py migrate
```

若仍有问题，可尝试：
- 删除本地数据库（开发环境）重新迁移
- 或检查各 app 的 `models.py` / `apps.py` 是否正常

### 5.4 Swagger 打不开或报错

- 确保后端已正常启动且无异常堆栈
- 检查最近是否修改了 serializer / view，特别是 Swagger 的 `ref_name` 冲突问题

---

## 6. 开发小提示

- 建议在 VS Code / PyCharm 中把工作目录设置为 `backend`
- 频繁改模型时，注意保持迁移文件整洁
- 日志默认会写入 `backend/logs/django.log`（如在 settings 中有配置）

---

## 7. 更新记录

- 2025-11-24
  - 新增 `backend/start.ps1` 一键本地启动脚本
  - 新增本 README，专门说明后端在 Windows 下的本地开发流程
