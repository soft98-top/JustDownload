# 视频解析器重构完成

## 更新概述

将 seacms 插件中的 M3U8 解析器功能抽离为独立的全局视频解析器插件系统，所有搜索插件都可以使用。

## 主要改动

### 1. 后端架构

#### 新增解析器插件系统
- **`backend/base_plugin.py`**: 添加 `ParserPlugin` 基类
- **`backend/plugins/parser/m3u8_parser_plugin.py`**: M3U8 解析器插件实现
- **`backend/plugin_manager.py`**: 
  - 支持 parser 类型插件的注册和管理
  - 添加 `get_active_parsers()` 方法获取启用的解析器
  - 添加 `parse_video_urls()` 方法为剧集批量添加解析链接
  - 添加 `_migrate_old_config()` 自动迁移旧配置

#### 搜索插件优化
- **`backend/plugins/search/seacms_plugin.py`**:
  - 移除 `m3u8_parsers_list` 配置字段
  - 简化剧集数据结构：`episode_name` + `play_url`
  - 添加 `description` 字段（简短描述）
  - 添加 `full_description` 字段（完整描述）
  - 版本升级到 2.0.0

#### API 增强
- **`backend/main.py`**:
  - 注册 M3U8 解析器插件
  - 搜索 API 自动为结果添加解析链接
  - `/api/plugins` 返回包含 parser 类型插件

### 2. 前端界面

#### 新增组件
- **`frontend/src/components/VideoDetailDialog.vue`**: 视频详情浮窗
  - 显示视频封面、描述、来源等信息
  - 展示剧集列表
  - 每个剧集显示原始链接和所有解析后的链接
  - 支持一键复制链接

#### 搜索页面优化
- **`frontend/src/views/Search.vue`**:
  - 搜索结果列表显示简短描述
  - 添加"播放"按钮，点击打开详情浮窗
  - 保留"下载"按钮用于下载功能

#### 设置页面增强
- **`frontend/src/views/Settings.vue`**:
  - 添加"视频解析器"标签页
  - 与搜索插件、下载插件并列展示
  - 支持启用/禁用解析器
  - 支持配置多个解析器地址

### 3. 配置迁移

#### 自动迁移逻辑
- 启动时自动检测 `search:seacms` 配置中的 `m3u8_parsers_list`
- 将旧配置迁移到 `parser:m3u8` 配置
- 从 seacms 配置中移除旧字段
- 保持向后兼容，不影响现有用户

#### 配置文件变化
**旧配置** (`config/plugins.json`):
```json
{
  "search:seacms": {
    "resource_sites_list": [...],
    "m3u8_parsers_list": [
      {"name": "解析器1", "parser_url": "...", "enabled": true}
    ]
  }
}
```

**新配置**:
```json
{
  "search:seacms": {
    "resource_sites_list": [...]
  },
  "parser:m3u8": {
    "parsers_list": [
      {"name": "解析器1", "parser_url": "...", "enabled": true}
    ]
  }
}
```

## 数据流

```
用户搜索关键词
    ↓
搜索插件返回结果（包含剧集列表）
    ↓
插件管理器应用所有启用的解析器
    ↓
为每个剧集的 play_url 生成解析链接
    ↓
返回增强后的结果（原始链接 + 解析链接）
    ↓
前端展示：
  - 列表：显示简短描述 + 播放按钮
  - 详情浮窗：显示完整信息 + 所有播放链接
```

## 剧集数据结构

### 搜索插件返回
```json
{
  "episode_name": "第1集",
  "play_url": "https://example.com/ep1.m3u8",
  "flag": "虎牙播放器",
  "is_m3u8": true
}
```

### 经过解析器增强后
```json
{
  "episode_name": "第1集",
  "play_url": "https://example.com/ep1.m3u8",
  "flag": "虎牙播放器",
  "is_m3u8": true,
  "parsed_urls": [
    {
      "name": "P2P商业加速",
      "url": "https://mtjiexi.cc:966/?url=https://example.com/ep1.m3u8"
    },
    {
      "name": "备用解析",
      "url": "https://www.mtjiexi.cc:966/?url=https://example.com/ep1.m3u8"
    }
  ]
}
```

## 使用方式

### 1. 配置解析器
1. 进入"设置"页面
2. 切换到"视频解析器"标签
3. 启用 M3U8 解析器
4. 点击"展开配置"
5. 添加/编辑解析器列表

### 2. 搜索视频
1. 在搜索页面输入关键词
2. 查看搜索结果（带简短描述）
3. 点击"播放"按钮查看详情

### 3. 查看详情
1. 详情浮窗显示视频完整信息
2. 查看剧集列表
3. 每个剧集显示：
   - 原始地址（可直接播放或复制）
   - 解析后地址（使用配置的解析器）
4. 点击链接在新标签页打开
5. 点击"复制"按钮复制链接

## 扩展性

### 添加新的解析器插件
1. 继承 `ParserPlugin` 基类
2. 实现 `parse_url()` 方法
3. 在 `main.py` 中注册插件
4. 前端自动显示在"视频解析器"标签页

### 示例：创建自定义解析器
```python
from base_plugin import ParserPlugin
from models import ConfigField

class CustomParserPlugin(ParserPlugin):
    @property
    def name(self) -> str:
        return "custom"
    
    def parse_url(self, original_url: str) -> List[Dict[str, str]]:
        # 自定义解析逻辑
        return [{"name": "自定义解析", "url": f"https://custom.com/?v={original_url}"}]
```

## 测试

运行测试脚本验证功能：
```bash
python backend/test_parser_plugin.py
```

测试内容：
- ✓ 解析器插件注册和配置
- ✓ 单个URL解析
- ✓ 批量剧集解析
- ✓ 配置自动迁移

## 优势

1. **解耦合**: 解析器独立于搜索插件，易于维护
2. **全局可用**: 所有搜索插件都能使用解析器
3. **易扩展**: 可以轻松添加新的解析器类型
4. **向后兼容**: 自动迁移旧配置，不影响现有用户
5. **用户友好**: 统一的配置界面，清晰的数据展示

## 注意事项

1. 首次启动会自动迁移旧配置
2. 解析器只处理包含 `.m3u8` 的链接
3. 可以配置多个解析器，所有启用的解析器都会生成链接
4. 前端详情浮窗支持复制链接到剪贴板
