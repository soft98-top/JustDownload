#!/bin/bash

# 启动前后端服务的便捷脚本

echo "================================"
echo "启动模块化下载系统"
echo "================================"

# 检查是否在正确的目录
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 启动后端
echo ""
echo "启动后端服务..."
cd backend
python main.py --log-level INFO &
BACKEND_PID=$!
echo "后端 PID: $BACKEND_PID"

# 等待后端启动
sleep 3

# 启动前端
echo ""
echo "启动前端服务..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "前端 PID: $FRONTEND_PID"

echo ""
echo "================================"
echo "服务已启动"
echo "================================"
echo "后端: http://localhost:8000"
echo "前端: http://localhost:5173"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo "================================"

# 等待用户中断
trap "echo ''; echo '停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT

# 保持脚本运行
wait
