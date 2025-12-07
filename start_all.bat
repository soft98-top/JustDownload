@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ================================
echo 启动模块化下载系统
echo ================================

:: 检查是否在正确的目录
if not exist "backend" (
    echo 错误: 未找到 backend 目录
    echo 请在项目根目录运行此脚本
    pause
    exit /b 1
)

if not exist "frontend" (
    echo 错误: 未找到 frontend 目录
    echo 请在项目根目录运行此脚本
    pause
    exit /b 1
)

:: 检查并安装后端依赖
echo.
echo 检查后端依赖...
cd backend

if not exist "requirements.txt" (
    echo 警告: 未找到 requirements.txt
) else (
    echo 安装/更新后端依赖...
    pip install -r requirements.txt -q
    if !errorlevel! equ 0 (
        echo √ 后端依赖已就绪
    ) else (
        echo × 后端依赖安装失败，但继续启动...
    )
)

:: 检查并安装插件依赖
echo.
echo 检查插件依赖...
set PLUGIN_DEPS_INSTALLED=0

for %%t in (search download parser) do (
    if exist "plugins\%%t" (
        for %%f in ("plugins\%%t\*_requirements.txt") do (
            echo   安装 %%~nxf...
            pip install -r "%%f" -q
            if !errorlevel! equ 0 (
                set /a PLUGIN_DEPS_INSTALLED+=1
            )
        )
    )
)

if !PLUGIN_DEPS_INSTALLED! gtr 0 (
    echo √ 已安装 !PLUGIN_DEPS_INSTALLED! 个插件的依赖
) else (
    echo   未找到插件依赖文件
)

:: 启动后端
echo.
echo 启动后端服务...
start "JustDownload-Backend" python main.py --log-level INFO
timeout /t 3 /nobreak >nul

:: 检查并安装前端依赖
echo.
echo 检查前端依赖...
cd ..\frontend

if not exist "node_modules" (
    echo 安装前端依赖（首次运行可能需要较长时间）...
    call npm install
    if !errorlevel! equ 0 (
        echo √ 前端依赖已安装
    ) else (
        echo × 前端依赖安装失败
        pause
        exit /b 1
    )
) else (
    echo √ 前端依赖已就绪
)

:: 启动前端
echo.
echo 启动前端服务...
start "JustDownload-Frontend" npm run dev

echo.
echo ================================
echo 服务已启动
echo ================================
echo 后端: http://localhost:8000
echo 前端: http://localhost:5173
echo.
echo 关闭此窗口将停止所有服务
echo ================================
echo.

pause
