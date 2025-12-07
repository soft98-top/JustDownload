# 🚀 从这里开始

欢迎使用 JustDownload 模块化下载系统！

## 三步快速启动

### 第一步：创建配置文件

```bash
# 复制示例配置
cp config.json.example config.json
```

或者在 Windows 上：
```cmd
copy config.json.example config.json
```

### 第二步：启动服务

**最简单的方式（推荐）:**

Windows 用户双击: `start.bat`

Linux/Mac 用户运行: `./start.sh`

**或者使用 Python:**
```bash
python start.py
```

### 第三步：访问系统

打开浏览器访问: **http://localhost:5173**

就这么简单！🎉

## 管理服务

### 查看服务状态

```bash
python status.py
```

或双击 `status.bat` (Windows) / 运行 `./status.sh` (Linux/Mac)

### 停止服务

```bash
python stop.py
```

或双击 `stop.bat` (Windows) / 运行 `./stop.sh` (Linux/Mac)

## 需要帮助？

- 📖 [快速开始指南](QUICKSTART_NEW.md) - 详细的入门教程
- 🔧 [配置说明](CONFIG_EXPLANATION.md) - 配置文件详解
- 🌐 [部署指南](README_DEPLOYMENT.md) - 各种部署场景
- 📋 [完整文档](README.md) - 系统功能介绍

## 常见场景

### 本地开发（默认）

使用默认配置即可，无需修改。

### 局域网访问

编辑 `config.json`，将 `localhost` 改为你的 IP 地址：

```json
{
  "backend": {
    "public_url": "http://192.168.1.100:8000"
  },
  "frontend": {
    "public_url": "http://192.168.1.100:5173",
    "api_url": "http://192.168.1.100:8000"
  }
}
```

### 修改端口

编辑 `config.json`，修改 `port` 字段：

```json
{
  "backend": {
    "port": 9000
  },
  "frontend": {
    "port": 3000
  }
}
```

## 遇到问题？

### 运行诊断工具

```bash
python diagnose.py
```

这会检查所有依赖和配置，帮助你快速定位问题。

### 查看日志

```bash
# 查看前端错误日志（最常用）
python logs.py frontend-error

# 查看后端错误日志
python logs.py backend-error

# 查看所有日志
python logs.py all
```

### 常见问题

**端口被占用**
- 修改 `config.json` 中的端口号，然后重启服务

**前端无法连接后端**
- 检查 `config.json` 中的 `frontend.api_url` 是否正确
- 确保后端服务正在运行: `python status.py`

**前端服务启动后立即停止**
- 查看前端错误日志: `python logs.py frontend-error`
- 检查 Node.js 和 npm 是否正确安装
- 检查前端依赖是否安装: `cd frontend && npm install`

**服务启动失败**
1. 运行诊断: `python diagnose.py`
2. 确保 Python 3.8+ 和 Node.js 16+ 已安装
3. 检查端口是否被占用
4. 查看错误日志

## 下一步

1. ⚙️ 访问设置页面配置插件
2. 🔍 开始搜索视频
3. ⬇️ 创建下载任务

祝使用愉快！
