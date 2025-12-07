@echo off
chcp 65001 >nul

python logs.py %*

if "%1"=="" pause
