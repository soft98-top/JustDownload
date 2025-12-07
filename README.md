# JustDownload - 模块化下载系统

一个基于插件架构的视频搜索和下载系统。

## 功能特性

- 🔌 插件化架构：支持搜索、下载、解析器插件
- 🔍 多平台搜索：支持多个视频平台的搜索
- ⬇️ 多种下载方式：支持HTTP、M3U8、磁力链接等
- 🎯 动态插件管理：在线安装、卸载插件
- ⚡ 插件热加载：安装/删除插件无需重启服务
- ⚙️ 配置导入导出：一键备份和恢复所有配置
- 🌐 Web界面：友好的前端操作界面

## 快速开始

### 方式一：配置化部署（推荐 ⭐）

支持灵活配置，适用于本地、局域网、公网等多种场景。

```bash
# 1. 创建配置文件
cp config.json.example config.json

# 2. 启动服务（后台运行）
python start.py

# 3. 访问系统
# 前端: http://localhost:5173
# 后端: http://localhost:8000
```

**管理命令:**
```bash
python status.py    # 查看服务状态
python stop.py      # 停止所有服务
python logs.py all  # 查看日志
python diagnose.py  # 运行诊断
```

**或使用便捷脚本:**
- Windows: `start.bat`, `stop.bat`, `status.bat`, `logs.bat`, `diagnose.bat`
- Linux/Mac: `./start.sh`, `./stop.sh`, `./status.sh`, `./logs.sh`, `./diagnose.sh`

**Linux/Mac 推荐使用 nohup 模式（更可靠）:**
```bash
chmod +x start_nohup.sh stop_nohup.sh status_nohup.sh
./start_nohup.sh  # 启动
./status_nohup.sh # 状态
./stop_nohup.sh   # 停止
```
📖 详细说明: [Nohup 模式指南](NOHUP_MODE.md)

📖 详细说明: [快速开始指南](QUICKSTART_NEW.md) | [部署指南](README_DEPLOYMENT.md) | [故障排查](TROUBLESHOOTING.md)

### 方式二：Docker 部署

使用 Docker Compose 一键部署：

```bash
docker-compose up -d
```

访问应用：
- 前端: http://localhost
- 后端 API: http://localhost:8000

详细说明请查看 [Docker 部署指南](DOCKER_DEPLOYMENT.md)

### 方式三：传统启动脚本

**Linux/Mac:**
```bash
chmod +x install_dependencies.sh start_all.sh
./install_dependencies.sh  # 首次运行
./start_all.sh            # 启动服务（前台运行）
```

**Windows:**
```cmd
install_dependencies.bat  # 首次运行
start_all.bat            # 启动服务（前台运行）
```

### 方式四：手动启动

#### 后端

```bash
cd backend
pip install -r requirements.txt
python main.py
```

#### 前端

```bash
cd frontend
npm install
npm run dev
```

## 插件系统

### 插件类型

1. **搜索插件** - 从各个平台搜索视频
2. **下载插件** - 处理不同协议的下载任务
3. **解析器插件** - 解析视频播放地址

### 插件自动发现

系统启动时会自动扫描插件目录，加载所有符合规范的插件：
- 无需在代码中手动注册插件
- 插件文件放入对应目录即可自动加载
- 支持零配置部署

### 插件管理

- 所有插件默认禁用，需要在设置中手动启用
- 支持在线安装插件（输入插件URL）
- 支持删除已安装的插件
- **支持插件热加载/热卸载，无需重启服务**
- 每个插件可以有独立的依赖文件

## 配置管理

在设置界面可以：
- 导出所有配置为JSON文件
- 导入配置文件快速恢复设置
- 管理插件的启用/禁用状态

## 项目结构

```
JustDownload/
├── backend/              # 后端服务
│   ├── plugins/         # 插件目录
│   │   ├── search/      # 搜索插件
│   │   ├── download/    # 下载插件
│   │   └── parser/      # 解析器插件
│   ├── config/          # 配置文件
│   └── requirements.txt # 核心依赖
├── frontend/            # 前端界面
└── README.md
```

## 开发插件

参考 `backend/plugins/search/plugin_template.py` 创建新插件。

## License

MIT
