# Git 仓库设置完成

## 当前状态

✅ Git 仓库已初始化  
✅ 远程仓库已配置: `git@github.com:soft98-top/JustDownload.git`  
✅ 初始提交已完成  
✅ .gitignore 已配置  

## 推送到远程仓库

### 首次推送

```bash
git push -u origin main
```

### 后续推送

```bash
git push
```

## 配置说明

### .gitignore 规则

已忽略以下内容：
- Python 缓存和虚拟环境
- Node.js 依赖和构建产物
- IDE 配置文件
- 日志文件
- **配置文件** (`backend/config/plugins.json`, `config/plugins.json`)
- **数据库文件** (`*.db`)
- 临时文档文件

### 配置文件管理

实际配置文件不会被提交到 Git，但提供了示例配置：
- `backend/config/plugins.json.example` - 插件配置示例

首次使用时，复制示例配置：
```bash
cp backend/config/plugins.json.example backend/config/plugins.json
```

然后根据实际情况修改配置。

## 常用 Git 命令

### 查看状态
```bash
git status
```

### 添加文件
```bash
git add .
```

### 提交更改
```bash
git commit -m "描述你的更改"
```

### 查看提交历史
```bash
git log --oneline
```

### 查看远程仓库
```bash
git remote -v
```

### 拉取最新代码
```bash
git pull origin main
```

## 分支管理

### 创建新分支
```bash
git checkout -b feature/new-feature
```

### 切换分支
```bash
git checkout main
```

### 合并分支
```bash
git checkout main
git merge feature/new-feature
```

## 注意事项

1. **配置文件安全**
   - 不要提交包含敏感信息的配置文件
   - API 密钥、密码等应该使用环境变量或单独的配置文件

2. **数据库文件**
   - 数据库文件不会被提交
   - 每个环境应该有自己的数据库

3. **文档文件**
   - 临时文档（*_FIX.md, *_SUMMARY.md 等）不会被提交
   - 重要文档已经提交到仓库

4. **提交信息**
   - 使用清晰的提交信息
   - 遵循约定式提交规范

## 协作开发

### Fork 工作流

1. Fork 仓库到自己的账号
2. Clone 到本地
3. 创建功能分支
4. 提交更改
5. 推送到自己的 Fork
6. 创建 Pull Request

### 代码审查

- 所有更改应该通过 Pull Request
- 至少一个人审查后才能合并
- 确保测试通过

## 问题排查

### SSH 密钥问题

如果推送时提示权限错误：

1. 检查 SSH 密钥是否已添加到 GitHub
```bash
ssh -T git@github.com
```

2. 如果没有 SSH 密钥，生成一个：
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

3. 将公钥添加到 GitHub：
   - 复制 `~/.ssh/id_ed25519.pub` 的内容
   - 在 GitHub Settings > SSH and GPG keys 中添加

### HTTPS 替代方案

如果 SSH 有问题，可以使用 HTTPS：

```bash
git remote set-url origin https://github.com/soft98-top/JustDownload.git
```

## 下一步

1. 推送代码到 GitHub：
   ```bash
   git push -u origin main
   ```

2. 在 GitHub 上查看仓库

3. 设置仓库描述和主题

4. 添加 README 徽章（可选）

5. 配置 GitHub Actions（可选）
