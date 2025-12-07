# 配置处理最佳实践

## 问题背景

在插件开发中，配置值可能来自用户输入，可能是空字符串、None或其他意外类型。直接使用 `int()` 或 `float()` 转换可能导致运行时错误。

**常见错误**：
```python
# ❌ 不安全的方式
max_retries = int(self.config.get('max_retries', 3))
# 如果配置值是空字符串 ''，会抛出 ValueError
```

## 解决方案

使用基类提供的配置辅助方法，安全地获取配置值。

## 配置辅助方法

所有插件基类（`SearchPlugin`、`DownloadPlugin`、`ParserPlugin`）都继承自 `BasePlugin`，提供以下辅助方法：

### 1. `_get_config_int(key, default)`

安全地获取整数配置值。

```python
# ✅ 安全的方式
max_retries = self._get_config_int('max_retries', 3)
timeout = self._get_config_int('timeout', 30)
```

**处理逻辑**：
- 如果值为空字符串或None，返回默认值
- 尝试转换为int，失败则返回默认值并记录警告
- 自动处理类型错误

### 2. `_get_config_float(key, default)`

安全地获取浮点数配置值。

```python
# ✅ 安全的方式
retry_delay = self._get_config_float('retry_delay', 2.0)
speed_limit = self._get_config_float('speed_limit', 0.0)
```

**处理逻辑**：
- 如果值为空字符串或None，返回默认值
- 尝试转换为float，失败则返回默认值并记录警告

### 3. `_get_config_bool(key, default)`

安全地获取布尔配置值。

```python
# ✅ 安全的方式
use_proxy = self._get_config_bool('use_proxy', False)
auto_convert = self._get_config_bool('auto_convert', True)
```

**处理逻辑**：
- 如果值为空字符串或None，返回默认值
- 如果是布尔类型，直接返回
- 如果是字符串，识别 'true', '1', 'yes', 'on' 为True
- 其他情况转换为布尔值

### 4. `_get_config_str(key, default)`

安全地获取字符串配置值。

```python
# ✅ 安全的方式
api_key = self._get_config_str('api_key', '')
base_url = self._get_config_str('base_url', 'https://example.com')
proxy_url = self._get_config_str('proxy_url', '')
```

**处理逻辑**：
- 如果值为None，返回默认值
- 其他情况转换为字符串

## 完整示例

### 错误示例 ❌

```python
class MyPlugin(SearchPlugin):
    async def search(self, keyword: str) -> List[SearchResult]:
        # 危险：可能抛出 ValueError
        max_results = int(self.config.get('max_results', 10))
        timeout = float(self.config.get('timeout', 30))
        use_proxy = bool(self.config.get('use_proxy', False))
        
        # ... 搜索逻辑
```

### 正确示例 ✅

```python
class MyPlugin(SearchPlugin):
    async def search(self, keyword: str) -> List[SearchResult]:
        # 安全：自动处理空值和类型错误
        max_results = self._get_config_int('max_results', 10)
        timeout = self._get_config_float('timeout', 30.0)
        use_proxy = self._get_config_bool('use_proxy', False)
        api_key = self._get_config_str('api_key', '')
        
        # 检查必需配置
        if not api_key:
            logger.warning("API密钥未配置")
            return []
        
        # ... 搜索逻辑
```

## 配置验证

### 在插件初始化时验证

```python
class MyPlugin(SearchPlugin):
    def set_config(self, config: Dict[str, Any]):
        super().set_config(config)
        
        # 验证必需配置
        api_key = self._get_config_str('api_key', '')
        if not api_key:
            logger.warning(f"[{self.name}] API密钥未配置，插件可能无法正常工作")
```

### 在方法中验证

```python
async def search(self, keyword: str) -> List[SearchResult]:
    api_key = self._get_config_str('api_key', '')
    
    # 提前返回，避免无效请求
    if not api_key:
        logger.error(f"[{self.name}] API密钥未配置")
        return []
    
    # ... 继续执行
```

## 配置类型定义

在 `get_config_schema()` 中明确定义配置类型：

```python
def get_config_schema(self) -> List[ConfigField]:
    return [
        ConfigField(
            name="max_results",
            label="最大结果数",
            type="number",          # 明确类型
            default=20,             # 提供默认值
            required=False,         # 标记是否必需
            description="每次搜索返回的最大结果数"
        ),
        ConfigField(
            name="api_key",
            label="API密钥",
            type="password",
            required=True,          # 必需配置
            description="平台API密钥"
        ),
        ConfigField(
            name="use_proxy",
            label="使用代理",
            type="boolean",
            default=False
        )
    ]
```

## 常见陷阱

### 陷阱1：空字符串转整数

```python
# ❌ 错误
value = int('')  # ValueError: invalid literal for int()

# ✅ 正确
value = self._get_config_int('key', 0)  # 返回默认值 0
```

### 陷阱2：None转浮点数

```python
# ❌ 错误
value = float(None)  # TypeError: float() argument must be a string or a number

# ✅ 正确
value = self._get_config_float('key', 0.0)  # 返回默认值 0.0
```

### 陷阱3：字符串转布尔

```python
# ❌ 错误（'false' 会被转换为 True）
value = bool('false')  # True（非空字符串）

# ✅ 正确
value = self._get_config_bool('key', False)  # 正确识别 'false'
```

### 陷阱4：忘记提供默认值

```python
# ❌ 不好（如果配置不存在会返回None）
value = self.config.get('key')

# ✅ 好（总是有一个合理的默认值）
value = self._get_config_str('key', 'default_value')
```

## 日志记录

辅助方法会自动记录配置错误：

```python
# 如果配置值无效，会自动记录警告
max_retries = self._get_config_int('max_retries', 3)
# 日志输出: WARNING [jable] 配置项 max_retries 的值 '' 无效，使用默认值 3
```

## 测试建议

测试插件时，应该测试各种配置值：

```python
# 测试空值
plugin.set_config({'max_results': ''})
result = plugin._get_config_int('max_results', 10)
assert result == 10

# 测试None
plugin.set_config({'max_results': None})
result = plugin._get_config_int('max_results', 10)
assert result == 10

# 测试无效值
plugin.set_config({'max_results': 'abc'})
result = plugin._get_config_int('max_results', 10)
assert result == 10

# 测试正常值
plugin.set_config({'max_results': 20})
result = plugin._get_config_int('max_results', 10)
assert result == 20
```

## 总结

✅ **始终使用配置辅助方法**
- `_get_config_int()` - 整数
- `_get_config_float()` - 浮点数
- `_get_config_bool()` - 布尔值
- `_get_config_str()` - 字符串

✅ **提供合理的默认值**

✅ **验证必需配置**

✅ **在配置schema中明确类型**

✅ **记录配置错误**

这样可以确保插件在各种配置情况下都能稳定运行！
