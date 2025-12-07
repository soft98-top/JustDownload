# 配置文件说明

## config.json 参数详解

### backend 配置

```json
{
  "backend": {
    "host": "0.0.0.0",
    "port": 8000,
    "public_url": "http://localhost:8000"
  }
}
```

**参数说明:**

- **host**: 后端服务监听地址
  - `0.0.0.0` - 监听所有网卡，允许外部访问
  - `127.0.0.1` - 仅监听本地，只能本机访问
  - 推荐使用 `0.0.0.0` 以获得最大灵活性

- **port**: 后端服务端口
  - 默认: `8000`
  - 可以修改为任意未被占用的端口

- **public_url**: 后端对外访问地址
  - 本地开发: `http://localhost:8000`
  - 局域网: `http://192.168.x.x:8000`
  - 公网: `http://your-domain.com:8000` 或 `https://api.your-domain.com`

### frontend 配置

```json
{
  "frontend": {
    "host": "0.0.0.0",
    "port": 5173,
    "public_url": "http://localhost:5173",
    "api_url": "http://localhost:8000"
  }
}
```

**参数说明:**

- **host**: 前端服务监听地址
  - 同 backend.host

- **port**: 前端服务端口
  - 默认: `5173` (Vite 默认端口)
  - 可以修改为任意未被占用的端口

- **public_url**: 前端对外访问地址
  - 用户在浏览器中访问的地址
  - 本地开发: `http://localhost:5173`
  - 局域网: `http://192.168.x.x:5173`
  - 公网: `http://your-domain.com` 或 `https://your-domain.com`

- **api_url**: 前端访问后端的地址
  - **重要**: 必须是浏览器能访问到的地址
  - 不能使用 `0.0.0.0`
  - 如果前后端在同一台机器: `http://localhost:8000`
  - 如果前后端分开部署: 使用后端的实际 IP 或域名

## 配置示例

### 示例 1: 本地开发

```json
{
  "backend": {
    "host": "127.0.0.1",
    "port": 8000,
    "public_url": "http://localhost:8000"
  },
  "frontend": {
    "host": "127.0.0.1",
    "port": 5173,
    "public_url": "http://localhost:5173",
    "api_url": "http://localhost:8000"
  }
}
```

### 示例 2: 局域网部署

服务器 IP: 192.168.1.100

```json
{
  "backend": {
    "host": "0.0.0.0",
    "port": 8000,
    "public_url": "http://192.168.1.100:8000"
  },
  "frontend": {
    "host": "0.0.0.0",
    "port": 5173,
    "public_url": "http://192.168.1.100:5173",
    "api_url": "http://192.168.1.100:8000"
  }
}
```

### 示例 3: 使用非标准端口

```json
{
  "backend": {
    "host": "0.0.0.0",
    "port": 9000,
    "public_url": "http://localhost:9000"
  },
  "frontend": {
    "host": "0.0.0.0",
    "port": 3000,
    "public_url": "http://localhost:3000",
    "api_url": "http://localhost:9000"
  }
}
```

### 示例 4: 前后端分离部署

后端服务器: 192.168.1.100
前端服务器: 192.168.1.101

**后端配置:**
```json
{
  "backend": {
    "host": "0.0.0.0",
    "port": 8000,
    "public_url": "http://192.168.1.100:8000"
  }
}
```

**前端配置:**
```json
{
  "frontend": {
    "host": "0.0.0.0",
    "port": 5173,
    "public_url": "http://192.168.1.101:5173",
    "api_url": "http://192.168.1.100:8000"
  }
}
```

### 示例 5: 公网部署（使用 Nginx 反向代理）

假设域名: example.com
Nginx 配置了反向代理和 SSL

```json
{
  "backend": {
    "host": "127.0.0.1",
    "port": 8000,
    "public_url": "https://api.example.com"
  },
  "frontend": {
    "host": "127.0.0.1",
    "port": 5173,
    "public_url": "https://example.com",
    "api_url": "https://api.example.com"
  }
}
```

## 常见问题

### Q: host 应该用 0.0.0.0 还是 127.0.0.1？

A: 
- 如果只在本机访问: 使用 `127.0.0.1`
- 如果需要局域网或公网访问: 使用 `0.0.0.0`
- 推荐使用 `0.0.0.0` 以获得最大灵活性

### Q: public_url 和 api_url 有什么区别？

A:
- `public_url`: 用于显示和日志输出，告诉用户访问地址
- `api_url`: 前端实际使用的后端地址，必须是浏览器能访问到的

### Q: 为什么 api_url 不能用 0.0.0.0？

A: `0.0.0.0` 是一个特殊地址，表示"监听所有网卡"，但不是一个可访问的地址。浏览器无法连接到 `0.0.0.0`，必须使用实际的 IP 地址或域名。

### Q: 修改配置后需要重启吗？

A: 是的，修改 `config.json` 后需要重启服务：
```bash
python stop.py
python start.py
```

### Q: 如何验证配置是否正确？

A:
1. 启动服务: `python start.py`
2. 查看输出的访问地址
3. 在浏览器中访问前端地址
4. 检查前端是否能正常连接后端（查看浏览器控制台）
