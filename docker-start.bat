@echo off
chcp 65001 >nul
echo ================================
echo JustDownload Docker 部署
echo ================================
echo.

REM 检查 Docker 是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: Docker 未安装
    echo 请先安装 Docker Desktop: https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)

REM 检查 Docker Compose 是否安装
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: Docker Compose 未安装
    echo Docker Desktop 应该已包含 Docker Compose
    pause
    exit /b 1
)

echo ✓ Docker 环境检查通过
echo.

REM 创建必要的目录
echo 创建必要的目录...
if not exist "backend\config" mkdir backend\config
if not exist "backend\data" mkdir backend\data
if not exist "backend\logs" mkdir backend\logs
echo ✓ 目录创建完成
echo.

REM 构建并启动服务
echo 构建并启动服务...
docker-compose up -d --build

if errorlevel 0 (
    echo.
    echo ================================
    echo ✓ 部署成功！
    echo ================================
    echo.
    echo 访问地址:
    echo   前端: http://localhost
    echo   后端: http://localhost:8000
    echo   API文档: http://localhost:8000/docs
    echo.
    echo 常用命令:
    echo   查看日志: docker-compose logs -f
    echo   停止服务: docker-compose down
    echo   重启服务: docker-compose restart
    echo.
) else (
    echo.
    echo ❌ 部署失败，请查看错误信息
    pause
    exit /b 1
)

pause
