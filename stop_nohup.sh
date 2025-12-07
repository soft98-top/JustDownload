#!/bin/bash

# 停止 nohup 启动的服务

echo "=================================================="
echo "停止所有服务"
echo "=================================================="

# 读取 PID 文件
if [ ! -f ".running_pids.json" ]; then
    echo "未找到 PID 文件，尝试通过端口查找进程..."
    
    # 读取配置
    if [ -f "config.json" ]; then
        BACKEND_PORT=$(python3 -c "import json; print(json.load(open('config.json'))['backend']['port'])" 2>/dev/null)
        FRONTEND_PORT=$(python3 -c "import json; print(json.load(open('config.json'))['frontend']['port'])" 2>/dev/null)
        
        # 通过端口查找并终止进程
        if [ ! -z "$BACKEND_PORT" ]; then
            echo "查找后端进程 (端口 ${BACKEND_PORT})..."
            BACKEND_PIDS=$(lsof -ti:${BACKEND_PORT} 2>/dev/null)
            if [ ! -z "$BACKEND_PIDS" ]; then
                echo "  终止进程: $BACKEND_PIDS"
                kill -9 $BACKEND_PIDS 2>/dev/null
            fi
        fi
        
        if [ ! -z "$FRONTEND_PORT" ]; then
            echo "查找前端进程 (端口 ${FRONTEND_PORT})..."
            FRONTEND_PIDS=$(lsof -ti:${FRONTEND_PORT} 2>/dev/null)
            if [ ! -z "$FRONTEND_PIDS" ]; then
                echo "  终止进程: $FRONTEND_PIDS"
                kill -9 $FRONTEND_PIDS 2>/dev/null
            fi
        fi
    fi
    
    # 查找所有相关进程
    echo ""
    echo "查找所有相关进程..."
    
    # 查找 Python 后端进程
    PYTHON_PIDS=$(ps aux | grep "python.*main.py" | grep -v grep | awk '{print $2}')
    if [ ! -z "$PYTHON_PIDS" ]; then
        echo "  终止 Python 进程: $PYTHON_PIDS"
        kill -9 $PYTHON_PIDS 2>/dev/null
    fi
    
    # 查找 npm/node 前端进程
    NPM_PIDS=$(ps aux | grep -E "npm.*dev|node.*vite" | grep -v grep | awk '{print $2}')
    if [ ! -z "$NPM_PIDS" ]; then
        echo "  终止 npm/node 进程: $NPM_PIDS"
        kill -9 $NPM_PIDS 2>/dev/null
    fi
    
else
    # 从 PID 文件读取
    BACKEND_PID=$(python3 -c "import json; print(json.load(open('.running_pids.json')).get('backend', ''))" 2>/dev/null)
    FRONTEND_PID=$(python3 -c "import json; print(json.load(open('.running_pids.json')).get('frontend', ''))" 2>/dev/null)
    
    # 停止后端
    if [ ! -z "$BACKEND_PID" ]; then
        echo "停止后端服务 (PID: ${BACKEND_PID})..."
        kill -9 ${BACKEND_PID} 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "  ✓ 后端已停止"
        else
            echo "  ⚠ 后端进程不存在或已停止"
        fi
    fi
    
    # 停止前端
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "停止前端服务 (PID: ${FRONTEND_PID})..."
        # 终止进程组（包括子进程）
        pkill -9 -P ${FRONTEND_PID} 2>/dev/null
        kill -9 ${FRONTEND_PID} 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "  ✓ 前端已停止"
        else
            echo "  ⚠ 前端进程不存在或已停止"
        fi
    fi
    
    # 删除 PID 文件
    rm -f .running_pids.json
    echo "  ✓ 已清理 PID 文件"
fi

echo ""
echo "验证服务已停止..."
sleep 1

# 检查端口
if [ -f "config.json" ]; then
    BACKEND_PORT=$(python3 -c "import json; print(json.load(open('config.json'))['backend']['port'])" 2>/dev/null)
    FRONTEND_PORT=$(python3 -c "import json; print(json.load(open('config.json'))['frontend']['port'])" 2>/dev/null)
    
    if netstat -tlnp 2>/dev/null | grep -q ":${BACKEND_PORT}"; then
        echo "⚠ 后端端口 ${BACKEND_PORT} 仍在使用"
    else
        echo "✓ 后端端口 ${BACKEND_PORT} 已释放"
    fi
    
    if netstat -tlnp 2>/dev/null | grep -q ":${FRONTEND_PORT}"; then
        echo "⚠ 前端端口 ${FRONTEND_PORT} 仍在使用"
    else
        echo "✓ 前端端口 ${FRONTEND_PORT} 已释放"
    fi
fi

echo ""
echo "所有服务已停止"
echo "=================================================="
