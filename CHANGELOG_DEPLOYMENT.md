# 部署系统更新日志

## 2024-12-07 - 配置化部署系统

### 新增功能

#### 1. 统一配置文件 (`config.json`)

新增配置文件用于管理前后端部署参数：

```json
{
  "backend": {
    "host": "0.0.0.0",           // 监听地址
    "port": 8000,                 // 端口
    "public_url": "http://localhost:8000"  // 对外访问地址
  },
  "frontend": {
    "host": "0.0.0.0",
    "port": 5173,
    "public_url": "http://localhost:5173",
    "api_url": "http://localhost:8000"     // 后端 API 地址
  }
}
```

**优势**:
- 集中管理所有部署参数
- 支持本地、局域网、公网等多种部署场景
- 无需修改代码即可调整配置

#### 2. 新版启动脚本

**Python 脚本** (跨平台):
- `start.py` - 启动所有服务（后台运行）
- `stop.py` - 停止所有服务
- `status.py` - 查看服务状态

**便捷脚本**:
- Windows: `start.bat`, `stop.bat`, `status.bat`
- Linux/Mac: `start.sh`, `stop.sh`, `status.sh`

**特性**:
- ✅ 后台运行，不阻塞终端
- ✅ 自动管理进程 PID
- ✅ 自动检查和安装依赖
- ✅ 跨平台支持（Windows/Linux/Mac）
- ✅ 输出清晰的访问地址

#### 3. 前端配置化

**新增文件**:
- `frontend/src/config.js` - API 配置
- `frontend/.env.example` - 环境变量示例

**修改**:
- `frontend/vite.config.js` - 支持动态 API 地址
- `frontend/src/main.js` - 配置 axios baseURL

**效果**:
- 前端可以连接到任意地址的后端
- 支持开发环境和生产环境不同配置
- 不再硬编码 API 地址

#### 4. 进程管理

新增 `.running_pids.json` 文件自动记录运行中的进程：

```json
{
  "backend": 12345,
  "frontend": 12346
}
```

可以通过 `status.py` 查看状态，`stop.py` 停止服务。

### 文档更新

新增文档：
- `README_DEPLOYMENT.md` - 详细部署指南
- `QUICKSTART_NEW.md` - 快速开始指南
- `config.json.example` - 配置文件示例
- `frontend/.env.example` - 前端环境变量示例

### 使用示例

#### 本地开发

```bash
# 1. 创建配置（使用默认值）
cp config.json.example config.json

# 2. 启动服务
python start.py

# 3. 访问
# 前端: http://localhost:5173
# 后端: http://localhost:8000
```

#### 局域网部署

```json
// config.json
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

```bash
python start.py
# 局域网访问: http://192.168.1.100:5173
```

#### 前后端分离部署

**后端服务器** (192.168.1.100):
```json
{
  "backend": {
    "host": "0.0.0.0",
    "port": 8000,
    "public_url": "http://192.168.1.100:8000"
  }
}
```

**前端服务器** (192.168.1.101):
```json
{
  "frontend": {
    "host": "0.0.0.0",
    "port": 5173,
    "public_url": "http://192.168.1.101:5173",
    "api_url": "http://192.168.1.100:8000"
  }
}
```

### 兼容性

- ✅ 保留旧版启动脚本 (`start_all.sh/bat`)
- ✅ 向后兼容，不影响现有部署
- ✅ 推荐使用新版配置化部署

### 技术细节

#### 前端 API 地址配置流程

1. `config.json` 定义 `frontend.api_url`
2. `start.py` 读取配置，生成 `frontend/.env`
3. Vite 加载 `.env` 中的 `VITE_API_BASE_URL`
4. `frontend/src/config.js` 导出 API 地址
5. `frontend/src/main.js` 配置 axios baseURL
6. 所有 API 请求使用配置的地址

#### 进程管理

- **Windows**: 使用 `CREATE_NEW_PROCESS_GROUP` 和 `taskkill`
- **Linux/Mac**: 使用 `os.setpgrp()` 和 `kill`
- PID 保存在 `.running_pids.json`
- 支持优雅停止和状态检查

### 已知限制

1. 前端开发服务器（Vite）的输出不会显示在终端
2. 需要手动查看日志文件排查问题
3. Windows 下可能需要管理员权限停止进程

### 后续计划

- [ ] 支持 Docker Compose 配置化
- [ ] 添加日志查看命令
- [ ] 支持重启单个服务
- [ ] 添加健康检查
- [ ] 支持配置验证

### 迁移指南

从旧版启动方式迁移到新版：

1. 创建配置文件:
   ```bash
   cp config.json.example config.json
   ```

2. 根据需要修改配置

3. 使用新版启动:
   ```bash
   python start.py
   ```

4. 验证服务正常运行:
   ```bash
   python status.py
   ```

就这么简单！
