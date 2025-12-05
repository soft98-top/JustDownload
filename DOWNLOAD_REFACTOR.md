# 下载管理重构说明

## 概述

将下载管理从独立存储模式改为直接查询下载插件的模式，实现了更清晰的架构和实时数据同步。

## 架构变化

### 之前的架构
- 下载管理维护独立的数据库表
- 数据存在冗余和同步问题
- 需要手动更新进度

### 新的架构
- 下载管理直接查询各下载插件的API
- 数据源单一，实时同步
- 无需维护本地数据库

## API 变化

### 1. 查询下载记录

**新接口：**
```
GET /api/downloads?platform={platform}
```

**参数：**
- `platform`: 平台名称
  - `all` - 返回所有平台的记录（聚合）
  - `metube` - 只返回 MeTube 的记录
  - `qbittorrent` - 只返回 qBittorrent 的记录

**返回格式（单平台）：**
```json
{
  "platform": "metube",
  "web_ui_url": "http://localhost:8081",
  "downloads": [
    {
      "id": "xxx",
      "platform": "metube",
      "title": "视频标题",
      "url": "https://...",
      "status": "downloading",
      "progress": 75.5,
      "speed": "2.5 MB/s",
      "eta": "5m",
      "created_at": null
    }
  ]
}
```

**返回格式（聚合）：**
```json
{
  "platform": "all",
  "platforms": [
    {
      "name": "metube",
      "web_ui_url": "http://localhost:8081",
      "downloads": [...]
    },
    {
      "name": "qbittorrent",
      "web_ui_url": "http://localhost:8080",
      "downloads": [...]
    }
  ],
  "total": 10
}
```

### 2. 取消下载

**新接口：**
```
POST /api/downloads/cancel
```

**请求体：**
```json
{
  "platform": "metube",
  "download_id": "xxx"
}
```

**说明：**
- 必须指定平台名称，确保操作精准
- download_id 是该平台的任务ID

### 3. 移除的接口

以下接口已移除（不再需要）：
- `DELETE /api/downloads/{task_id}` - 删除任务
- `PUT /api/downloads/{task_id}` - 更新任务
- `POST /api/downloads/{task_id}/cancel` - 取消任务（旧版）
- `GET /api/downloads/{task_id}/progress` - 获取进度

## 插件接口变化

### 新增方法

所有下载插件需要实现以下新方法：

#### 1. get_downloads()
```python
async def get_downloads(self) -> List[Dict[str, Any]]:
    """获取该平台的所有下载记录
    
    Returns:
        List[Dict]: 下载记录列表，每条记录包含:
            - id: 平台任务ID
            - platform: 平台名称
            - title: 标题
            - url: 下载链接
            - status: 状态 (pending/downloading/completed/failed/paused)
            - progress: 进度 (0-100)
            - speed: 下载速度（可选）
            - eta: 预计剩余时间（可选）
            - created_at: 创建时间（可选）
    """
```

#### 2. get_web_ui_url()
```python
def get_web_ui_url(self) -> str:
    """获取该平台的 Web UI 地址
    
    Returns:
        str: Web UI 地址，如 "http://localhost:8081"
    """
```

### 实现示例

#### MeTube 插件
```python
async def get_downloads(self) -> list:
    metube_url = self.config.get('metube_url', 'http://localhost:8081').rstrip('/')
    downloads = []
    
    async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
        response = await client.get(f"{metube_url}/history")
        
        if response.status_code == 200:
            data = response.json()
            
            # 处理队列中的任务
            for download in data.get('queue', []):
                downloads.append({
                    'id': download.get('id', download.get('url')),
                    'platform': self.name,
                    'title': download.get('title', '未知标题'),
                    'url': download.get('url', ''),
                    'status': self._map_status(download.get('status', 'downloading')),
                    'progress': download.get('percent') or 0.0,
                    'speed': download.get('speed', ''),
                    'eta': download.get('eta', ''),
                    'created_at': None
                })
            
            # 处理已完成的任务
            for download in data.get('done', []):
                downloads.append({
                    'id': download.get('id', download.get('url')),
                    'platform': self.name,
                    'title': download.get('title', '未知标题'),
                    'url': download.get('url', ''),
                    'status': 'completed',
                    'progress': 100.0,
                    'speed': '',
                    'eta': '',
                    'created_at': None
                })
    
    return downloads

def get_web_ui_url(self) -> str:
    return self.config.get('metube_url', 'http://localhost:8081').rstrip('/')
```

#### qBittorrent 插件
```python
async def get_downloads(self) -> list:
    host = self.config.get('host', 'http://localhost:8080')
    downloads = []
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 登录
        await client.post(f"{host}/api/v2/auth/login", data={
            "username": self.config.get('username', 'admin'),
            "password": self.config.get('password', '')
        })
        
        # 获取所有种子
        response = await client.get(f"{host}/api/v2/torrents/info")
        
        if response.status_code == 200:
            torrents = response.json()
            
            for torrent in torrents:
                downloads.append({
                    'id': torrent.get('hash'),
                    'platform': self.name,
                    'title': torrent.get('name', '未知标题'),
                    'url': torrent.get('magnet_uri', ''),
                    'status': self._map_status(torrent.get('state', 'unknown')),
                    'progress': torrent.get('progress', 0.0) * 100,
                    'speed': self._format_speed(torrent.get('dlspeed', 0)),
                    'eta': self._format_eta(torrent.get('eta', 0)),
                    'created_at': torrent.get('added_on')
                })
    
    return downloads

def get_web_ui_url(self) -> str:
    return self.config.get('host', 'http://localhost:8080')
```

## 前端变化

### 新增功能

1. **平台选择器**
   - 下拉菜单选择查看的平台（全部/MeTube/qBittorrent）
   - 切换平台时自动刷新数据

2. **按平台分组显示**
   - 每个平台显示为独立的卡片组
   - 显示平台名称和"打开平台"链接

3. **跳转到平台**
   - 每个平台组显示"🔗 打开平台"按钮
   - 点击在新标签页打开对应平台的 Web UI

### 移除功能

- 删除任务按钮（不再需要本地删除）
- 刷新单个任务进度按钮（自动刷新）
- 重试按钮（直接在平台操作）

### 保留功能

- 新增下载（仍然通过后端API创建）
- 取消下载（调用新的取消接口）
- 自动刷新（每10秒）

## 数据库变化

### 保留的功能
- 创建下载任务时仍然会在数据库中创建记录
- 用于跟踪任务的初始信息和元数据

### 移除的功能
- 不再从数据库查询下载列表
- 不再更新任务进度到数据库
- 下载管理页面完全从插件获取数据

## 优势

1. **数据一致性** - 数据源单一，避免同步问题
2. **实时性** - 直接从下载平台获取最新状态
3. **架构清晰** - 下载管理只是聚合视图层
4. **易于扩展** - 新增下载插件只需实现标准接口
5. **减少维护** - 无需维护本地数据库的同步逻辑

## 使用说明

### 查看下载记录

1. 打开下载管理页面
2. 选择要查看的平台（或选择"全部平台"）
3. 系统会实时从对应平台获取下载记录

### 取消下载

1. 在下载列表中找到要取消的任务
2. 点击"取消"按钮
3. 系统会调用对应平台的API取消任务

### 详细操作

1. 点击平台组的"🔗 打开平台"按钮
2. 在平台的 Web UI 中进行详细操作
3. 返回下载管理页面查看更新后的状态

## 注意事项

1. **配置要求** - 确保下载插件已正确配置（URL、认证等）
2. **网络连接** - 需要能够访问下载平台的API
3. **权限** - qBittorrent 需要正确的用户名和密码
4. **刷新频率** - 默认每10秒自动刷新，可根据需要调整

## 测试建议

1. 测试单平台查询（MeTube、qBittorrent）
2. 测试聚合查询（全部平台）
3. 测试取消操作（确保平台参数正确）
4. 测试跳转到平台功能
5. 测试错误处理（平台不可用时）
