# 测试改进功能

## 快速测试

### 1. 测试数据库功能

```bash
python backend/test_database.py
```

预期输出：
```
✓ 任务创建成功
✓ 任务获取成功
✓ 任务更新成功
✓ 所有测试通过！
```

### 2. 启动服务

```bash
# 方式1: 使用启动脚本（推荐）
./start_all.sh

# 方式2: 手动启动
# 终端1 - 后端
cd backend
python main.py

# 终端2 - 前端
cd frontend
npm run dev
```

### 3. 测试 Placeholder 功能

1. 打开浏览器访问 http://localhost:5173
2. 进入"设置"页面
3. 观察输入框：
   - 如果是新安装，输入框应该是空的
   - 鼠标悬停或点击输入框，应该看到灰色的 placeholder 提示
   - 例如：`默认: http://localhost:8081`

4. 输入一些配置值（例如修改 Metube 地址）
5. 点击"保存配置"
6. 刷新页面，确认配置值正确显示（不是 placeholder）

### 4. 测试配置同步

1. 在设置页面修改配置
2. 保存配置
3. 打开浏览器开发者工具（F12）
4. 查看 Network 标签，应该看到：
   - POST `/api/plugins/download/metube/config` - 保存配置
   - GET `/api/plugins/download/metube/config` - 重新加载配置
5. 刷新页面，确认配置正确显示

### 5. 测试下载持久化

#### 5.1 添加下载任务

1. 进入"搜索"页面
2. 搜索一些内容（例如使用 SeaCMS 插件）
3. 点击某个结果的"下载"按钮
4. 进入"下载管理"页面
5. 确认任务出现在列表中

#### 5.2 验证持久化

```bash
# 检查数据库文件是否创建
ls -lh backend/data/downloads.db

# 查看数据库内容（需要安装 sqlite3）
sqlite3 backend/data/downloads.db "SELECT id, title, status FROM download_tasks;"
```

#### 5.3 重启测试

1. 停止后端服务（Ctrl+C）
2. 重新启动后端：`python backend/main.py`
3. 刷新前端页面
4. 进入"下载管理"页面
5. 确认之前的任务仍然存在

## 详细测试场景

### 场景1: 首次使用

**步骤**:
1. 清空配置：`rm backend/config/plugins.json`
2. 清空数据库：`rm backend/data/downloads.db`
3. 启动服务
4. 访问设置页面

**预期**:
- 所有输入框为空
- 显示 placeholder 提示
- 布尔值开关显示默认状态

### 场景2: 配置修改

**步骤**:
1. 修改 Metube URL 为 `http://192.168.1.100:8081`
2. 点击"保存配置"
3. 观察 Toast 提示："配置已保存"
4. 刷新页面

**预期**:
- 输入框显示 `http://192.168.1.100:8081`（不是 placeholder）
- 后端日志显示配置已保存
- 配置文件 `backend/config/plugins.json` 包含新配置

### 场景3: 下载任务生命周期

**步骤**:
1. 添加下载任务
2. 检查数据库：任务状态为 `pending`
3. 插件开始下载：任务状态变为 `downloading`
4. 下载完成：任务状态变为 `completed`
5. 删除任务：从数据库中移除

**预期**:
- 每个状态变化都持久化到数据库
- 前端实时显示状态变化
- 重启后任务状态保持

### 场景4: 错误处理

**步骤**:
1. 配置错误的 Metube URL（例如 `http://localhost:9999`）
2. 尝试下载任务

**预期**:
- 任务状态变为 `failed`
- 后端日志显示详细错误信息
- 前端显示错误提示
- 任务保存在数据库中，可以重试

## 验证清单

- [ ] 数据库测试通过
- [ ] Placeholder 正确显示
- [ ] 配置保存后自动重新加载
- [ ] 下载任务保存到数据库
- [ ] 重启后任务仍然存在
- [ ] 任务状态正确更新
- [ ] 错误处理正确
- [ ] 日志输出清晰

## 常见问题

### Q: 数据库文件在哪里？
A: `backend/data/downloads.db`，首次创建任务时自动生成。

### Q: 如何清空所有数据？
A: 删除 `backend/data/downloads.db` 和 `backend/config/plugins.json`。

### Q: Placeholder 不显示？
A: 确保配置为空，刷新页面，检查浏览器控制台是否有错误。

### Q: 配置保存后不生效？
A: 检查后端日志，确认配置已保存，刷新页面重新加载。

### Q: 任务重启后丢失？
A: 检查数据库文件是否存在，查看后端日志是否有数据库错误。

## 性能测试

### 大量任务测试

```python
# 创建测试脚本
import requests
import time

for i in range(100):
    response = requests.post('http://localhost:8000/api/download', json={
        'url': f'https://example.com/video{i}.mp4',
        'title': f'测试视频 {i}',
        'plugin_name': 'metube'
    })
    print(f'任务 {i}: {response.status_code}')
    time.sleep(0.1)
```

**预期**:
- 所有任务成功创建
- 数据库查询速度正常
- 前端列表正常显示

## 日志检查

### 后端日志

```bash
tail -f backend/logs/app_*.log
```

关键日志：
- `任务已添加: xxx` - 任务创建
- `任务已更新: xxx` - 状态更新
- `数据库初始化成功` - 数据库就绪

### 前端日志

打开浏览器控制台（F12），查看：
- Network 请求
- Console 错误
- Vue DevTools 状态

## 总结

所有改进都已实现并测试通过：
1. ✅ Placeholder 显示预设信息
2. ✅ 前后端配置同步
3. ✅ 下载管理持久化（SQLite）

建议按照上述测试场景逐一验证功能。
