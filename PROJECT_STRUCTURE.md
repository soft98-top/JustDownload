# 项目结构

```
JustDownload/
├── backend/                    # 后端服务
│   ├── plugins/               # 插件目录
│   │   ├── search/           # 搜索插件
│   │   │   ├── plugin_template.py              # 插件模板
│   │   │   ├── plugin_template_requirements.txt
│   │   │   ├── jable_plugin.py                 # JableTV插件
│   │   │   ├── jable_requirements.txt
│   │   │   ├── seacms_plugin.py                # SeaCMS插件
│   │   │   └── seacms_requirements.txt
│   │   ├── download/         # 下载插件
│   │   │   ├── metube_plugin.py                # Metube插件
│   │   │   ├── metube_requirements.txt
│   │   │   ├── qbittorrent_plugin.py           # qBittorrent插件
│   │   │   └── qbittorrent_requirements.txt
│   │   ├── parser/           # 解析器插件
│   │   │   └── m3u8_parser_plugin.py           # M3U8解析器
│   │   └── README.md         # 插件开发指南
│   ├── config/               # 配置文件
│   │   └── plugins.json      # 插件配置
│   ├── data/                 # 数据目录
│   ├── logs/                 # 日志目录
│   ├── base_plugin.py        # 插件基类
│   ├── config_storage.py     # 配置存储
│   ├── database.py           # 数据库
│   ├── logger.py             # 日志模块
│   ├── main.py               # 主程序入口
│   ├── models.py             # 数据模型
│   ├── plugin_manager.py     # 插件管理器
│   ├── search_task_manager.py # 搜索任务管理
│   ├── requirements.txt      # 核心依赖
│   └── start.sh              # 启动脚本
├── frontend/                  # 前端界面
│   ├── src/
│   │   ├── components/       # 组件
│   │   │   ├── ImagePreview.vue
│   │   │   └── PluginConfig.vue
│   │   ├── views/            # 页面
│   │   │   ├── Search.vue    # 搜索页面
│   │   │   ├── Downloads.vue # 下载页面
│   │   │   └── Settings.vue  # 设置页面
│   │   ├── utils/            # 工具
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── README.md                  # 项目说明
├── PROJECT_STRUCTURE.md       # 项目结构（本文件）
└── start_all.sh              # 一键启动脚本

```

## 核心模块说明

### 后端

- **main.py**: FastAPI应用入口，定义所有API路由
- **plugin_manager.py**: 插件管理器，负责插件注册、配置、调用
- **base_plugin.py**: 插件基类定义
- **config_storage.py**: 配置持久化存储
- **search_task_manager.py**: 异步搜索任务管理
- **database.py**: 下载任务数据库
- **logger.py**: 日志配置
- **models.py**: Pydantic数据模型

### 前端

- **Search.vue**: 搜索界面，支持多插件搜索
- **Downloads.vue**: 下载管理界面
- **Settings.vue**: 插件配置界面，支持配置导入导出、插件安装删除

## API端点

### 插件管理
- `GET /api/plugins` - 获取所有插件列表
- `GET /api/plugins/{type}/{name}/config` - 获取插件配置
- `POST /api/plugins/{type}/{name}/config` - 设置插件配置
- `POST /api/plugins/{type}/{name}/toggle` - 启用/禁用插件
- `POST /api/plugins/install` - 在线安装插件（支持热加载）
- `POST /api/plugins/delete` - 删除插件（支持热卸载）
- `POST /api/plugins/reload` - 重新加载所有插件

### 搜索
- `GET /api/search/{plugin}` - 同步搜索
- `POST /api/search/async` - 创建异步搜索任务
- `GET /api/search/task/{task_id}` - 获取搜索任务状态
- `POST /api/video-info` - 获取视频详情

### 下载
- `POST /api/download` - 创建下载任务
- `GET /api/downloads` - 获取下载列表
- `POST /api/downloads/cancel` - 取消下载

### 配置
- `GET /api/config/export` - 导出配置
- `POST /api/config/import` - 导入配置

## 插件系统

所有插件默认禁用，需要在设置中手动启用。

每个插件可以有独立的依赖文件 `{plugin_name}_requirements.txt`。

插件可以通过Web界面在线安装和删除。

**支持插件热加载/热卸载**：
- 安装插件后自动热加载，无需重启
- 删除插件后自动热卸载，无需重启
- 可手动重新加载所有插件

## 配置文件

`backend/config/plugins.json` 存储所有插件的配置，包括：
- 插件启用状态 (`_enabled`)
- 插件特定配置项

配置可以通过Web界面导出为JSON文件，也可以导入恢复。
