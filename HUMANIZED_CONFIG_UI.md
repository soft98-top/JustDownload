# 人性化配置界面实现

## 更新日期
2025-12-05

## 改进内容

将SeaCMS插件的配置从JSON文本编辑改为人性化的表单界面。

## 修改前后对比

### 修改前（JSON文本编辑）
```
资源站列表:
[
  {
    "name": "茅台资源",
    "api_url": "https://...",
    "url_prefix": "",
    "url_suffix": "$hym3u8",
    "enabled": true
  }
]
```
- 需要手动编辑JSON
- 容易出现格式错误
- 不直观

### 修改后（表单界面）
```
资源站
  #1
    资源站名称: [茅台资源]
    API地址: [https://...]
    URL前缀（可选）: []
    URL后缀（可选，如$hym3u8）: [$hym3u8]
    ☑ 启用
  [+ 添加资源站]
```
- 每个字段独立输入
- 清晰的标签说明
- 可视化的启用/禁用开关
- 一键添加/删除

## 实现细节

### 1. 更新ConfigField模型

**文件**: `backend/models.py`

添加`fields`属性支持列表类型的子字段定义：

```python
class ConfigField(BaseModel):
    """插件配置字段定义"""
    name: str
    label: str
    type: str  # text, password, number, boolean, select, list
    default: Any = None
    required: bool = False
    options: List[str] = []
    description: str = ""
    fields: List[Dict[str, Any]] = []  # 用于list类型的子字段定义
```

### 2. 更新SeaCMS插件配置

**文件**: `backend/plugins/search/seacms_plugin.py`

将配置字段类型从`text`改为`list`，并定义子字段结构：

```python
ConfigField(
    name="resource_sites_list",
    label="资源站",
    type="list",
    default=[],
    required=True,
    description='添加多个资源站，支持所有海洋CMS兼容的API',
    fields=[
        {"name": "name", "label": "资源站名称", "type": "text", "default": ""},
        {"name": "api_url", "label": "API地址", "type": "text", "default": ""},
        {"name": "url_prefix", "label": "URL前缀（可选）", "type": "text", "default": ""},
        {"name": "url_suffix", "label": "URL后缀（可选，如$hym3u8）", "type": "text", "default": ""},
        {"name": "enabled", "label": "启用", "type": "boolean", "default": True}
    ]
)
```

### 3. 重写列表编辑器UI

**文件**: `frontend/src/components/PluginConfigForm.vue`

#### 结构改进
- 每个列表项显示为独立的卡片
- 顶部显示序号和删除按钮
- 子字段按类型分别渲染
- 布尔字段显示为复选框
- 文本/数字字段显示为输入框

#### 模板代码
```vue
<div v-else-if="field.type === 'list'" class="list-editor">
  <div v-for="(item, index) in formData[field.name]" :key="index" class="list-item">
    <div class="list-item-header">
      <span class="list-item-number">#{{ index + 1 }}</span>
      <button @click="removeListItem(field.name, index)" class="btn-remove-small">
        ✕
      </button>
    </div>
    <div class="list-item-fields">
      <div v-for="subField in field.fields" :key="subField.name" class="list-subfield">
        <!-- 布尔类型 -->
        <label v-if="subField.type === 'boolean'" class="subfield-checkbox">
          <input type="checkbox" v-model="item[subField.name]" />
          <span>{{ subField.label }}</span>
        </label>
        
        <!-- 文本/数字类型 -->
        <div v-else class="subfield-text">
          <label>{{ subField.label }}</label>
          <input
            :type="subField.type === 'number' ? 'number' : 'text'"
            v-model="item[subField.name]"
            :placeholder="subField.label"
            class="list-item-input"
          />
        </div>
      </div>
    </div>
  </div>
  <button @click="addListItem(field.name, field.fields)" class="btn-add">
    + 添加{{ field.label }}
  </button>
</div>
```

### 4. 样式优化

#### 卡片式设计
```css
.list-item {
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
```

#### 序号和删除按钮
```css
.list-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.list-item-number {
  font-weight: 600;
  color: #3498db;
}

.btn-remove-small {
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
}
```

#### 复选框样式
```css
.subfield-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
  cursor: pointer;
}

.subfield-checkbox:hover {
  background: #e9ecef;
}
```

## 功能特性

### 1. 直观的字段输入
- 每个字段都有清晰的标签
- 输入框带有占位符提示
- 布尔值使用复选框

### 2. 灵活的列表管理
- 点击"+ 添加"按钮新增项
- 点击"✕"按钮删除项
- 自动编号显示顺序

### 3. 视觉反馈
- 卡片式设计，层次分明
- 悬停效果提升交互体验
- 颜色区分不同状态

### 4. 数据验证
- 自动处理字段类型
- 保持数据结构完整性
- 支持默认值

## 使用指南

### 添加资源站

1. 打开设置页面
2. 展开SeaCMS插件配置
3. 在"资源站"部分点击"+ 添加资源站"
4. 填写各个字段：
   - **资源站名称**: 自定义名称，如"茅台资源"
   - **API地址**: 资源站的API URL
   - **URL前缀**: 如果链接有前缀需要去除，填写在这里
   - **URL后缀**: 如果链接有后缀需要去除（如`$hym3u8`），填写在这里
   - **启用**: 勾选以启用该资源站
5. 点击"保存配置"

### 添加M3U8解析器

1. 在"M3U8解析器"部分点击"+ 添加M3U8解析器"
2. 填写字段：
   - **解析器名称**: 如"P2P商业加速"
   - **解析器地址**: 解析器的URL前缀
   - **启用**: 勾选以启用该解析器
3. 点击"保存配置"

### 删除项目

点击每个项目右上角的"✕"按钮即可删除。

## 修改文件清单

- ✅ `backend/models.py` - 添加fields属性
- ✅ `backend/plugins/search/seacms_plugin.py` - 改用list类型配置
- ✅ `frontend/src/components/PluginConfigForm.vue` - 重写列表编辑器UI

## 优势

1. **用户友好**: 不需要了解JSON格式
2. **减少错误**: 避免JSON语法错误
3. **直观清晰**: 每个字段的作用一目了然
4. **易于维护**: 添加/删除/修改都很方便
5. **视觉美观**: 现代化的卡片式设计

## 兼容性

- ✅ 自动迁移旧的JSON配置
- ✅ 保持数据结构不变
- ✅ 向后兼容

## 效果预览

```
┌─────────────────────────────────────────┐
│ 资源站                                   │
├─────────────────────────────────────────┤
│ ┌─────────────────────────────────────┐ │
│ │ #1                              ✕   │ │
│ ├─────────────────────────────────────┤ │
│ │ 资源站名称                           │ │
│ │ [茅台资源                    ]       │ │
│ │                                     │ │
│ │ API地址                             │ │
│ │ [https://caiji.maotaizy.cc/...]    │ │
│ │                                     │ │
│ │ URL前缀（可选）                      │ │
│ │ [                            ]       │ │
│ │                                     │ │
│ │ URL后缀（可选，如$hym3u8）           │ │
│ │ [$hym3u8                     ]       │ │
│ │                                     │ │
│ │ ☑ 启用                              │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [+ 添加资源站]                          │
└─────────────────────────────────────────┘
```

## 总结

通过将JSON文本编辑改为人性化的表单界面，大大提升了配置的易用性和用户体验。用户无需了解JSON格式，就能轻松管理资源站和解析器配置。
