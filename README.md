# 模块化下载系统

一个基于插件架构的 Web 下载系统，支持自定义搜索和下载插件。

## 功能特性

- 🔌 **插件化架构**：搜索插件和下载插件完全独立
- 🔍 **多源搜索**：支持 YouTube 等多个视频平台搜索
- ⬇️ **多协议下载**：支持 HTTP/HTTPS、m3u8、磁力链接等
- ⚙️ **灵活配置**：每个插件都有独立的配置选项
- 🌐 **Web 界面**：现代化的 Vue 3 前端界面

## 项目结构

```
├── backend/                 # 后端服务
│   ├── plugins/            # 插件目录
│   │   ├── search/         # 搜索插件
│   │   │   └── youtube_plugin.py
│   │   └── download/       # 下载插件
│   │       ├── metube_plugin.py
│   │       └── qbittorrent_plugin.py
│   ├── base_plugin.py      # 插件基类
│   ├── models.py           # 数据模型
│   ├── plugin_manager.py   # 插件管理器
│   ├── main.py             # FastAPI 应用
│   └── requirements.txt
└── frontend/               # 前端应用
    ├── src/
    │   ├── views/          # 页面组件
    │   │   ├── Search.vue
    │   │   ├── Downloads.vue
    │   │   └── Settings.vue
    │   ├── App.vue
    │   └── main.js
    ├── index.html
    ├── package.json
    └── vite.config.js
```

## 快速开始

### 后端启动

```bash
cd backend
pip install -r requirements.txt

# 普通模式
python main.py

# 详细日志模式（推荐调试时使用）
python main.py --verbose

# 指定日志级别
python main.py --log-level DEBUG
```

后端将在 http://localhost:8000 启动

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端将在 http://localhost:3000 启动

### 日志系统

系统支持详细的日志记录，便于调试和问题排查：

- **日志级别**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **彩色输出**: 不同级别使用不同颜色
- **文件记录**: 自动保存到 `logs/` 目录
- **详细模式**: 显示函数名和行号

详见 [日志使用指南](LOGGING_GUIDE.md)

## 已实现的插件

### 搜索插件

- **YouTube**: 使用 YouTube Data API v3 搜索视频
- **SeaCMS**: 海洋CMS资源采集插件，支持多资源站并发搜索，自动过滤m3u8资源

### 下载插件

- **Metube**: 支持 YouTube、m3u8 等格式下载
- **qBittorrent**: 支持 BT 种子和磁力链接下载

## 如何开发新插件

### 创建搜索插件

```python
from base_plugin import SearchPlugin
from models import ConfigField, SearchResult

class MySearchPlugin(SearchPlugin):
    @property
    def name(self) -> str:
        return "my_plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "我的搜索插件"
    
    def get_config_schema(self) -> List[ConfigField]:
        return [
            ConfigField(
                name="api_key",
                label="API 密钥",
                type="password",
                required=True
            )
        ]
    
    async def search(self, keyword: str, **kwargs) -> List[SearchResult]:
        # 实现搜索逻辑
        pass
    
    async def get_video_info(self, url: str) -> SearchResult:
        # 实现获取视频信息逻辑
        pass
```

### 创建下载插件

```python
from base_plugin import DownloadPlugin
from models import ConfigField, DownloadTask

class MyDownloadPlugin(DownloadPlugin):
    @property
    def name(self) -> str:
        return "my_downloader"
    
    @property
    def supported_protocols(self) -> List[str]:
        return ["http", "https"]
    
    # 实现其他必需方法...
```

## API 文档

启动后端后访问 http://localhost:8000/docs 查看完整的 API 文档。

## 配置说明

在 Web 界面的"设置"页面可以配置各个插件的参数，例如：

- YouTube API 密钥
- Metube 服务地址
- qBittorrent 连接信息
- 代理设置
- 下载路径

## 技术栈

- **后端**: FastAPI + Python 3.8+
- **前端**: Vue 3 + Vite
- **HTTP 客户端**: httpx (异步)
