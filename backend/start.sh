#!/bin/bash

# 模块化下载系统启动脚本

# 默认启动（INFO级别日志）
# python main.py

# 详细日志模式（DEBUG级别）
# python main.py --verbose

# 指定日志级别
# python main.py --log-level DEBUG

# 自定义端口
# python main.py --port 8080

# 完整示例：详细日志 + 自定义端口
python main.py --verbose --port 8000 --host 0.0.0.0
