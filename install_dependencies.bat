@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ================================
echo 安装 JustDownload 依赖
echo ================================

:: 检查是否在正确的目录
if not exist "backend" (
    echo 错误: 未找到 backend 目录
    pause
    exit /b 1
)

if not exist "frontend" (
    echo 错误: 未找到 frontend 目录
    pause
    exit /b 1
)

:: 安装后端核心依赖
echo.
echo 1. 安装后端核心依赖...
cd backend

if not exist "requirements.txt" (
    echo × 未找到 requirements.txt
    pause
    exit /b 1
)

pip install -r requirements.txt
if !errorlevel! equ 0 (
    echo √ 后端核心依赖安装成功
) else (
    echo × 后端核心依赖安装失败
    pause
    exit /b 1
)

:: 安装插件依赖
echo.
echo 2. 安装插件依赖...
set PLUGIN_COUNT=0
set SUCCESS_COUNT=0

for %%t in (search download parser) do (
    if exist "plugins\%%t" (
        for %%f in ("plugins\%%t\*_requirements.txt") do (
            set /a PLUGIN_COUNT+=1
            for %%n in ("%%~nf") do set plugin_name=%%~n
            set plugin_name=!plugin_name:_requirements=!
            echo   安装 %%t/!plugin_name! 依赖...
            pip install -r "%%f"
            if !errorlevel! equ 0 (
                set /a SUCCESS_COUNT+=1
                echo   √ !plugin_name! 依赖安装成功
            ) else (
                echo   × !plugin_name! 依赖安装失败
            )
        )
    )
)

if !PLUGIN_COUNT! equ 0 (
    echo   未找到插件依赖文件
) else (
    echo √ 插件依赖安装完成: !SUCCESS_COUNT!/!PLUGIN_COUNT! 成功
)

:: 安装前端依赖
echo.
echo 3. 安装前端依赖...
cd ..\frontend

if not exist "package.json" (
    echo × 未找到 package.json
    pause
    exit /b 1
)

call npm install
if !errorlevel! equ 0 (
    echo √ 前端依赖安装成功
) else (
    echo × 前端依赖安装失败
    pause
    exit /b 1
)

echo.
echo ================================
echo 依赖安装完成！
echo ================================
echo.
echo 现在可以运行以下命令启动服务:
echo   start_all.bat         (Windows)
echo   ./start_all.sh        (Linux/Mac)
echo.
echo 或分别启动:
echo   后端: cd backend ^&^& python main.py
echo   前端: cd frontend ^&^& npm run dev
echo ================================
echo.

pause
