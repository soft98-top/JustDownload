# 前端无法访问 - 调试指南

## 问题

浏览器无法访问 http://192.168.0.106:10016/

## 可能的原因

1. **前端服务实际未运行** - Vite 启动后立即退出
2. **防火墙阻止** - 端口被防火墙拦截
3. **配置错误** - 环境变量或配置不正确
4. **依赖问题** - 前端依赖有问题导致启动失败

## 排查步骤

### 步骤 1: 检查端口是否真的开放

```bash
# 在服务器上执行
netstat -tlnp | grep 10016

# 或使用 ss
ss -tlnp | grep 10016
```

**如果没有输出**，说明端口未开放，前端服务没有运行。

### 步骤 2: 查看前端错误日志

```bash
python logs.py frontend-error
```

查看是否有错误信息。

### 步骤 3: 手动启动前端（查看详细错误）

```bash
cd frontend
npm run dev
```

**不要后台运行**，直接在终端查看输出。看是否有错误信息。

### 步骤 4: 检查防火墙

```bash
# 检查防火墙状态
sudo ufw status

# 如果防火墙开启，添加规则
sudo ufw allow 10016/tcp
sudo ufw allow 11000/tcp

# 或者临时关闭防火墙测试
sudo ufw disable
```

### 步骤 5: 检查配置

```bash
# 查看配置文件
cat config.json

# 查看前端环境变量
cat frontend/.env

# 应该显示正确的 API 地址
```

### 步骤 6: 检查进程

```bash
# 查看所有相关进程
ps aux | grep -E "node|vite|npm"

# 如果没有输出，说明前端确实没有运行
```

## 常见问题和解决方案

### 问题 1: 前端启动后立即退出

**原因**: 
- 依赖问题
- 配置错误
- 端口被占用

**解决**:
```bash
# 重新安装依赖
cd frontend
rm -rf node_modules package-lock.json
npm install

# 检查端口
netstat -tlnp | grep 10016

# 如果端口被占用，修改配置
python update_config.py frontend.port=3000
```

### 问题 2: 防火墙阻止

**解决**:
```bash
# 开放端口
sudo ufw allow 10016/tcp
sudo ufw allow 11000/tcp

# 重启防火墙
sudo ufw reload
```

### 问题 3: 环境变量不正确

**解决**:
```bash
# 检查 frontend/.env
cat frontend/.env

# 应该是:
# VITE_API_BASE_URL=http://192.168.0.106:11000

# 如果不对，手动修改或运行
python fix_and_restart.py
```

### 问题 4: Vite 配置问题

**检查** `frontend/vite.config.js`:

```javascript
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())
  const apiBaseUrl = env.VITE_API_BASE_URL || 'http://localhost:8000'
  const port = parseInt(env.VITE_PORT || '5173')
  const host = env.VITE_HOST || '0.0.0.0'
  
  return {
    plugins: [vue()],
    server: {
      host: host,
      port: port,
      // ...
    }
  }
})
```

## 快速修复

### 方法 1: 使用修复脚本（推荐）

```bash
python fix_and_restart.py
```

这会：
1. 停止所有服务
2. 更新前端环境变量
3. 重新启动服务
4. 检查服务状态

### 方法 2: 手动修复

```bash
# 1. 停止服务
python stop.py

# 2. 更新前端环境变量
echo "VITE_API_BASE_URL=http://192.168.0.106:11000" > frontend/.env

# 3. 重新启动
python start.py

# 4. 等待 5 秒
sleep 5

# 5. 检查服务
python check_services.py
```

### 方法 3: 前台运行（调试用）

```bash
# 停止后台服务
python stop.py

# 手动启动后端（新终端）
cd backend
python main.py --host 0.0.0.0 --port 11000

# 手动启动前端（新终端）
cd frontend
export VITE_API_BASE_URL=http://192.168.0.106:11000
export VITE_PORT=10016
export VITE_HOST=0.0.0.0
npm run dev
```

## 验证修复

### 1. 检查端口

```bash
netstat -tlnp | grep 10016
```

应该看到类似：
```
tcp  0  0  0.0.0.0:10016  0.0.0.0:*  LISTEN  12345/node
```

### 2. 本地访问测试

```bash
curl http://127.0.0.1:10016/
```

应该返回 HTML 内容。

### 3. 远程访问测试

在另一台机器上：
```bash
curl http://192.168.0.106:10016/
```

### 4. 浏览器访问

打开浏览器，访问: http://192.168.0.106:10016/

## 如果还是不行

### 收集诊断信息

```bash
# 运行完整诊断
python diagnose.py > diagnosis.txt

# 查看所有日志
python logs.py all >> diagnosis.txt

# 检查服务
python check_services.py >> diagnosis.txt

# 查看网络
netstat -tlnp >> diagnosis.txt

# 查看进程
ps aux | grep -E "node|vite|npm|python" >> diagnosis.txt
```

### 检查系统日志

```bash
# 查看系统日志
sudo journalctl -xe | tail -100

# 查看 dmesg
sudo dmesg | tail -50
```

### 尝试不同的端口

```bash
# 使用标准端口
python update_config.py frontend.port=3000 backend.port=8000

# 重启
python stop.py
python start.py
```

## 最简单的测试

如果所有方法都不行，尝试最简单的配置：

```bash
# 1. 停止所有服务
python stop.py

# 2. 使用默认配置
cp config.json.example config.json

# 3. 启动
python start.py

# 4. 访问
# http://localhost:5173  (本地)
# http://192.168.0.106:5173  (远程)
```

## 总结

最常见的问题：
1. ✅ 防火墙阻止 - 开放端口
2. ✅ 环境变量错误 - 运行 fix_and_restart.py
3. ✅ 依赖问题 - 重新安装 npm install
4. ✅ 端口冲突 - 修改端口

**下一步**: 运行 `python fix_and_restart.py` 尝试自动修复！
