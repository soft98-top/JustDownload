# 修复前端端口问题

## 问题说明

前端服务启动了，但是：
1. 监听在默认端口 5173，而不是配置的端口
2. 进程检测显示"已停止"（实际在运行）

## 解决方案

### 方案 1: 快速修复（推荐）

```bash
# 1. 停止当前服务
python stop.py

# 2. 更新配置（如果你想用端口 10016）
python update_config.py frontend.port=10016 backend.port=11000

# 或者交互式更新
python update_config.py

# 3. 重新启动
python start.py

# 4. 检查状态（现在应该显示正确了）
python status.py
```

### 方案 2: 手动修改配置

编辑 `config.json`:

```json
{
  "backend": {
    "host": "0.0.0.0",
    "port": 11000,
    "public_url": "http://192.168.0.106:11000"
  },
  "frontend": {
    "host": "0.0.0.0",
    "port": 10016,
    "public_url": "http://192.168.0.106:10016",
    "api_url": "http://192.168.0.106:11000"
  }
}
```

然后重启服务：
```bash
python stop.py
python start.py
```

## 验证修复

```bash
# 1. 检查服务状态
python status.py

# 2. 检查前端日志，应该显示正确的端口
python logs.py frontend

# 3. 访问前端
# http://192.168.0.106:10016
```

## 为什么会出现这个问题？

1. **端口配置未生效**: 旧版 `vite.config.js` 没有读取环境变量中的端口
2. **进程检测问题**: Linux 下的进程检测方法不够可靠

这两个问题现在都已修复！

## 已修复的内容

1. ✅ 修改 `frontend/vite.config.js` 支持从环境变量读取端口和主机
2. ✅ 修改 `status.py` 改进 Linux 下的进程检测
3. ✅ 创建 `update_config.py` 方便快速更新配置

## 注意事项

- 修改配置后必须重启服务才能生效
- 确保新端口没有被其他程序占用
- 如果使用防火墙，需要开放对应端口
