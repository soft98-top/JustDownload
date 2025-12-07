@echo off
chcp 65001 >nul

python update_config.py %*

pause
