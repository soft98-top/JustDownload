# Docker 快速开始

## 一键部署

### Linux/Mac

```bash
chmod +x docker-start.sh
./docker-start.sh
```

### Windows

```cmd
docker-start.bat
```

## 使用 Makefile（Linux/Mac）

```bash
# 查看所有命令
make help

# 启动服务
make up

# 查看日志
make logs

# 停止服务
make down

# 重启服务
make restart

# 备份数据
make backup
```

## 手动部署

```bash
# 构建并启动
docker-compose up -d --build

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 访问应用

- **前端**: http://localhost
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## 常见问题

### 端口被占用

编辑 `docker-compose.yml` 修改端口映射：

```yaml
services:
  frontend:
    ports:
      - "3000:80"  # 改为 3000 端口
  backend:
    ports:
      - "8080:8000"  # 改为 8080 端口
```

### 查看日志

```bash
# 所有服务
docker-compose logs -f

# 仅后端
docker-compose logs -f backend

# 仅前端
docker-compose logs -f frontend
```

### 重新构建

```bash
docker-compose down
docker-compose up -d --build
```

### 清理所有数据

```bash
docker-compose down -v
```

## 数据持久化

以下目录会自动挂载到宿主机：

- `backend/config/` - 插件配置
- `backend/data/` - 数据库
- `backend/logs/` - 日志文件
- `backend/plugins/` - 插件代码

即使删除容器，这些数据也会保留。

## 更多信息

详细文档请查看 [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
