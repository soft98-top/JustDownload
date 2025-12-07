@echo off
chcp 65001 >nul
echo ==================================================
echo 模块化下载系统 - 统一启动
echo ==================================================
echo.

python start.py

if %errorlevel% neq 0 (
    echo.
    echo 启动失败，请检查错误信息
    pause
    exit /b 1
)

pause
