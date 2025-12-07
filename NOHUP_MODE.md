# Nohup 模式启动指南

## 简介

nohup 模式使用传统的 Linux `nohup` 命令启动服务，比 Python 的 subprocess 方式更可靠。

## 优势

- ✅ **更可靠**: 使用系统原生的 nohup 命令
- ✅ **更稳定**: 进程不会因为父进程退出而终止
- ✅ **更简单**: 直接使用 shell 脚本，易于理解和调试
- ✅ **更灵活**: 可以轻松查看和管理进程

## 快速开始

### 1. 给脚本添加执行权限

```bash
chmod +x start_nohup.sh stop_nohup.sh status_nohup.sh
```

### 2. 启动服务

```bash
./start_nohup.sh
```

### 3. 查看状态

```bash
./status_nohup.sh
```

### 4. 停止服务

```bash
./stop_nohup.sh
```

## 详细说明

### 启动服务 (start_nohup.sh)

```bash
./start_nohup.sh
```

这个脚本会：
1. 读取 `config.json` 配置
2. 生成前端环境变量文件
3. 使用 nohup 启动后端服务
4. 使用 nohup 启动前端服务
5. 保存进程 PID 到 `.running_pids.json`
6. 检查服务是否启动成功
7. 显示访问地址和日志位置

**输出示例**:
```
==================================================
启动模块化下载系统 (nohup 模式)
==================================================

配置信息:
  后端: 0.0.0.0:11000
  前端: 0.0.0.0:10016
  API: http://192.168.0.106:11000

✓ 已生成前端环境配置

启动后端服务...
  后端 PID: 12345
  等待后端启动...

启动前端服务...
  前端 PID: 12346
  等待前端启动...

==================================================
服务已启动
==================================================
后端 PID: 12345
前端 PID: 12346

访问地址:
  后端: http://192.168.0.106:11000
  前端: http://192.168.0.106:10016

日志文件:
  后端: logs/backend.log, logs/backend_error.log
  前端: logs/frontend.log, logs/frontend_error.log
==================================================
```

### 查看状态 (status_nohup.sh)

```bash
./status_nohup.sh
```

这个脚本会：
1. 显示配置信息
2. 显示进程 PID
3. **检查端口是否开放**（最可靠）
4. 检查 HTTP 响应
5. 显示相关进程列表
6. 显示日志文件信息

**输出示例**:
```
==================================================
服务状态 (nohup 模式)
==================================================

配置信息:
  后端: http://192.168.0.106:11000
  前端: http://192.168.0.106:10016

进程信息:
  后端 PID: 12345
  前端 PID: 12346

端口状态:
  ✓ 后端端口 11000 开放 (12345/python3)
  ✓ 前端端口 10016 开放 (12347/node)

HTTP 响应:
  ✓ 后端 HTTP 响应正常
  ✓ 前端 HTTP 响应正常

相关进程:
  PID: 12345    CPU: 0.5%  MEM: 2.1%  CMD: python3 main.py
  PID: 12347    CPU: 1.2%  MEM: 3.5%  CMD: node vite
==================================================
```

### 停止服务 (stop_nohup.sh)

```bash
./stop_nohup.sh
```

这个脚本会：
1. 读取 PID 文件
2. 终止后端进程
3. 终止前端进程及其子进程
4. 如果 PID 文件不存在，通过端口查找进程
5. 验证服务已停止
6. 清理 PID 文件

## 日志管理

### 查看日志

```bash
# 查看前端日志
tail -f logs/frontend.log

# 查看前端错误日志
tail -f logs/frontend_error.log

# 查看后端日志
tail -f logs/backend.log

# 查看后端错误日志
tail -f logs/backend_error.log

# 或使用 Python 脚本
python3 logs.py all
```

### 清理日志

```bash
# 清空日志文件
> logs/backend.log
> logs/backend_error.log
> logs/frontend.log
> logs/frontend_error.log

# 或删除日志文件
rm logs/*.log
```

## 常用命令

### 检查端口

```bash
# 检查端口是否开放
netstat -tlnp | grep 10016
netstat -tlnp | grep 11000

# 或使用 ss
ss -tlnp | grep 10016
ss -tlnp | grep 11000
```

### 查看进程

```bash
# 查看所有相关进程
ps aux | grep -E "python.*main.py|npm.*dev|node.*vite"

# 查看进程树
pstree -p | grep -A 5 npm
```

### 手动终止进程

```bash
# 通过 PID 终止
kill -9 12345

# 通过端口终止
kill -9 $(lsof -ti:10016)
kill -9 $(lsof -ti:11000)
```

## 故障排查

### 问题 1: 服务启动后立即退出

**检查**:
```bash
# 查看错误日志
tail -50 logs/frontend_error.log
tail -50 logs/backend_error.log
```

**常见原因**:
- 端口被占用
- 依赖缺失
- 配置错误

### 问题 2: 端口未开放

**检查**:
```bash
# 检查端口
netstat -tlnp | grep 10016

# 如果没有输出，查看日志
tail -50 logs/frontend_error.log
```

**解决**:
```bash
# 重新安装依赖
cd frontend
npm install

# 重启服务
cd ..
./stop_nohup.sh
./start_nohup.sh
```

### 问题 3: 防火墙阻止

**检查**:
```bash
sudo ufw status
```

**解决**:
```bash
sudo ufw allow 10016/tcp
sudo ufw allow 11000/tcp
sudo ufw reload
```

## 与 Python 模式对比

| 特性 | Python 模式 | Nohup 模式 |
|------|------------|-----------|
| 启动方式 | `python start.py` | `./start_nohup.sh` |
| 进程管理 | subprocess | nohup |
| 可靠性 | 中等 | 高 |
| 调试难度 | 较难 | 容易 |
| 跨平台 | 是 | 仅 Linux/Mac |
| 日志查看 | 文件 | 文件 |
| 进程检测 | 可能不准确 | 准确 |

## 推荐使用场景

### 使用 Nohup 模式

- ✅ Linux/Mac 服务器
- ✅ 生产环境
- ✅ 需要长期运行
- ✅ 需要可靠的进程管理

### 使用 Python 模式

- ✅ Windows 系统
- ✅ 开发环境
- ✅ 需要跨平台
- ✅ 快速测试

## 最佳实践

### 1. 定期检查服务状态

```bash
# 添加到 crontab
*/5 * * * * cd /path/to/project && ./status_nohup.sh >> logs/status.log 2>&1
```

### 2. 日志轮转

```bash
# 每天轮转日志
0 0 * * * cd /path/to/project && mv logs/frontend.log logs/frontend.log.$(date +\%Y\%m\%d) && touch logs/frontend.log
```

### 3. 自动重启

```bash
# 如果服务停止，自动重启
*/10 * * * * cd /path/to/project && ./status_nohup.sh | grep -q "未开放" && ./start_nohup.sh
```

## 总结

Nohup 模式提供了更可靠的服务管理方式，特别适合 Linux 服务器环境。

**现在就试试**:
```bash
chmod +x start_nohup.sh stop_nohup.sh status_nohup.sh
./start_nohup.sh
```
