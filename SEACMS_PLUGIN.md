# 海洋CMS搜索插件实现说明

## 实现完成 ✅

已成功实现海洋CMS资源采集搜索插件，支持以下功能：

### 核心功能

1. **多资源站支持**
   - 可配置多个资源站URL
   - 并发搜索所有启用的资源站
   - 自动合并搜索结果

2. **M3U8资源过滤**
   - 自动识别m3u8播放源
   - 可配置只返回m3u8资源
   - 统计m3u8集数

3. **M3U8解析器**
   - 支持配置多个解析器
   - 自动为每个m3u8地址生成解析后的URL
   - 前端可选择使用原始地址或解析地址播放

4. **代理支持**
   - 可配置HTTP/HTTPS代理
   - 支持单独为每个请求启用/禁用代理

### 配置示例

```json
{
  "resource_sites": [
    {
      "name": "茅台资源",
      "api_url": "https://caiji.maotaizy.cc/api.php/provide/vod/at/xml",
      "enabled": true
    }
  ],
  "m3u8_parsers": [
    {
      "name": "P2P商业加速解析",
      "parser_url": "https://mtjiexi.cc:966/?url=",
      "enabled": true
    },
    {
      "name": "加速解析（备用）",
      "parser_url": "https://www.mtjiexi.cc:966/?url=",
      "enabled": true
    }
  ],
  "only_m3u8": true,
  "use_proxy": false,
  "proxy_url": "",
  "timeout": 30
}
```

### 测试结果

搜索"斗罗大陆"测试通过：
- ✅ 成功获取20个结果
- ✅ 正确解析剧集信息（129集、162集等）
- ✅ 正确过滤m3u8资源
- ✅ 成功生成解析后的播放地址
- ✅ 封面图、标题、备注等信息完整

### 返回数据示例

```python
SearchResult(
    title="斗罗大陆2：绝世唐门",
    url="https://vodcnd03.kunyu.com.cn/20250223/sur2zzGA/index.m3u8",
    thumbnail="https://mtzy1.com/upload/vod/xxx.jpg",
    platform="茅台资源",
    metadata={
        "video_id": "70360",
        "note": "第129集",
        "episodes": [
            {
                "name": "第01集",
                "url": "https://vodcnd03.kunyu.com.cn/20250223/sur2zzGA/index.m3u8",
                "flag": "mtm3u8",
                "is_m3u8": True,
                "parsed_urls": [
                    {
                        "name": "P2P商业加速",
                        "url": "https://mtjiexi.cc:966/?url=https://vodcnd03.kunyu.com.cn/20250223/sur2zzGA/index.m3u8"
                    },
                    {
                        "name": "备用解析",
                        "url": "https://www.mtjiexi.cc:966/?url=https://vodcnd03.kunyu.com.cn/20250223/sur2zzGA/index.m3u8"
                    }
                ]
            },
            // ... 更多剧集
        ],
        "episode_count": 129,
        "has_m3u8": True,
        "m3u8_count": 129
    }
)
```

### 文件位置

- 插件代码：`backend/plugins/search/seacms_plugin.py`
- 测试代码：`backend/test_seacms.py`
- 插件文档：`backend/plugins/search/README.md`
- 主程序集成：`backend/main.py`（已注册）

### 使用方法

#### 1. 后端API

```bash
# 列出所有插件
GET /api/plugins

# 配置插件
POST /api/plugins/search/seacms/config
{
  "resource_sites": [...],
  "m3u8_parsers": [...]
}

# 搜索
GET /api/search/seacms?keyword=斗罗大陆
```

#### 2. 前端使用

在前端的搜索页面中：
1. 选择"海洋CMS资源采集插件"
2. 输入关键词搜索
3. 显示搜索结果（包含剧集列表）
4. 用户可选择：
   - 直接播放原始m3u8地址
   - 使用解析器加速播放

### 扩展性

插件设计为通用的海洋CMS采集插件，理论上支持所有使用海洋CMS标准API的资源站，包括：

- 茅台资源
- 非凡资源
- 量子资源
- 红牛资源
- 光速资源
- 闪电资源
- 鱼乐资源
- 等等...

只需在配置中添加资源站的API地址即可。

### 下一步建议

1. **前端界面优化**
   - 显示剧集选择器
   - 支持选择解析器
   - 添加播放器集成

2. **功能增强**
   - 添加资源站健康检查
   - 支持分类浏览
   - 添加搜索历史
   - 支持收藏功能

3. **性能优化**
   - 添加搜索结果缓存
   - 实现增量加载
   - 优化并发请求数量
