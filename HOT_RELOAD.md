# 插件热加载功能说明

## 概述

插件热加载功能允许在不重启后端服务的情况下，动态安装、卸载和重新加载插件。这大大提高了开发和使用效率。

## 插件自动发现

系统启动时会自动扫描以下目录：
- `backend/plugins/search/` - 搜索插件
- `backend/plugins/download/` - 下载插件  
- `backend/plugins/parser/` - 解析器插件

所有符合命名规范（`*_plugin.py`）的文件都会被自动加载，**无需在代码中手动注册**。

**优势**：
- ✅ 零配置部署：复制插件文件即可
- ✅ 不会因缺少插件而报错
- ✅ 支持动态扩展
- ✅ 简化插件开发流程

## 功能特性

### 1. 热加载（Hot Load）

当安装新插件时，系统会自动：
1. 下载插件代码文件
2. 下载并安装插件依赖
3. 动态导入插件模块
4. 实例化并注册插件
5. 加载插件配置

**无需重启服务，插件立即可用！**

### 2. 热卸载（Hot Unload）

当删除插件时，系统会自动：
1. 从插件管理器中注销插件
2. 删除插件代码文件
3. 删除插件依赖文件

**无需重启服务，插件立即失效！**

### 3. 重新加载（Reload）

手动重新加载所有插件：
1. 清空当前所有插件
2. 重新扫描插件目录
3. 重新导入所有插件模块
4. 重新注册所有插件

**用于修复插件加载问题或更新插件代码后刷新**

## 技术实现

### 核心机制

使用Python的 `importlib` 模块实现动态导入：

```python
import importlib
import sys

# 动态导入模块
module = importlib.import_module(f"plugins.{plugin_type}.{plugin_name}_plugin")

# 如果模块已加载，重新加载
if module_path in sys.modules:
    importlib.reload(sys.modules[module_path])
```

### 插件发现

通过反射机制自动发现插件类：

```python
for attr_name in dir(module):
    attr = getattr(module, attr_name)
    if isinstance(attr, type) and issubclass(attr, SearchPlugin):
        plugin_class = attr
        break
```

### 插件注册

动态实例化并注册插件：

```python
plugin_instance = plugin_class()
plugin_manager.register_search_plugin(plugin_instance)
```

## API接口

### 安装插件（热加载）

```http
POST /api/plugins/install
Content-Type: application/json

{
  "url": "https://example.com/my_plugin.py",
  "plugin_type": "search"
}
```

响应：
```json
{
  "status": "success",
  "plugin_name": "my_plugin",
  "hot_loaded": true,
  "message": "插件安装成功并已加载，可以立即使用"
}
```

### 删除插件（热卸载）

```http
POST /api/plugins/delete
Content-Type: application/json

{
  "plugin_type": "search",
  "plugin_name": "my_plugin"
}
```

响应：
```json
{
  "status": "success",
  "hot_unloaded": true,
  "message": "插件删除成功并已卸载"
}
```

### 重新加载所有插件

```http
POST /api/plugins/reload
```

响应：
```json
{
  "status": "success",
  "success_count": 5,
  "fail_count": 0,
  "message": "插件重新加载完成: 成功 5, 失败 0"
}
```

## 使用场景

### 场景1：开发新插件

1. 编写插件代码
2. 上传到服务器或提供URL
3. 在Web界面安装插件
4. **立即测试，无需重启**
5. 发现问题，修改代码
6. 点击"重新加载插件"
7. **再次测试，无需重启**

### 场景2：更新现有插件

1. 修改插件代码
2. 点击"重新加载插件"
3. **更新立即生效，无需重启**

### 场景3：临时禁用插件

1. 在设置中禁用插件（不删除）
2. 插件停止工作但文件保留
3. 需要时重新启用
4. **无需重启服务**

### 场景4：清理不需要的插件

1. 点击插件的删除按钮
2. 插件立即卸载并删除文件
3. **无需重启服务**

## 注意事项

### 1. 依赖安装

插件依赖通过 `pip install` 安装，如果安装失败：
- 检查网络连接
- 检查pip配置
- 手动安装依赖：`pip install -r plugin_requirements.txt`

### 2. 模块缓存

Python会缓存已导入的模块，热加载使用 `importlib.reload()` 强制重新加载。

### 3. 插件命名规范

- 插件文件名：`{plugin_name}_plugin.py`
- 插件类名：继承自 `SearchPlugin`、`DownloadPlugin` 或 `ParserPlugin`
- 插件name属性：返回唯一标识符

### 4. 配置持久化

插件配置保存在 `backend/config/plugins.json`，热加载后会自动加载保存的配置。

### 5. 运行中的任务

热卸载插件不会影响正在运行的任务，但新任务无法使用已卸载的插件。

## 故障排除

### 问题1：热加载失败

**症状**：安装插件后提示"请重启服务"

**原因**：
- 插件代码有语法错误
- 插件类定义不符合规范
- 依赖未正确安装

**解决**：
1. 查看后端日志获取详细错误
2. 修复插件代码
3. 手动安装依赖
4. 点击"重新加载插件"

### 问题2：插件列表不更新

**症状**：安装/删除插件后列表没有变化

**原因**：前端缓存或网络延迟

**解决**：
1. 刷新页面
2. 点击"重新加载插件"
3. 检查浏览器控制台错误

### 问题3：插件功能异常

**症状**：插件加载成功但功能不正常

**原因**：
- 插件配置错误
- 插件代码逻辑问题
- 依赖版本冲突

**解决**：
1. 检查插件配置
2. 查看后端日志
3. 重新加载插件
4. 必要时重启服务

## 性能影响

热加载功能对性能的影响：

- **内存**：每个插件占用少量内存（通常<10MB）
- **CPU**：加载时有短暂CPU峰值（<1秒）
- **响应时间**：对正常请求无影响
- **并发**：不影响其他请求的处理

## 最佳实践

1. **开发阶段**：频繁使用热加载测试插件
2. **生产环境**：谨慎使用，建议在低峰期操作
3. **备份配置**：操作前导出配置备份
4. **测试验证**：热加载后测试插件功能
5. **监控日志**：关注后端日志中的错误信息

## 未来改进

计划中的功能：

- [ ] 插件版本管理
- [ ] 插件依赖检查
- [ ] 插件冲突检测
- [ ] 插件市场集成
- [ ] 自动更新插件
- [ ] 插件沙箱隔离
