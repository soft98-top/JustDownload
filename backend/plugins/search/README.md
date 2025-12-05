# 搜索插件说明

## SeaCMS 资源采集插件

### 功能特性

- 支持海洋CMS标准API格式的资源站
- 可配置多个资源站并发搜索
- 自动过滤m3u8资源
- 支持多个m3u8解析器配置
- 支持代理设置

### 配置说明

#### 资源站列表 (resource_sites)
JSON格式数组，每个资源站包含：
- `name`: 资源站名称
- `api_url`: 资源站API地址（完整URL）
- `enabled`: 是否启用

示例：
```json
[
  {
    "name": "茅台资源",
    "api_url": "https://caiji.maotaizy.cc/api.php/provide/vod/at/xml",
    "enabled": true
  }
]
```

#### M3U8解析器列表 (m3u8_parsers)
JSON格式数组，每个解析器包含：
- `name`: 解析器名称
- `parser_url`: 解析器地址（需要以`?url=`结尾）
- `enabled`: 是否启用

示例：
```json
[
  {
    "name": "P2P商业加速",
    "parser_url": "https://mtjiexi.cc:966/?url=",
    "enabled": true
  }
]
```

#### 其他配置
- `only_m3u8`: 只采集m3u8资源（默认true）
- `use_proxy`: 是否使用代理（默认false）
- `proxy_url`: 代理地址（例如：http://127.0.0.1:7890）
- `timeout`: 请求超时时间（秒，默认30）

### 返回数据结构

每个搜索结果包含：
- `title`: 视频标题
- `url`: 第一集的播放地址
- `thumbnail`: 封面图
- `platform`: 来源资源站名称
- `metadata`: 详细信息
  - `video_id`: 视频ID
  - `note`: 更新备注
  - `episodes`: 剧集列表
    - `name`: 集数名称
    - `url`: 原始播放地址
    - `flag`: 播放器标识
    - `is_m3u8`: 是否为m3u8
    - `parsed_urls`: 解析后的地址列表
  - `episode_count`: 总集数
  - `has_m3u8`: 是否包含m3u8
  - `m3u8_count`: m3u8集数

### 使用示例

```python
from plugins.search.seacms_plugin import SeaCMSSearchPlugin

plugin = SeaCMSSearchPlugin()
plugin.set_config({
    'resource_sites': [...],
    'm3u8_parsers': [...],
    'only_m3u8': True
})

results = await plugin.search("斗罗大陆")
for result in results:
    print(f"{result.title} - {result.metadata['episode_count']}集")
```

### 兼容的资源站

理论上支持所有使用海洋CMS标准API的资源站，包括但不限于：
- 茅台资源
- 非凡资源
- 量子资源
- 红牛资源
- 等等...

只需要获取资源站的API地址即可配置使用。
