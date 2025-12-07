# 故障排查指南

## 快速诊断

遇到问题时，首先运行诊断工具：

```bash
python diagnose.py
```

这会自动检查：
- Python 和 Node.js 版本
- 配置文件是否正确
- 依赖是否安装
- 端口是否被占用
- 日志文件内容

## 查看日志

### 前端日志

```bash
# 查看前端错误日志（最重要）
python logs.py frontend-error

# 查看前端完整日志
python logs.py frontend
```

### 后端日志

```bash
# 查看后端错误日志
python logs.py backend-error

# 查看后端完整日志
python logs.py backend
```

### 查看所有日志

```bash
python logs.py all
```

## 常见问题

### 1. 前端端口配置未生效

**症状**: 
- 前端日志显示监听在 5173 端口，但配置的是其他端口
- `status.py` 显示前端已停止，但实际在运行

**原因**: 
- Vite 配置未读取环境变量
- 进程检测方法不可靠

**解决方法**:

```bash
# 1. 停止服务
python stop.py

# 2. 快速更新配置
python update_config.py frontend.port=10016 backend.port=11000

# 3. 重新启动
python start.py

# 4. 验证
python status.py
python logs.py frontend
```

详细说明: [fix_frontend_port.md](fix_frontend_port.md)

### 2. 前端服务启动后立即停止

**症状**: 运行 `python status.py` 显示前端服务已停止，且日志为空

**排查步骤**:

1. 查看前端错误日志:
   ```bash
   python logs.py frontend-error
   ```

2. 常见原因:
   - **依赖未安装**: 运行 `cd frontend && npm install`
   - **Node.js 版本过低**: 需要 Node.js 16+
   - **端口被占用**: 修改 `config.json` 中的端口
   - **配置文件错误**: 检查 `frontend/.env` 是否正确生成

3. 手动测试前端:
   ```bash
   cd frontend
   npm run dev
   ```
   查看输出的错误信息

### 2. 端口被占用

**症状**: 启动时提示端口已被使用

**解决方法**:

1. 修改 `config.json`:
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

2. 或者找到占用端口的进程并终止:
   
   **Linux/Mac**:
   ```bash
   # 查找占用端口的进程
   lsof -i :8000
   lsof -i :5173
   
   # 终止进程
   kill -9 <PID>
   ```
   
   **Windows**:
   ```cmd
   # 查找占用端口的进程
   netstat -ano | findstr :8000
   netstat -ano | findstr :5173
   
   # 终止进程
   taskkill /F /PID <PID>
   ```

### 3. 前端无法连接后端

**症状**: 前端页面打开，但无法加载数据

**排查步骤**:

1. 检查后端是否运行:
   ```bash
   python status.py
   ```

2. 检查 API 地址配置:
   ```bash
   cat frontend/.env
   ```
   
   应该显示:
   ```
   VITE_API_BASE_URL=http://your-backend-url:8000
   ```

3. 检查浏览器控制台 (F12):
   - 查看是否有网络错误
   - 查看请求的 URL 是否正确

4. 测试后端 API:
   ```bash
   curl http://localhost:8000/api/plugins
   ```

5. 修复方法:
   - 确保 `config.json` 中的 `frontend.api_url` 正确
   - 重启服务: `python stop.py && python start.py`

### 4. 依赖安装失败

**症状**: 启动时提示依赖缺失

**解决方法**:

**后端依赖**:
```bash
cd backend
pip install -r requirements.txt
```

**前端依赖**:
```bash
cd frontend
npm install
```

如果 npm 安装很慢，可以使用国内镜像:
```bash
npm install --registry=https://registry.npmmirror.com
```

### 5. 配置文件错误

**症状**: 启动时提示配置文件错误

**解决方法**:

1. 检查配置文件是否存在:
   ```bash
   ls -la config.json
   ```

2. 验证 JSON 格式:
   ```bash
   python -c "import json; json.load(open('config.json', encoding='utf-8'))"
   ```

3. 重新创建配置文件:
   ```bash
   cp config.json.example config.json
   ```

### 6. 权限问题

**症状**: 无法创建文件或启动进程

**解决方法**:

**Linux/Mac**:
```bash
# 给脚本添加执行权限
chmod +x start.sh stop.sh status.sh logs.sh diagnose.sh

# 如果需要，使用 sudo
sudo python start.py
```

**Windows**:
- 以管理员身份运行命令提示符或 PowerShell

### 7. 进程残留

**症状**: 提示端口被占用，但 `status.py` 显示服务未运行

**解决方法**:

1. 清理 PID 文件:
   ```bash
   rm .running_pids.json
   ```

2. 手动查找并终止进程:
   
   **Linux/Mac**:
   ```bash
   ps aux | grep "python.*main.py"
   ps aux | grep "npm.*dev"
   kill -9 <PID>
   ```
   
   **Windows**:
   ```cmd
   tasklist | findstr python
   tasklist | findstr node
   taskkill /F /PID <PID>
   ```

### 8. 日志文件过大

**症状**: 日志文件占用大量磁盘空间

**解决方法**:

```bash
# 清空日志文件
> logs/backend.log
> logs/backend_error.log
> logs/frontend.log
> logs/frontend_error.log

# 或删除日志文件
rm logs/*.log
```

## 调试技巧

### 1. 手动启动服务

如果自动启动有问题，可以手动启动来查看详细输出:

**后端**:
```bash
cd backend
python main.py --host 0.0.0.0 --port 8000
```

**前端**:
```bash
cd frontend
npm run dev
```

### 2. 检查环境变量

```bash
# 查看前端环境变量
cat frontend/.env

# 查看系统环境变量
env | grep VITE
```

### 3. 测试网络连接

```bash
# 测试后端 API
curl http://localhost:8000/
curl http://localhost:8000/api/plugins

# 测试前端
curl http://localhost:5173/
```

### 4. 查看进程状态

**Linux/Mac**:
```bash
ps aux | grep python
ps aux | grep node
```

**Windows**:
```cmd
tasklist | findstr python
tasklist | findstr node
```

## 获取帮助

如果以上方法都无法解决问题:

1. 运行完整诊断:
   ```bash
   python diagnose.py > diagnosis.txt
   python logs.py all >> diagnosis.txt
   ```

2. 收集以下信息:
   - 操作系统和版本
   - Python 版本: `python --version`
   - Node.js 版本: `node --version`
   - npm 版本: `npm --version`
   - 配置文件内容: `cat config.json`
   - 错误日志内容
   - 诊断输出

3. 查看项目文档:
   - [快速开始](QUICKSTART_NEW.md)
   - [部署指南](README_DEPLOYMENT.md)
   - [配置说明](CONFIG_EXPLANATION.md)

## 预防措施

### 1. 定期清理日志

```bash
# 每周清理一次日志
rm logs/*.log
```

### 2. 备份配置

```bash
# 备份配置文件
cp config.json config.json.backup
```

### 3. 使用版本控制

```bash
# 提交配置更改
git add config.json
git commit -m "Update configuration"
```

### 4. 监控服务状态

```bash
# 定期检查服务状态
python status.py
```

## 性能优化

### 1. 前端构建优化

如果前端启动很慢:

```bash
cd frontend
npm run build
npm run preview
```

### 2. 后端性能

如果后端响应慢:
- 检查日志级别（改为 WARNING 或 ERROR）
- 检查数据库大小
- 检查插件配置

### 3. 网络优化

如果网络请求慢:
- 使用本地部署而不是远程
- 检查防火墙设置
- 使用 CDN 加速静态资源
