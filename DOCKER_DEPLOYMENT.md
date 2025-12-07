# Docker 部署指南

## 快速开始

### 使用 Docker Compose（推荐）

1. **构建并启动所有服务**
```bash
docker-compose up -d
```

2. **查看服务状态**
```bash
docker-compose ps
```

3. **查看日志**
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看后端日志
docker-compose logs -f backend

# 查看前端日志
docker-compose logs -f frontend
```

4. **停止服务**
```bash
docker-compose down
```

5. **重新构建并启动**
```bash
docker-compose up -d --build
```

### 访问应用

- **前端**: http://localhost
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## 单独构建

### 构建后端镜像

```bash
cd backend
docker build -t justdownload-backend .
docker run -d -p 8000:8000 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  justdownload-backend
```

### 构建前端镜像

```bash
cd frontend
docker build -t justdownload-frontend .
docker run -d -p 80:80 justdownload-frontend
```

## 配置说明

### 环境变量

在 `docker-compose.yml` 中可以配置以下环境变量：

**后端环境变量**:
- `LOG_LEVEL`: 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
- `PYTHONUNBUFFERED`: Python 输出缓冲设置

### 数据持久化

以下目录会被挂载到宿主机，确保数据持久化：

- `./backend/config` - 插件配置
- `./backend/data` - 数据库文件
- `./backend/logs` - 日志文件
- `./backend/plugins` - 插件代码

### 端口配置

默认端口映射：
- 前端: `80:80`
- 后端: `8000:8000`

如需修改，编辑 `docker-compose.yml` 中的 `ports` 配置：

```yaml
services:
  backend:
    ports:
      - "8080:8000"  # 将后端映射到宿主机 8080 端口
  
  frontend:
    ports:
      - "3000:80"    # 将前端映射到宿主机 3000 端口
```

## 生产环境建议

### 1. 使用环境变量文件

创建 `.env` 文件：

```env
# 后端配置
LOG_LEVEL=INFO
BACKEND_PORT=8000

# 前端配置
FRONTEND_PORT=80
```

修改 `docker-compose.yml` 使用环境变量：

```yaml
services:
  backend:
    ports:
      - "${BACKEND_PORT}:8000"
    env_file:
      - .env
```

### 2. 使用 HTTPS

在生产环境中，建议使用 Nginx 反向代理并配置 SSL 证书：

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:80;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
    }
}
```

### 3. 资源限制

在 `docker-compose.yml` 中添加资源限制：

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 4. 健康检查

添加健康检查配置：

```yaml
services:
  backend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

## 故障排查

### 查看容器日志

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 进入容器调试

```bash
# 进入后端容器
docker-compose exec backend /bin/bash

# 进入前端容器
docker-compose exec frontend /bin/sh
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启单个服务
docker-compose restart backend
```

### 清理并重建

```bash
# 停止并删除容器、网络
docker-compose down

# 删除所有数据（谨慎使用）
docker-compose down -v

# 重新构建并启动
docker-compose up -d --build
```

## 更新应用

### 更新代码后重新部署

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build
```

### 仅更新后端

```bash
docker-compose up -d --build backend
```

### 仅更新前端

```bash
docker-compose up -d --build frontend
```

## 备份与恢复

### 备份数据

```bash
# 备份配置和数据
tar -czf backup-$(date +%Y%m%d).tar.gz \
  backend/config \
  backend/data \
  backend/plugins
```

### 恢复数据

```bash
# 解压备份
tar -xzf backup-20231201.tar.gz

# 重启服务
docker-compose restart
```

## 监控

### 查看资源使用

```bash
docker stats
```

### 查看容器详情

```bash
docker-compose ps
docker inspect justdownload-backend
docker inspect justdownload-frontend
```
