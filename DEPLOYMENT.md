# 部署指南

## 零配置部署

得益于插件自动发现机制，JustDownload支持零配置部署。

### 最小化部署

只需要核心文件即可运行：

```
JustDownload/
├── backend/
│   ├── plugins/          # 插件目录（可以为空）
│   │   ├── search/
│   │   ├── download/
│   │   └── parser/
│   ├── config/
│   │   └── plugins.json  # 配置文件
│   ├── *.py              # 核心Python文件
│   └── requirements.txt
└── frontend/
    └── dist/             # 前端构建产物
```

### 部署步骤

#### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 2. 启动服务

```bash
python main.py
```

就这么简单！系统会自动：
- 扫描插件目录
- 加载所有可用插件
- 启动API服务

#### 3. 访问界面

打开浏览器访问：`http://localhost:5173`（开发模式）或部署的前端地址

## 添加插件

### 方式1：直接复制文件

将插件文件复制到对应目录：

```bash
# 添加搜索插件
cp my_plugin.py backend/plugins/search/

# 添加插件依赖（如果有）
cp my_requirements.txt backend/plugins/search/

# 安装依赖
pip install -r backend/plugins/search/my_requirements.txt
```

然后：
- **重启服务**，或
- **在Web界面点击"重新加载插件"**

### 方式2：在线安装

1. 在Web界面进入"设置"页面
2. 点击"📦 安装插件"
3. 输入插件URL
4. 系统自动下载、安装依赖、热加载

## 生产环境部署

### 使用Gunicorn（推荐）

```bash
pip install gunicorn

gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### 使用Docker

创建 `Dockerfile`：

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY backend/ .

# 暴露端口
EXPOSE 8000

# 启动服务
CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "8000"]
```

构建和运行：

```bash
docker build -t justdownload .
docker run -d -p 8000:8000 -v ./plugins:/app/plugins justdownload
```

### 使用Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 环境变量配置

支持通过环境变量配置：

```bash
# 日志级别
export LOG_LEVEL=INFO

# 详细日志
export VERBOSE=true

# 启动服务
python main.py
```

或使用命令行参数：

```bash
python main.py --log-level DEBUG --verbose --host 0.0.0.0 --port 8000
```

## 数据持久化

### 配置文件

配置保存在 `backend/config/plugins.json`，建议定期备份：

```bash
# 备份配置
cp backend/config/plugins.json backup/plugins.json.$(date +%Y%m%d)

# 或通过Web界面导出
```

### 数据库

下载任务数据保存在 `backend/data/` 目录（如果使用本地数据库）。

### 日志

日志保存在 `backend/logs/` 目录。

## 多实例部署

如果需要负载均衡，可以部署多个后端实例：

```bash
# 实例1
python main.py --port 8001

# 实例2
python main.py --port 8002

# 实例3
python main.py --port 8003
```

然后使用Nginx进行负载均衡：

```nginx
upstream backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    location /api {
        proxy_pass http://backend;
    }
}
```

## 安全建议

1. **使用HTTPS**：生产环境必须使用HTTPS
2. **限制访问**：使用防火墙限制API访问
3. **定期更新**：及时更新依赖包
4. **备份配置**：定期导出配置备份
5. **监控日志**：监控异常日志和错误

## 性能优化

1. **使用生产级ASGI服务器**：Gunicorn + Uvicorn
2. **启用缓存**：使用Redis缓存搜索结果
3. **CDN加速**：前端静态资源使用CDN
4. **数据库优化**：使用PostgreSQL替代SQLite
5. **限流保护**：使用Nginx限流防止滥用

## 故障排除

### 问题1：插件加载失败

**检查**：
```bash
# 查看日志
tail -f backend/logs/app.log

# 手动测试插件
python -c "from plugins.search.my_plugin import *"
```

### 问题2：端口被占用

**解决**：
```bash
# 查找占用端口的进程
lsof -i :8000

# 或使用其他端口
python main.py --port 8001
```

### 问题3：依赖安装失败

**解决**：
```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或手动安装
pip install fastapi uvicorn httpx
```

## 监控和维护

### 健康检查

```bash
# 检查服务状态
curl http://localhost:8000/

# 检查插件列表
curl http://localhost:8000/api/plugins
```

### 日志轮转

使用logrotate管理日志：

```
/path/to/backend/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### 自动重启

使用systemd管理服务：

```ini
[Unit]
Description=JustDownload Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/backend
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启用服务：

```bash
sudo systemctl enable justdownload
sudo systemctl start justdownload
```

## 更新升级

### 更新代码

```bash
# 备份配置
cp backend/config/plugins.json backup/

# 拉取最新代码
git pull

# 更新依赖
pip install -r backend/requirements.txt --upgrade

# 重启服务
systemctl restart justdownload
```

### 更新插件

1. 在Web界面删除旧插件
2. 安装新版本插件
3. 或直接替换插件文件后重新加载

## 总结

JustDownload的零配置部署特性使得部署和维护变得非常简单：

✅ 无需修改代码
✅ 插件即插即用
✅ 支持热加载
✅ 易于扩展
✅ 便于维护
