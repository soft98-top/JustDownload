# 前端测试指南

## 问题诊断

后端已经正确返回了新的配置schema（type: list），但前端仍显示旧的JSON文本框。

## 可能的原因

1. **浏览器缓存** - 前端JavaScript或API响应被缓存
2. **页面未刷新** - 需要硬刷新页面
3. **前端代码未更新** - 前端构建未重新编译

## 解决步骤

### 1. 硬刷新浏览器

**Mac**: `Cmd + Shift + R`
**Windows/Linux**: `Ctrl + Shift + R`

或者：
1. 打开开发者工具（F12）
2. 右键点击刷新按钮
3. 选择"清空缓存并硬性重新加载"

### 2. 清除浏览器缓存

1. 打开开发者工具（F12）
2. 进入 Network 标签
3. 勾选 "Disable cache"
4. 刷新页面

### 3. 验证API响应

在浏览器控制台执行：

```javascript
fetch('/api/plugins')
  .then(r => r.json())
  .then(data => {
    const seacms = data.search.find(p => p.name === 'seacms');
    console.log('Schema type:', seacms.config_schema[0].type);
    console.log('Has fields:', 'fields' in seacms.config_schema[0]);
    console.log('Fields:', seacms.config_schema[0].fields);
  });
```

**期望输出**:
```
Schema type: list
Has fields: true
Fields: Array(5) [...]
```

### 4. 检查前端是否正确渲染

在设置页面，打开浏览器控制台，执行：

```javascript
// 查看Vue组件的props
const settingsComponent = document.querySelector('[data-v-app]').__vueParentComponent;
console.log('Plugins:', settingsComponent.ctx.searchPlugins);
```

### 5. 重启前端开发服务器

如果使用开发服务器：

```bash
# 停止前端服务
# 然后重新启动
npm run dev
# 或
yarn dev
```

### 6. 清除localStorage

在浏览器控制台执行：

```javascript
localStorage.clear();
location.reload();
```

## 验证成功的标志

刷新后，SeaCMS配置应该显示：

```
资源站 *
添加多个资源站，支持所有海洋CMS兼容的API

[+ 添加资源站]

M3U8解析器
添加多个M3U8解析器，用于加速播放

[+ 添加M3U8解析器]
```

而不是：

```
资源站列表 *
[
  {
    "name": "茅台资源",
    ...
  }
]
```

## 如果仍然不工作

### 检查前端代码

确认 `frontend/src/components/PluginConfigForm.vue` 包含列表编辑器代码：

```vue
<!-- 列表编辑器（用于资源站列表、解析器列表等） -->
<div v-else-if="field.type === 'list'" class="list-editor">
  <div v-for="(item, index) in formData[field.name]" :key="index" class="list-item">
    ...
  </div>
</div>
```

### 检查配置数据

旧的配置数据可能是JSON字符串格式，需要转换为数组。

在浏览器控制台执行：

```javascript
fetch('/api/plugins/search/seacms/config')
  .then(r => r.json())
  .then(data => {
    console.log('Config:', data.config);
    console.log('resource_sites_list type:', typeof data.config.resource_sites_list);
  });
```

如果返回的是字符串而不是数组，需要清除旧配置：

```bash
# 删除旧配置（谨慎操作！）
rm backend/config/search_seacms.json
```

然后重启后端。

## 调试技巧

### 1. 查看Vue组件状态

在浏览器控制台：

```javascript
// 找到PluginConfigForm组件
const forms = document.querySelectorAll('.config-form');
forms.forEach(form => {
  const vnode = form.__vnode;
  console.log('Schema:', vnode.component.props.schema);
  console.log('FormData:', vnode.component.data.formData);
});
```

### 2. 监控API请求

在Network标签中：
1. 筛选 XHR/Fetch 请求
2. 查找 `/api/plugins` 请求
3. 检查响应内容

### 3. Vue DevTools

如果安装了Vue DevTools：
1. 打开DevTools
2. 进入Components标签
3. 找到PluginConfigForm组件
4. 查看props和data

## 预期行为

### 初始状态（无配置）

```
资源站 *
添加多个资源站，支持所有海洋CMS兼容的API

[+ 添加资源站]
```

### 添加一个资源站后

```
资源站 *
添加多个资源站，支持所有海洋CMS兼容的API

┌─────────────────────────────────┐
│ #1                          ✕   │
├─────────────────────────────────┤
│ 资源站名称                       │
│ [                        ]       │
│                                 │
│ API地址                         │
│ [                        ]       │
│                                 │
│ URL前缀（可选）                  │
│ [                        ]       │
│                                 │
│ URL后缀（可选，如$hym3u8）       │
│ [                        ]       │
│                                 │
│ ☐ 启用                          │
└─────────────────────────────────┘

[+ 添加资源站]
```

## 总结

最常见的解决方法是**硬刷新浏览器**（Cmd+Shift+R 或 Ctrl+Shift+R）。

如果还不行，尝试：
1. 清除浏览器缓存
2. 清除localStorage
3. 重启前端开发服务器
4. 检查API响应是否正确
