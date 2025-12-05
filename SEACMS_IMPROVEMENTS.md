# SeaCMS插件改进说明

## 更新日期
2025-12-05

## 改进内容

### 1. 搜索插件框架增加描述字段支持

**修改文件**: `backend/base_plugin.py`, `backend/models.py`

- 在`SearchPlugin`基类中为`description`属性添加了详细注释
- 在`SearchResult`模型中添加了`description`字段，用于存储资源的详细描述
- SeaCMS插件现在会从XML响应中提取`<des>`标签的内容作为描述

**使用示例**:
```python
result = SearchResult(
    title="电影名称",
    url="https://example.com/video.m3u8",
    platform="茅台资源",
    description="这是一部精彩的电影..."  # 新增的描述字段
)
```

### 2. 资源站配置支持URL前缀/后缀清理

**修改文件**: `backend/plugins/search/seacms_plugin.py`

**问题**: 某些资源站的视频链接包含个性化的前缀或后缀，例如：
- `https://1080p.huyall.com/play/mep3QRQd/index.m3u8$hym3u8`
- 后缀 `$hym3u8` 会导致下载失败

**解决方案**: 
在资源站配置中添加`url_prefix`和`url_suffix`字段：

```json
{
  "name": "示例资源站",
  "api_url": "https://example.com/api.php/provide/vod/at/xml",
  "url_prefix": "",
  "url_suffix": "$hym3u8",
  "enabled": true
}
```

**功能**:
- 插件会自动去除配置的前缀和后缀
- 支持同时配置前缀和后缀
- 如果不需要清理，留空即可

**实现方法**:
```python
def _clean_url(self, url: str, site: Dict[str, Any]) -> str:
    """清理URL，去除个性化前缀和后缀"""
    cleaned_url = url
    
    # 去除后缀
    url_suffix = site.get('url_suffix', '').strip()
    if url_suffix and cleaned_url.endswith(url_suffix):
        cleaned_url = cleaned_url[:-len(url_suffix)]
    
    # 去除前缀
    url_prefix = site.get('url_prefix', '').strip()
    if url_prefix and cleaned_url.startswith(url_prefix):
        cleaned_url = cleaned_url[len(url_prefix):]
    
    return cleaned_url
```

### 3. 下载地址支持手动修改

**修改文件**: `frontend/src/components/DownloadDialog.vue`

**改进**:
- 将下载地址从只读的预览框改为可编辑的文本框
- 用户可以在下载前手动修改URL
- 支持多行显示，方便查看和编辑长URL

**UI变化**:
```vue
<!-- 之前：只读预览 -->
<div class="url-preview">{{ downloadUrl }}</div>

<!-- 现在：可编辑文本框 -->
<textarea 
  v-model="editableUrl" 
  class="url-input"
  rows="3"
  placeholder="输入或修改下载地址"
></textarea>
```

### 4. 优化下载插件选择逻辑

**修改文件**: `frontend/src/components/DownloadDialog.vue`

**改进前**: 
- 默认显示"自动选择"
- 用户需要手动选择插件

**改进后**:
- 默认自动选择第一个启用的下载插件
- 减少用户操作步骤
- 更符合用户使用习惯

**实现**:
```javascript
watch: {
  show(newVal) {
    if (newVal) {
      // 默认选择第一个启用的下载插件
      this.selectedDownloader = this.enabledDownloadPlugins.length > 0 
        ? this.enabledDownloadPlugins[0].name 
        : ''
    }
  }
}
```

### 5. 禁用的下载插件不显示

**修改文件**: `frontend/src/components/DownloadDialog.vue`

**改进**:
- 下载对话框中只显示已启用的下载插件
- 避免用户选择已禁用的插件导致错误

**实现**:
```javascript
computed: {
  // 只显示启用的下载插件
  enabledDownloadPlugins() {
    return (this.downloadPlugins || []).filter(plugin => plugin.enabled !== false)
  }
}
```

```vue
<select v-model="selectedDownloader" class="full-width">
  <option v-for="plugin in enabledDownloadPlugins" :key="plugin.name" :value="plugin.name">
    {{ plugin.description }} ({{ plugin.supported_protocols.join(', ') }})
  </option>
</select>
```

## 测试

运行测试脚本验证功能：

```bash
python backend/test_seacms_improvements.py
```

测试内容：
1. ✓ URL清理功能（前缀/后缀去除）
2. ✓ 配置字段包含url_prefix和url_suffix
3. ✓ SearchResult支持description字段

## 使用指南

### 配置资源站前缀/后缀

1. 进入设置页面
2. 选择SeaCMS插件
3. 编辑资源站列表
4. 为需要清理URL的资源站添加`url_prefix`和`url_suffix`字段

示例配置：
```json
[
  {
    "name": "茅台资源",
    "api_url": "https://caiji.maotaizy.cc/api.php/provide/vod/at/xml",
    "url_prefix": "",
    "url_suffix": "",
    "enabled": true
  },
  {
    "name": "示例资源站（带后缀）",
    "api_url": "https://example.com/api.php/provide/vod/at/xml",
    "url_prefix": "",
    "url_suffix": "$hym3u8",
    "enabled": true
  }
]
```

### 手动修改下载地址

1. 在搜索结果中点击"下载选项"
2. 在下载对话框中，下载地址显示在可编辑的文本框中
3. 直接修改URL（如果需要）
4. 点击"确认下载"

### 管理下载插件

1. 在设置页面启用/禁用下载插件
2. 禁用的插件不会出现在下载对话框中
3. 下载对话框默认选择第一个启用的插件

## 兼容性

- 所有改进都向后兼容
- 旧的配置文件会自动适配（url_prefix和url_suffix默认为空字符串）
- 不影响现有功能

## 相关文件

- `backend/base_plugin.py` - 插件基类
- `backend/models.py` - 数据模型
- `backend/plugins/search/seacms_plugin.py` - SeaCMS插件
- `frontend/src/components/DownloadDialog.vue` - 下载对话框
- `backend/test_seacms_improvements.py` - 测试脚本
