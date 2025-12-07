#!/bin/bash

# 检查 nohup 启动的服务状态

echo "=================================================="
echo "服务状态 (nohup 模式)"
echo "=================================================="

# 读取配置
if [ ! -f "config.json" ]; then
    echo "错误: config.json 不存在"
    exit 1
fi

BACKEND_PORT=$(python3 -c "import json; print(json.load(open('config.json'))['backend']['port'])")
FRONTEND_PORT=$(python3 -c "import json; print(json.load(open('config.json'))['frontend']['port'])")
BACKEND_URL=$(python3 -c "import json; print(json.load(open('config.json'))['backend']['public_url'])")
FRONTEND_URL=$(python3 -c "import json; print(json.load(open('config.json'))['frontend']['public_url'])")

echo ""
echo "配置信息:"
echo "  后端: ${BACKEND_URL}"
echo "  前端: ${FRONTEND_URL}"

# 检查 PID 文件
echo ""
echo "进程信息:"
if [ -f ".running_pids.json" ]; then
    BACKEND_PID=$(python3 -c "import json; print(json.load(open('.running_pids.json')).get('backend', ''))" 2>/dev/null)
    FRONTEND_PID=$(python3 -c "import json; print(json.load(open('.running_pids.json')).get('frontend', ''))" 2>/dev/null)
    
    if [ ! -z "$BACKEND_PID" ]; then
        echo "  后端 PID: ${BACKEND_PID}"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "  前端 PID: ${FRONTEND_PID}"
    fi
else
    echo "  未找到 PID 文件"
fi

# 检查端口状态（最可靠的方法）
echo ""
echo "端口状态:"

# 检查后端端口
if netstat -tlnp 2>/dev/null | grep -q ":${BACKEND_PORT}"; then
    BACKEND_PROCESS=$(netstat -tlnp 2>/dev/null | grep ":${BACKEND_PORT}" | awk '{print $7}')
    echo "  ✓ 后端端口 ${BACKEND_PORT} 开放 (${BACKEND_PROCESS})"
else
    echo "  ✗ 后端端口 ${BACKEND_PORT} 未开放"
fi

# 检查前端端口
if netstat -tlnp 2>/dev/null | grep -q ":${FRONTEND_PORT}"; then
    FRONTEND_PROCESS=$(netstat -tlnp 2>/dev/null | grep ":${FRONTEND_PORT}" | awk '{print $7}')
    echo "  ✓ 前端端口 ${FRONTEND_PORT} 开放 (${FRONTEND_PROCESS})"
else
    echo "  ✗ 前端端口 ${FRONTEND_PORT} 未开放"
fi

# 检查 HTTP 响应
echo ""
echo "HTTP 响应:"

# 检查后端
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:${BACKEND_PORT}/ 2>/dev/null | grep -q "200"; then
    echo "  ✓ 后端 HTTP 响应正常"
else
    echo "  ✗ 后端 HTTP 无响应"
fi

# 检查前端
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:${FRONTEND_PORT}/ 2>/dev/null | grep -q "200"; then
    echo "  ✓ 前端 HTTP 响应正常"
else
    echo "  ✗ 前端 HTTP 无响应"
fi

# 显示相关进程
echo ""
echo "相关进程:"
ps aux | grep -E "python.*main.py|npm.*dev|node.*vite" | grep -v grep | awk '{printf "  PID: %-8s CPU: %-5s MEM: %-5s CMD: %s\n", $2, $3"%", $4"%", substr($0, index($0,$11))}'

# 日志文件信息
echo ""
echo "日志文件:"
if [ -f "logs/backend.log" ]; then
    BACKEND_LOG_SIZE=$(du -h logs/backend.log | awk '{print $1}')
    BACKEND_LOG_LINES=$(wc -l < logs/backend.log)
    echo "  后端日志: logs/backend.log (${BACKEND_LOG_SIZE}, ${BACKEND_LOG_LINES} 行)"
fi

if [ -f "logs/frontend.log" ]; then
    FRONTEND_LOG_SIZE=$(du -h logs/frontend.log | awk '{print $1}')
    FRONTEND_LOG_LINES=$(wc -l < logs/frontend.log)
    echo "  前端日志: logs/frontend.log (${FRONTEND_LOG_SIZE}, ${FRONTEND_LOG_LINES} 行)"
fi

echo ""
echo "=================================================="
echo "提示:"
echo "  查看日志: python3 logs.py all"
echo "  停止服务: ./stop_nohup.sh"
echo "  重启服务: ./stop_nohup.sh && ./start_nohup.sh"
echo "=================================================="
