# UI 和配置改进说明

## 改进内容

### 1. 前端界面优化 - Placeholder 显示

**问题**: 之前预设信息直接填充到输入框中，用户无法区分哪些是默认值，哪些是已保存的配置。

**解决方案**:
- 将默认值改为 `placeholder` 显示
- 只有用户实际保存的配置才会填充到输入框
- 空输入框显示灰色提示文本（placeholder）

**修改文件**:
- `frontend/src/components/PluginConfigForm.vue`
  - `initFormData()` 方法：只有配置中有值时才填充，否则留空
  - `getPlaceholder()` 方法：使用描述或默认值作为 placeholder

**效果**:
```
之前: [http://localhost:8081        ] (直接填充)
现在: [                             ] placeholder: "默认: http://localhost:8081"
```

### 2. 前后端配置同步

**问题**: 保存配置后，前端显示可能与后端实际存储的不一致。

**解决方案**:
- 保存配置后自动重新加载配置
- 确保前端展示与后端存储完全一致
- 使用对象展开确保数据独立性

**修改文件**:
- `frontend/src/views/Settings.vue`
  - `saveConfig()` 方法：保存后重新加载配置
  - `loadPluginConfig()` 方法：使用对象展开 `{ ...config }`

**流程**:
```
用户保存配置 → 发送到后端 → 后端存储 → 重新从后端加载 → 前端更新显示
```

### 3. 下载管理持久化 (SQLite)

**问题**: 下载任务没有持久化存储，重启后丢失。

**解决方案**:
- 使用 SQLite 数据库存储下载任务
- 所有任务状态变化都写入数据库
- 支持任务的增删改查

**数据库结构**:
```sql
CREATE TABLE download_tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    status TEXT NOT NULL,
    progress REAL DEFAULT 0.0,
    plugin_name TEXT NOT NULL,
    save_path TEXT,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**修改文件**:
- `backend/database.py` - 数据库操作类（已存在，确保完整）
- `backend/plugins/download/metube_plugin.py` - 集成数据库更新
- `backend/plugins/download/qbittorrent_plugin.py` - 集成数据库更新
- `backend/main.py` - 使用数据库存储和查询任务

**数据库位置**:
- `backend/data/downloads.db`
- 自动创建，无需手动初始化

**任务状态流转**:
```
pending → downloading → completed/failed/cancelled
```

## 使用说明

### 测试数据库功能

```bash
cd backend
python test_database.py
```

### 启动服务

```bash
# 后端
cd backend
python main.py

# 前端
cd frontend
npm run dev
```

### 配置管理

1. 访问设置页面
2. 输入框为空时显示 placeholder（灰色提示）
3. 输入配置值后点击"保存配置"
4. 保存后会自动重新加载，确保显示与后端一致

### 下载管理

1. 在搜索页面添加下载任务
2. 任务自动保存到数据库
3. 在下载管理页面查看所有任务
4. 重启服务后任务依然存在

## 技术细节

### Placeholder vs Value

```vue
<!-- 有配置值 -->
<input v-model="formData.metube_url" value="http://192.168.1.100:8081" />

<!-- 无配置值 -->
<input v-model="formData.metube_url" value="" placeholder="默认: http://localhost:8081" />
```

### 数据库更新时机

```python
# 任务创建
db.add_task(task.model_dump())

# 开始下载
db.update_task(task.id, {'status': 'downloading'})

# 下载失败
db.update_task(task.id, {'status': 'failed'})

# 下载完成
db.update_task(task.id, {'status': 'completed', 'progress': 100.0})
```

### 配置同步流程

```javascript
// 保存配置
async saveConfig(type, plugin) {
  await axios.post(`/api/plugins/${type}/${plugin.name}/config`, config)
  // 重新加载确保同步
  await this.loadPluginConfig(type, plugin.name)
}
```

## 文件变更清单

### 新增文件
- `backend/data/.gitkeep` - 数据库目录占位文件
- `backend/test_database.py` - 数据库测试脚本
- `UI_CONFIG_IMPROVEMENTS.md` - 本文档

### 修改文件
- `frontend/src/components/PluginConfigForm.vue` - Placeholder 优化
- `frontend/src/views/Settings.vue` - 配置同步优化
- `backend/plugins/download/metube_plugin.py` - 数据库集成
- `backend/plugins/download/qbittorrent_plugin.py` - 数据库集成
- `backend/main.py` - 下载任务管理优化
- `.gitignore` - 忽略数据库文件

## 注意事项

1. **数据库文件**: `backend/data/downloads.db` 不会被 git 跟踪
2. **配置文件**: `backend/config/plugins.json` 不会被 git 跟踪
3. **日志文件**: `backend/logs/*.log` 不会被 git 跟踪
4. **首次运行**: 数据库会自动创建，无需手动初始化

## 测试建议

### 测试 Placeholder 功能
1. 清空所有插件配置
2. 刷新设置页面
3. 确认输入框为空，显示灰色 placeholder
4. 输入配置并保存
5. 刷新页面，确认配置值正确显示

### 测试配置同步
1. 修改配置并保存
2. 检查后端日志确认配置已保存
3. 刷新页面，确认配置正确加载
4. 重启后端服务，确认配置持久化

### 测试下载持久化
1. 添加下载任务
2. 检查数据库文件是否创建
3. 重启后端服务
4. 访问下载管理页面，确认任务仍然存在
5. 运行 `python test_database.py` 验证数据库功能
