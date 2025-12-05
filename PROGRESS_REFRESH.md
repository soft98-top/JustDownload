# 进度刷新功能

## 功能说明

### 1. 单任务刷新按钮
- 每个下载任务都有独立的"🔄 刷新"按钮
- 点击按钮立即查询最新进度
- 刷新时按钮显示"刷新中..."并禁用
- 只有正在下载或等待中的任务显示刷新按钮

### 2. Metube HTTP API 进度查询
- 使用 Metube 的 `/downloads` HTTP 接口
- 查询队列、已完成、失败三个列表
- 返回详细的进度信息（进度、速度、ETA）

### 3. 进度信息显示
- 进度百分比
- 下载速度（如果可用）
- 预计剩余时间 ETA（如果可用）
- 错误信息（失败任务）

## 实现细节

### 后端 - Metube 插件

```python
async def get_progress(self, metube_id: str) -> dict:
    """获取下载进度（通过 HTTP API）"""
    
    # 查询所有任务
    response = await client.get(f"{metube_url}/downloads")
    data = response.json()
    
    # 检查队列中的任务（正在下载）
    for download in data.get('queue', []):
        if download.get('id') == metube_id:
            progress = download.get('progress', 0.0) * 100
            return {
                'progress': progress,
                'status': 'downloading',
                'error': None,
                'speed': download.get('speed', ''),
                'eta': download.get('eta', '')
            }
    
    # 检查已完成的任务
    for download in data.get('done', []):
        if download.get('id') == metube_id:
            return {
                'progress': 100.0,
                'status': 'completed',
                'error': None
            }
    
    # 检查失败的任务
    for download in data.get('error', []):
        if download.get('id') == metube_id:
            return {
                'progress': 0.0,
                'status': 'failed',
                'error': download.get('error', 'Unknown error')
            }
    
    return {'progress': 0.0, 'status': 'unknown'}
```

### 后端 - API 接口

```python
@app.get("/api/downloads/{task_id}/progress")
async def get_download_progress(task_id: str):
    """获取下载进度"""
    
    # 获取任务信息
    task = db.get_task(task_id)
    
    # 获取插件
    plugin = plugin_manager.get_download_plugin(task['plugin_name'])
    
    # 获取平台任务ID
    platform_id = task['metadata'].get('metube_id')
    
    # 从插件获取最新进度
    progress_info = await plugin.get_progress(platform_id)
    
    # 更新数据库
    db.update_task(task_id, {
        'progress': progress_info['progress'],
        'status': progress_info['status']
    })
    
    return progress_info
```

### 前端 - 刷新按钮

```vue
<template>
  <button 
    v-if="task.status === 'downloading'" 
    @click="refreshProgress(task.id)"
    class="btn btn-info"
    :disabled="task.refreshing"
  >
    {{ task.refreshing ? '刷新中...' : '🔄 刷新' }}
  </button>
</template>

<script>
async refreshProgress(taskId) {
  const task = this.tasks.find(t => t.id === taskId)
  task.refreshing = true
  
  try {
    const response = await axios.get(`/api/downloads/${taskId}/progress`)
    
    // 更新任务信息
    task.progress = response.data.progress
    task.status = response.data.status
    task.speed = response.data.speed
    task.eta = response.data.eta
    task.error = response.data.error
    
    this.$toast.success('进度已更新', `${task.progress.toFixed(1)}%`)
  } finally {
    task.refreshing = false
  }
}
</script>
```

### 前端 - 进度显示

```vue
<div class="progress-bar">
  <div class="progress-fill" :style="{ width: task.progress + '%' }"></div>
  <span class="progress-text">
    {{ task.progress.toFixed(1) }}%
    <span v-if="task.speed" class="progress-extra"> · {{ task.speed }}</span>
    <span v-if="task.eta" class="progress-extra"> · ETA: {{ task.eta }}</span>
  </span>
</div>

<div v-if="task.status === 'failed' && task.error" class="error-message">
  错误: {{ task.error }}
</div>
```

## Metube API 说明

### 获取所有任务

```http
GET http://localhost:8081/downloads
```

**响应格式**:
```json
{
  "queue": [
    {
      "id": "abc123",
      "title": "视频标题",
      "url": "https://...",
      "status": "downloading",
      "progress": 0.45,
      "speed": "2.5 MB/s",
      "eta": "00:05:30"
    }
  ],
  "done": [
    {
      "id": "def456",
      "title": "已完成的视频",
      "url": "https://...",
      "status": "finished"
    }
  ],
  "error": [
    {
      "id": "ghi789",
      "title": "失败的视频",
      "url": "https://...",
      "error": "Video unavailable"
    }
  ]
}
```

### 进度值说明

- Metube 返回的 `progress` 是 0-1 的小数（例如 0.45 表示 45%）
- 我们的系统统一使用 0-100 的百分比
- 转换公式：`progress_percent = progress * 100`

## 使用流程

### 1. 查看任务进度

```
用户打开下载管理页面
  → 看到任务列表
  → 每个正在下载的任务显示进度条
  → 进度条显示百分比、速度、ETA
```

### 2. 手动刷新进度

```
用户点击"🔄 刷新"按钮
  → 按钮变为"刷新中..."并禁用
  → 调用 GET /api/downloads/{id}/progress
  → 后端查询 Metube API
  → 返回最新进度信息
  → 前端更新显示
  → 显示 Toast 提示
  → 按钮恢复可用
```

### 3. 自动刷新

```
页面加载后启动定时器
  → 每10秒刷新任务列表
  → 只刷新任务状态，不查询详细进度
  → 避免频繁请求 Metube API
  → 用户可以手动点击刷新获取最新进度
```

## 测试

### 测试脚本

```bash
# 测试 Metube 进度查询
python backend/test_metube_progress.py
```

**预期输出**:
```
============================================================
测试 Metube 进度查询
============================================================

1. 测试获取所有任务...

队列中的任务 (queue): 2
  - ID: abc123
    标题: 测试视频
    进度: 45.5%
    状态: downloading

已完成的任务 (done): 5
  - ID: def456
    标题: 已完成的视频

失败的任务 (error): 0

2. 测试查询特定任务进度: abc123
  进度: 45.5%
  状态: downloading
  速度: 2.5 MB/s
  ETA: 00:05:30
  错误: None

============================================================
✓ 测试完成
============================================================
```

### 手动测试

1. **启动 Metube**:
   ```bash
   docker run -d -p 8081:8081 -v /downloads:/downloads ghcr.io/alexta69/metube
   ```

2. **添加下载任务**:
   - 在前端点击"新增下载"
   - 输入 YouTube 链接
   - 开始下载

3. **测试刷新按钮**:
   - 找到正在下载的任务
   - 点击"🔄 刷新"按钮
   - 观察进度更新
   - 检查速度和 ETA 显示

4. **测试错误显示**:
   - 添加一个无效链接
   - 等待失败
   - 点击刷新
   - 查看错误信息显示

## 性能优化

### 1. 按需刷新
- 不自动刷新每个任务的详细进度
- 用户点击刷新按钮才查询
- 减少 API 请求次数

### 2. 状态缓存
- 已完成/失败的任务不再查询进度
- 直接返回数据库中的状态
- 避免无效请求

### 3. 请求防抖
- 刷新时禁用按钮
- 防止重复点击
- 避免并发请求

### 4. 超时控制
- HTTP 请求设置 10 秒超时
- 避免长时间等待
- 快速失败并提示用户

## 错误处理

### 1. Metube 服务不可用

```python
try:
    response = await client.get(f"{metube_url}/downloads")
except httpx.ConnectError:
    logger.error("Metube 服务不可用")
    return {'progress': 0.0, 'status': 'unknown', 'error': 'Service unavailable'}
```

### 2. 任务不存在

```python
# 任务不在任何列表中
if not found:
    return {
        'progress': 0.0,
        'status': 'unknown',
        'error': 'Task not found in Metube'
    }
```

### 3. 前端错误处理

```javascript
try {
  await axios.get(`/api/downloads/${taskId}/progress`)
} catch (error) {
  this.$toast.error('刷新失败', error.response?.data?.detail)
}
```

## 界面优化

### 1. 按钮样式

```css
.btn-info {
  background: #3498db;
  color: white;
}

.btn-info:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}
```

### 2. 进度条增强

```css
.progress-text {
  white-space: nowrap;
}

.progress-extra {
  font-weight: normal;
  font-size: 0.8rem;
}
```

### 3. 错误提示

```css
.error-message {
  background: #fee;
  border-left: 3px solid #e74c3c;
  color: #c0392b;
}
```

## 后续改进

### 可选功能

1. **WebSocket 实时推送**（未来）:
   - 建立 WebSocket 连接到 Metube
   - 实时接收进度更新
   - 无需手动刷新

2. **批量刷新**:
   - 一键刷新所有正在下载的任务
   - 并发查询提高效率

3. **进度图表**:
   - 显示下载速度曲线
   - 历史进度记录

4. **通知提醒**:
   - 下载完成后桌面通知
   - 浏览器通知 API

## 文件变更

### 修改文件
- `backend/plugins/download/metube_plugin.py` - 优化进度查询
- `backend/main.py` - 更新进度接口
- `frontend/src/views/Downloads.vue` - 添加刷新按钮和显示

### 新增文件
- `backend/test_metube_progress.py` - 进度查询测试
- `PROGRESS_REFRESH.md` - 本文档

## 总结

✅ **完整的进度刷新功能**:
- 单任务刷新按钮
- HTTP API 进度查询
- 详细信息显示（进度、速度、ETA）
- 错误信息展示
- 性能优化和错误处理

用户可以随时点击刷新按钮获取最新进度，无需等待自动刷新！
