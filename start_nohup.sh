#!/bin/bash

# 使用 nohup 启动服务的脚本

echo "=================================================="
echo "启动模块化下载系统 (nohup 模式)"
echo "=================================================="

# 检查配置文件
if [ ! -f "config.json" ]; then
    echo "错误: config.json 不存在"
    echo "请先运行: cp config.json.example config.json"
    exit 1
fi

# 读取配置
BACKEND_PORT=$(python3 -c "import json; print(json.load(open('config.json'))['backend']['port'])")
FRONTEND_PORT=$(python3 -c "import json; print(json.load(open('config.json'))['frontend']['port'])")
BACKEND_HOST=$(python3 -c "import json; print(json.load(open('config.json'))['backend']['host'])")
FRONTEND_HOST=$(python3 -c "import json; print(json.load(open('config.json'))['frontend']['host'])")
API_URL=$(python3 -c "import json; print(json.load(open('config.json'))['frontend']['api_url'])")

echo ""
echo "配置信息:"
echo "  后端: ${BACKEND_HOST}:${BACKEND_PORT}"
echo "  前端: ${FRONTEND_HOST}:${FRONTEND_PORT}"
echo "  API: ${API_URL}"

# 创建日志目录
mkdir -p logs

# 生成前端环境变量
echo "VITE_API_BASE_URL=${API_URL}" > frontend/.env
echo "✓ 已生成前端环境配置"

# 启动后端
echo ""
echo "启动后端服务..."
cd backend
nohup python3 main.py --host ${BACKEND_HOST} --port ${BACKEND_PORT} --log-level INFO > ../logs/backend.log 2> ../logs/backend_error.log &
BACKEND_PID=$!
echo "  后端 PID: ${BACKEND_PID}"
cd ..

# 保存后端 PID
echo "{\"backend\": ${BACKEND_PID}" > .running_pids.json

# 等待后端启动
echo "  等待后端启动..."
sleep 3

# 启动前端
echo ""
echo "启动前端服务..."
cd frontend

# 设置环境变量并启动
export VITE_API_BASE_URL=${API_URL}
export VITE_PORT=${FRONTEND_PORT}
export VITE_HOST=${FRONTEND_HOST}

nohup npm run dev > ../logs/frontend.log 2> ../logs/frontend_error.log &
FRONTEND_PID=$!
echo "  前端 PID: ${FRONTEND_PID}"
cd ..

# 更新 PID 文件
echo "{\"backend\": ${BACKEND_PID}, \"frontend\": ${FRONTEND_PID}}" > .running_pids.json

# 等待前端启动
echo "  等待前端启动..."
sleep 5

echo ""
echo "=================================================="
echo "服务已启动"
echo "=================================================="
echo "后端 PID: ${BACKEND_PID}"
echo "前端 PID: ${FRONTEND_PID}"
echo ""
echo "访问地址:"
python3 -c "import json; c=json.load(open('config.json')); print(f\"  后端: {c['backend']['public_url']}\"); print(f\"  前端: {c['frontend']['public_url']}\")"
echo ""
echo "日志文件:"
echo "  后端: logs/backend.log, logs/backend_error.log"
echo "  前端: logs/frontend.log, logs/frontend_error.log"
echo ""
echo "管理命令:"
echo "  查看状态: python3 status.py"
echo "  查看日志: python3 logs.py all"
echo "  停止服务: python3 stop.py"
echo "  检查端口: netstat -tlnp | grep ${BACKEND_PORT}"
echo "            netstat -tlnp | grep ${FRONTEND_PORT}"
echo "=================================================="

# 检查服务是否启动成功
echo ""
echo "检查服务状态..."
sleep 2

# 检查后端端口
if netstat -tlnp 2>/dev/null | grep -q ":${BACKEND_PORT}"; then
    echo "✓ 后端端口 ${BACKEND_PORT} 已开放"
else
    echo "✗ 后端端口 ${BACKEND_PORT} 未开放，请查看日志"
fi

# 检查前端端口
if netstat -tlnp 2>/dev/null | grep -q ":${FRONTEND_PORT}"; then
    echo "✓ 前端端口 ${FRONTEND_PORT} 已开放"
else
    echo "✗ 前端端口 ${FRONTEND_PORT} 未开放，请查看日志"
    echo ""
    echo "前端可能启动失败，查看错误日志:"
    echo "  tail -20 logs/frontend_error.log"
fi

echo ""
echo "提示: 服务在后台运行，关闭终端不会停止服务"
