# 插件开发指南

## 插件类型

### 1. 搜索插件 (Search Plugin)

位置: `backend/plugins/search/`

搜索插件用于从各个平台搜索视频内容。

**模板**: `plugin_template.py`

**必需方法**:
- `name`: 插件唯一标识
- `version`: 版本号
- `description`: 插件描述
- `get_config_schema()`: 返回配置项定义
- `search(keyword)`: 搜索方法
- `get_video_info(url)`: 获取视频详情

**依赖文件**: `{plugin_name}_requirements.txt`

### 2. 下载插件 (Download Plugin)

位置: `backend/plugins/download/`

下载插件用于处理不同协议的下载任务。

**必需方法**:
- `name`: 插件唯一标识
- `version`: 版本号
- `description`: 插件描述
- `supported_protocols`: 支持的协议列表
- `get_config_schema()`: 返回配置项定义
- `download(task)`: 下载方法
- `get_downloads()`: 获取下载列表
- `cancel(download_id)`: 取消下载

**依赖文件**: `{plugin_name}_requirements.txt`

### 3. 解析器插件 (Parser Plugin)

位置: `backend/plugins/parser/`

解析器插件用于解析视频播放地址。

**必需方法**:
- `name`: 插件唯一标识
- `version`: 版本号
- `description`: 插件描述
- `get_config_schema()`: 返回配置项定义
- `parse_url(url)`: 解析URL方法

**依赖文件**: `{plugin_name}_requirements.txt`

## 创建新插件

### 步骤1: 复制模板

```bash
cp backend/plugins/search/plugin_template.py backend/plugins/search/my_plugin.py
```

### 步骤2: 修改插件代码

修改 `name`, `version`, `description` 等属性，实现必需的方法。

### 步骤3: 创建依赖文件

创建 `my_requirements.txt` 文件，列出插件特定的依赖：

```
requests>=2.28.0
beautifulsoup4>=4.11.0
```

### 步骤4: 放置插件文件

将插件文件放入对应目录：
- 搜索插件：`backend/plugins/search/`
- 下载插件：`backend/plugins/download/`
- 解析器插件：`backend/plugins/parser/`

### 步骤5: 重启服务或热加载

**方式1：重启服务**
```bash
# 重启后端服务
python main.py
```

**方式2：热加载（推荐）**
- 在Web界面点击"重新加载插件"按钮
- 或调用API：`POST /api/plugins/reload`

插件会被自动发现并加载，无需手动注册！

## 插件自动发现

系统启动时会自动扫描插件目录，加载所有符合命名规范的插件文件：

**命名规范**：`{plugin_name}_plugin.py`

**示例**：
- `jable_plugin.py` → 插件名: `jable`
- `metube_plugin.py` → 插件名: `metube`
- `my_custom_plugin.py` → 插件名: `my_custom`

**注意**：
- 模板文件（`plugin_template*.py`）会被自动跳过
- 插件类必须继承自对应的基类
- 插件的 `name` 属性应与文件名一致

## 在线安装插件

用户可以通过Web界面在线安装插件：

1. 在设置页面点击"安装插件"
2. 输入插件文件的URL
3. 系统自动下载并安装依赖
4. **插件自动热加载，立即可用**

## 配置项类型

插件可以定义以下类型的配置项：

- `text`: 文本输入
- `password`: 密码输入（隐藏显示）
- `number`: 数字输入
- `boolean`: 开关

示例：

```python
ConfigField(
    name="api_key",
    label="API密钥",
    type="password",
    required=True,
    description="平台API密钥"
)
```

## 最佳实践

1. **错误处理**: 使用try-except捕获异常
2. **日志记录**: 使用logger记录关键信息
3. **配置验证**: 检查必需配置是否存在
4. **超时设置**: 为网络请求设置合理的超时时间
5. **代理支持**: 考虑添加代理配置选项
6. **依赖隔离**: 将插件特定依赖放在独立的requirements文件中

## 示例插件

参考现有插件：
- `jable_plugin.py` - 复杂的搜索插件示例
- `seacms_plugin.py` - SeaCMS搜索插件
- `metube_plugin.py` - 下载插件示例
- `m3u8_parser_plugin.py` - 解析器插件示例
