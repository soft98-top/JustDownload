# 插件过滤优化

## 更新时间
2024年12月5日

## 优化内容

### 1. 搜索页面优化

#### 只显示启用的插件
- 插件选择器只显示已启用的搜索插件
- 禁用的插件不会出现在下拉列表中
- 使用 `computed` 属性过滤启用的插件

#### 默认选择第一个插件
- 页面加载时自动选择第一个启用的插件
- 无需用户手动选择
- 提升用户体验

#### 无插件提示
- 如果没有启用的搜索插件，显示友好的警告提示
- 提示用户前往设置页面启用插件
- 禁用搜索输入框和按钮

### 2. 下载管理页面优化

#### 平台选择器
- 只显示启用的下载插件
- 动态生成平台选项
- 保留"全部平台"选项

#### 新增下载对话框
- 插件选择器只显示启用的下载插件
- 保留"自动选择"选项
- 动态生成插件选项

## 实现细节

### 搜索页面（Search.vue）

#### 计算属性
```javascript
computed: {
  enabledSearchPlugins() {
    // 只返回启用的搜索插件
    return this.searchPlugins.filter(plugin => plugin.enabled !== false)
  }
}
```

#### 默认选择
```javascript
async loadPlugins() {
  const response = await axios.get('/api/plugins')
  this.searchPlugins = response.data.search || []
  
  // 默认选择第一个启用的搜索插件
  const enabledPlugins = this.searchPlugins.filter(p => p.enabled !== false)
  if (enabledPlugins.length > 0) {
    this.selectedPlugin = enabledPlugins[0].name
  }
}
```

#### 模板更新
```vue
<select v-model="selectedPlugin" v-if="enabledSearchPlugins.length > 0">
  <option v-for="plugin in enabledSearchPlugins" :key="plugin.name" :value="plugin.name">
    {{ plugin.description }}
  </option>
</select>
<div v-else class="no-plugins-warning">
  <span>⚠️ 没有启用的搜索插件，请前往设置页面启用</span>
</div>
```

### 下载管理页面（Downloads.vue）

#### 计算属性
```javascript
computed: {
  enabledDownloadPlugins() {
    // 只返回启用的下载插件
    return this.downloadPlugins.filter(plugin => plugin.enabled !== false)
  }
}
```

#### 平台选择器
```vue
<select v-model="selectedPlatform" @change="loadDownloads" class="platform-select">
  <option value="all">全部平台</option>
  <option v-for="plugin in enabledDownloadPlugins" :key="plugin.name" :value="plugin.name">
    {{ getPlatformDisplayName(plugin.name) }}
  </option>
</select>
```

#### 新增下载对话框
```vue
<select v-model="newDownload.plugin">
  <option value="">自动选择</option>
  <option v-for="plugin in enabledDownloadPlugins" :key="plugin.name" :value="plugin.name">
    {{ getPlatformDisplayName(plugin.name) }}
  </option>
</select>
```

## 用户体验改进

### 搜索页面

**之前：**
- 显示所有插件（包括禁用的）
- 需要手动选择插件
- 可能选择到禁用的插件导致错误

**现在：**
- 只显示启用的插件
- 自动选择第一个插件
- 无插件时显示友好提示

### 下载管理页面

**之前：**
- 硬编码的平台选项
- 显示所有平台（包括禁用的）

**现在：**
- 动态生成平台选项
- 只显示启用的平台
- 更灵活的插件管理

## 样式优化

### 无插件警告样式
```css
.no-plugins-warning {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 4px;
  color: #856404;
  font-size: 0.9rem;
}
```

### 禁用状态样式
```css
.search-form input:disabled,
.search-form button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

## 行为说明

### 插件过滤逻辑

1. **获取插件列表** - 从 API 获取所有插件及其启用状态
2. **过滤启用插件** - 使用 `computed` 属性过滤 `enabled !== false` 的插件
3. **动态渲染** - 根据过滤后的列表渲染选项

### 默认选择逻辑

1. **加载插件** - 页面挂载时加载插件列表
2. **过滤启用插件** - 获取启用的插件列表
3. **选择第一个** - 如果有启用的插件，选择第一个

### 无插件处理

1. **检查数量** - 检查启用的插件数量
2. **显示警告** - 如果为 0，显示警告信息
3. **禁用操作** - 禁用相关的输入和按钮

## 测试场景

### 场景 1：正常使用
1. 至少有一个启用的搜索插件
2. 打开搜索页面
3. 验证：自动选择第一个插件
4. 验证：只显示启用的插件

### 场景 2：无启用插件
1. 禁用所有搜索插件
2. 打开搜索页面
3. 验证：显示警告信息
4. 验证：搜索功能被禁用

### 场景 3：部分启用
1. 启用部分插件，禁用部分插件
2. 打开搜索页面
3. 验证：只显示启用的插件
4. 验证：禁用的插件不在列表中

### 场景 4：动态切换
1. 在设置页面禁用当前选中的插件
2. 返回搜索页面
3. 验证：自动切换到其他启用的插件
4. 验证：如果没有其他插件，显示警告

## 优势

1. **更好的用户体验** - 自动选择，减少操作步骤
2. **避免错误** - 不显示禁用的插件，避免选择错误
3. **友好提示** - 无插件时给出明确的指引
4. **动态更新** - 插件状态变化时自动更新界面
5. **一致性** - 所有页面使用相同的过滤逻辑

## 相关文件

- `frontend/src/views/Search.vue` - 搜索页面
- `frontend/src/views/Downloads.vue` - 下载管理页面
- `frontend/src/views/Settings.vue` - 设置页面

## 后续改进建议

1. 添加插件状态变化的实时通知
2. 记住用户最后选择的插件
3. 添加插件快速切换快捷键
4. 支持插件分组和排序
5. 添加插件使用频率统计
