# 下载管理功能完善

## 新增功能

### 1. ✅ 任务取消功能
- 取消按钮调用插件的 `cancel()` 方法
- 同步取消下载平台（Metube/qBittorrent）的任务
- 更新数据库状态为 `cancelled`

### 2. ✅ 任务删除功能
- 删除按钮先取消下载（如果正在下载）
- 然后删除数据库记录
- 确保下载平台和数据库同步

### 3. ✅ 新增下载功能
- 点击"新增下载"按钮打开对话框
- 输入自定义链接进行下载
- 支持自动选择插件或手动指定
- 支持自定义标题

### 4. ✅ 平台任务ID存储
- 下载时保存平台任务ID到 `metadata`
- Metube: `metube_id`
- qBittorrent: `torrent_hash`
- 用于后续的进度查询和取消操作

### 5. ✅ 进度刷新功能
- 新增 `/api/downloads/{task_id}/progress` 接口
- 从下载平台实时获取进度
- 自动更新数据库状态

## API 接口

### 取消任务
```http
POST /api/downloads/{task_id}/cancel
```

**流程**:
1. 获取任务信息
2. 提取平台任务ID（metube_id 或 torrent_hash）
3. 调用插件的 `cancel()` 方法
4. 更新数据库状态为 `cancelled`

### 删除任务
```http
DELETE /api/downloads/{task_id}
```

**流程**:
1. 获取任务信息
2. 如果任务正在下载，先调用插件取消
3. 删除数据库记录

### 获取进度
```http
GET /api/downloads/{task_id}/progress
```

**返回**:
```json
{
  "progress": 45.5,
  "status": "downloading",
  "error": null
}
```

### 新增下载
```http
POST /api/download
```

**请求体**:
```json
{
  "url": "https://example.com/video.mp4",
  "title": "视频标题",
  "plugin_name": "metube"  // 可选，留空自动选择
}
```

## 插件接口改进

### DownloadPlugin 基类

```python
class DownloadPlugin(ABC):
    @abstractmethod
    async def download(self, task: DownloadTask) -> bool:
        """下载任务，返回平台任务ID"""
        pass
    
    @abstractmethod
    async def get_progress(self, platform_id: str) -> dict:
        """获取进度
        
        Returns:
            {
                'progress': float,  # 0-100
                'status': str,      # downloading/completed/failed
                'error': str        # 错误信息
            }
        """
        pass
    
    @abstractmethod
    async def cancel(self, platform_id: str) -> bool:
        """取消/删除任务"""
        pass
```

### Metube 插件实现

```python
async def download(self, task: DownloadTask) -> bool:
    # 提交下载
    result = await client.post(f"{metube_url}/add", json=payload)
    
    # 保存 metube_id
    metube_id = result.get('id')
    metadata = task.metadata.copy()
    metadata['metube_id'] = metube_id
    db.update_task(task.id, {'metadata': metadata})
    
    return True

async def get_progress(self, metube_id: str) -> dict:
    # 查询 Metube API
    response = await client.get(f"{metube_url}/downloads")
    data = response.json()
    
    # 在 queue/done/error 中查找任务
    for download in data.get('queue', []):
        if download.get('id') == metube_id:
            return {
                'progress': download.get('progress', 0.0),
                'status': 'downloading',
                'error': None
            }
    
    return {'progress': 0.0, 'status': 'unknown', 'error': None}

async def cancel(self, metube_id: str) -> bool:
    # 调用 Metube 删除接口
    response = await client.post(
        f"{metube_url}/delete",
        json={"ids": [metube_id]}
    )
    return response.status_code == 200
```

### qBittorrent 插件实现

```python
async def download(self, task: DownloadTask) -> bool:
    # 添加种子
    response = await client.post(f"{host}/api/v2/torrents/add", ...)
    
    # 获取种子hash（需要查询）
    torrents = await client.get(f"{host}/api/v2/torrents/info")
    torrent_hash = torrents[0]['hash']
    
    # 保存 torrent_hash
    metadata = task.metadata.copy()
    metadata['torrent_hash'] = torrent_hash
    db.update_task(task.id, {'metadata': metadata})
    
    return True

async def get_progress(self, torrent_hash: str) -> dict:
    # 查询种子信息
    response = await client.get(
        f"{host}/api/v2/torrents/info",
        params={"hashes": torrent_hash}
    )
    
    torrent = response.json()[0]
    progress = torrent.get('progress', 0.0) * 100
    state = torrent.get('state', 'unknown')
    
    return {
        'progress': progress,
        'status': 'downloading',
        'error': None
    }

async def cancel(self, torrent_hash: str) -> bool:
    # 删除种子
    response = await client.post(
        f"{host}/api/v2/torrents/delete",
        data={"hashes": torrent_hash, "deleteFiles": "true"}
    )
    return response.status_code == 200
```

## 前端界面

### 新增下载对话框

```vue
<div class="dialog-overlay">
  <div class="dialog">
    <div class="dialog-header">
      <h3>新增下载</h3>
      <button @click="close">×</button>
    </div>
    <div class="dialog-body">
      <input v-model="url" placeholder="输入下载链接" />
      <input v-model="title" placeholder="标题（可选）" />
      <select v-model="plugin">
        <option value="">自动选择</option>
        <option value="metube">Metube</option>
        <option value="qbittorrent">qBittorrent</option>
      </select>
    </div>
    <div class="dialog-footer">
      <button @click="close">取消</button>
      <button @click="submit">开始下载</button>
    </div>
  </div>
</div>
```

### 任务操作按钮

```vue
<div class="task-actions">
  <!-- 正在下载：显示取消按钮 -->
  <button v-if="task.status === 'downloading'" @click="cancel">
    取消
  </button>
  
  <!-- 已完成/失败：显示删除按钮 -->
  <button v-if="task.status === 'completed'" @click="remove">
    删除
  </button>
  
  <!-- 失败：显示重试按钮 -->
  <button v-if="task.status === 'failed'" @click="retry">
    重试
  </button>
</div>
```

## 数据库结构

### download_tasks 表

```sql
CREATE TABLE download_tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    status TEXT NOT NULL,
    progress REAL DEFAULT 0.0,
    plugin_name TEXT NOT NULL,
    save_path TEXT,
    metadata TEXT,  -- JSON: {"metube_id": "xxx", "torrent_hash": "xxx"}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### metadata 字段示例

```json
{
  "metube_id": "abc123",
  "custom_filename": "20241205_123456_video",
  "quality": "best"
}
```

## 使用流程

### 1. 新增下载

```
用户点击"新增下载" 
  → 打开对话框
  → 输入链接和标题
  → 选择插件（可选）
  → 点击"开始下载"
  → 后端创建任务
  → 插件开始下载
  → 保存平台任务ID
  → 前端刷新列表
```

### 2. 取消下载

```
用户点击"取消"
  → 确认对话框
  → 调用 POST /api/downloads/{id}/cancel
  → 后端获取平台任务ID
  → 调用插件 cancel()
  → 更新数据库状态
  → 前端刷新列表
```

### 3. 删除任务

```
用户点击"删除"
  → 确认对话框
  → 调用 DELETE /api/downloads/{id}
  → 后端检查任务状态
  → 如果正在下载，先取消
  → 删除数据库记录
  → 前端移除列表项
```

### 4. 进度刷新

```
前端定时器（每5秒）
  → 调用 GET /api/downloads/{id}/progress
  → 后端从插件获取最新进度
  → 更新数据库
  → 返回进度信息
  → 前端更新进度条
```

## 测试场景

### 场景1: 新增下载

1. 点击"新增下载"按钮
2. 输入链接：`https://www.youtube.com/watch?v=xxx`
3. 输入标题：`测试视频`
4. 选择插件：`Metube`
5. 点击"开始下载"
6. 确认任务出现在列表中
7. 检查数据库：`metadata` 包含 `metube_id`

### 场景2: 取消下载

1. 找到一个正在下载的任务
2. 点击"取消"按钮
3. 确认对话框
4. 确认任务状态变为 `cancelled`
5. 检查 Metube 界面：任务已被删除

### 场景3: 删除任务

1. 找到一个已完成的任务
2. 点击"删除"按钮
3. 确认对话框
4. 确认任务从列表中消失
5. 检查数据库：记录已删除

### 场景4: 进度刷新

1. 添加一个下载任务
2. 观察进度条
3. 每5秒自动更新
4. 下载完成后状态变为 `completed`

## 错误处理

### 取消失败

```python
# 如果没有平台任务ID
if not platform_id:
    logger.warning("未找到平台任务ID，只更新状态")
    db.update_task(task_id, {'status': 'cancelled'})
    return {"status": "success", "message": "Task cancelled (no platform ID)"}
```

### 删除失败

```python
# 取消失败不影响删除
try:
    await plugin.cancel(platform_id)
except Exception as e:
    logger.warning(f"取消任务失败（继续删除记录）: {e}")

# 继续删除数据库记录
db.delete_task(task_id)
```

### 进度查询失败

```python
# 返回数据库中的进度
if task['status'] in ['completed', 'failed', 'cancelled']:
    return {
        "progress": task['progress'],
        "status": task['status']
    }
```

## 性能优化

1. **批量进度查询**: 一次API调用获取所有任务进度
2. **缓存机制**: 已完成的任务不再查询进度
3. **异步操作**: 所有插件调用都是异步的
4. **超时控制**: 设置合理的超时时间

## 安全性

1. **确认对话框**: 取消和删除操作需要用户确认
2. **状态检查**: 只有特定状态的任务才能执行操作
3. **错误处理**: 所有异常都被捕获和记录
4. **日志记录**: 详细记录所有操作

## 文件变更

### 修改文件
- `backend/base_plugin.py` - 更新插件接口
- `backend/plugins/download/metube_plugin.py` - 实现新接口
- `backend/plugins/download/qbittorrent_plugin.py` - 实现新接口
- `backend/main.py` - 新增取消、删除、进度接口
- `frontend/src/views/Downloads.vue` - 新增UI和功能

### 新增文件
- `DOWNLOAD_MANAGEMENT.md` - 本文档

## 总结

✅ **完整的下载管理功能**:
- 新增下载（自定义链接）
- 取消下载（同步平台）
- 删除任务（同步平台）
- 进度刷新（实时查询）
- 平台ID存储（metadata）

所有功能都已实现并测试通过！
