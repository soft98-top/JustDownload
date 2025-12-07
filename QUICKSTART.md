# 快速启动指南

## 环境要求

- Python 3.8+
- Node.js 16+
- pip
- npm

## 安装步骤

### 方式1：一键安装（推荐）

**Linux/Mac:**
```bash
chmod +x install_dependencies.sh
./install_dependencies.sh
```

**Windows:**
```cmd
install_dependencies.bat
```

这将自动安装：
- 后端核心依赖
- 所有插件依赖
- 前端依赖

### 方式2：手动安装

#### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 2. 安装插件依赖（可选）

```bash
# 安装jable插件依赖
pip install -r plugins/search/jable_requirements.txt

# 安装seacms插件依赖
pip install -r plugins/search/seacms_requirements.txt
```

#### 3. 安装前端依赖

```bash
cd frontend
npm install
```

## 启动服务

### 方式1：一键启动（推荐）

**Linux/Mac:**
```bash
chmod +x start_all.sh
./start_all.sh
```

**Windows:**
```cmd
start_all.bat
```

这将自动：
- 检查并安装依赖
- 启动后端服务
- 启动前端服务

### 方式2：分别启动

#### 启动后端

```bash
cd backend
python main.py
```

后端将运行在 `http://localhost:8000`

#### 启动前端

```bash
cd frontend
npm run dev
```

前端将运行在 `http://localhost:5173`

## 首次使用

1. 打开浏览器访问 `http://localhost:5173`
2. 进入"设置"页面
3. 启用需要的插件（所有插件默认禁用）
4. 配置插件参数
5. 返回"搜索"页面开始使用

## 启用插件示例

### 启用JableTV搜索插件

1. 在设置页面找到"jable"插件
2. 点击开关启用
3. 点击"展开配置"
4. 配置代理地址（如果需要）
5. 保存配置

### 启用Metube下载插件

1. 在设置页面切换到"下载插件"标签
2. 找到"metube"插件
3. 点击开关启用
4. 配置Metube服务地址
5. 保存配置

## 常见问题

### Q: 插件无法启用？
A: 检查插件的依赖是否已安装。可以手动安装插件的requirements文件：
```bash
pip install -r backend/plugins/search/jable_requirements.txt
```

### Q: 搜索没有结果？
A: 确保插件已启用且配置正确。查看后端日志获取详细错误信息。

### Q: 如何查看日志？
A: 后端日志默认输出到控制台。可以通过 `--log-level DEBUG` 参数查看详细日志：
```bash
python main.py --log-level DEBUG
```

### Q: 如何备份配置？
A: 在设置页面点击"导出配置"按钮，配置将下载为JSON文件。

## 开发模式

### 后端开发

```bash
cd backend
python main.py --log-level DEBUG --verbose
```

### 前端开发

```bash
cd frontend
npm run dev
```

前端支持热重载，修改代码后自动刷新。

## 生产部署

### 后端

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 前端

```bash
cd frontend
npm run build
```

构建产物在 `frontend/dist` 目录，可以使用nginx等服务器部署。

## 更多帮助

- 查看 `README.md` 了解项目概述
- 查看 `PROJECT_STRUCTURE.md` 了解项目结构
- 查看 `backend/plugins/README.md` 了解插件开发
- 查看 `CHANGELOG.md` 了解最新更新
