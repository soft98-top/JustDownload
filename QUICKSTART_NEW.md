# 快速开始（新版配置化部署）

本指南介绍如何使用新的配置化部署方式快速启动系统。

## 前置要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

## 快速启动（3 步）

### 1. 配置部署参数

首次使用需要创建配置文件：

```bash
# 复制示例配置
cp config.json.example config.json

# 编辑配置（可选，默认配置适用于本地开发）
# Windows: notepad config.json
# Linux/Mac: nano config.json
```

**默认配置**（本地开发）：
```json
{
  "backend": {
    "host": "0.0.0.0",
    "port": 8000,
    "public_url": "http://localhost:8000"
  },
  "frontend": {
    "host": "0.0.0.0",
    "port": 5173,
    "public_url": "http://localhost:5173",
    "api_url": "http://localhost:8000"
  }
}
```

### 2. 启动服务

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**或直接使用 Python:**
```bash
python start.py
```

启动成功后会显示：
```
==================================================
服务已启动
==================================================
后端 API: http://localhost:8000
前端界面: http://localhost:5173

提示:
  - 进程已在后台运行
  - 使用 'python stop.py' 停止所有服务
  - 使用 'python status.py' 查看服务状态
==================================================
```

### 3. 访问系统

打开浏览器访问: **http://localhost:5173**

## 常用命令

### 查看服务状态

```bash
# Windows
status.bat

# Linux/Mac
./status.sh

# 或
python status.py
```

### 停止服务

```bash
# Windows
stop.bat

# Linux/Mac
./stop.sh

# 或
python stop.py
```

### 重启服务

```bash
# 先停止
python stop.py

# 再启动
python start.py
```

## 不同部署场景

### 场景 1: 本地开发（默认）

使用默认配置即可，访问 http://localhost:5173

### 场景 2: 局域网访问

假设你的电脑 IP 是 `192.168.1.100`，修改 `config.json`：

```json
{
  "backend": {
    "host": "0.0.0.0",
    "port": 8000,
    "public_url": "http://192.168.1.100:8000"
  },
  "frontend": {
    "host": "0.0.0.0",
    "port": 5173,
    "public_url": "http://192.168.1.100:5173",
    "api_url": "http://192.168.1.100:8000"
  }
}
```

局域网内其他设备访问: http://192.168.1.100:5173

**注意**: 需要确保防火墙开放了 8000 和 5173 端口。

### 场景 3: 修改端口

如果默认端口被占用，可以修改：

```json
{
  "backend": {
    "port": 9000,
    "public_url": "http://localhost:9000"
  },
  "frontend": {
    "port": 3000,
    "public_url": "http://localhost:3000",
    "api_url": "http://localhost:9000"
  }
}
```

## 常见问题

### Q: 端口被占用怎么办？

A: 修改 `config.json` 中的端口号，然后重启服务。

### Q: 如何让局域网内其他设备访问？

A: 
1. 确保 `host` 设置为 `0.0.0.0`
2. 将 `public_url` 和 `api_url` 中的 `localhost` 改为你的实际 IP
3. 开放防火墙端口

### Q: 前端无法连接后端？

A: 检查 `frontend.api_url` 是否正确，必须是浏览器能访问到的地址。

### Q: 如何查看日志？

A: 
- 后端日志: `backend/logs/`
- 前端日志: 浏览器控制台（F12）

### Q: 服务启动失败？

A: 
1. 检查 Python 和 Node.js 是否正确安装
2. 检查端口是否被占用
3. 查看错误信息排查问题

## 下一步

- 📖 查看 [README_DEPLOYMENT.md](README_DEPLOYMENT.md) 了解详细部署说明
- ⚙️ 访问设置页面配置插件
- 🔍 开始搜索和下载

## 与旧版启动方式的区别

| 特性 | 旧版 | 新版 |
|------|------|------|
| 配置 | 硬编码 | 配置文件 |
| 运行 | 前台阻塞 | 后台运行 |
| 管理 | 手动 | 自动 PID 管理 |
| 灵活性 | 低 | 高 |

旧版脚本（`start_all.sh/bat`）仍然可用，但推荐使用新版。
