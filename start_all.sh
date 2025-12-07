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

# 检查并安装后端依赖
echo ""
echo "检查后端依赖..."
cd backend

if [ ! -f "requirements.txt" ]; then
    echo "警告: 未找到 requirements.txt"
else
    echo "安装/更新后端依赖..."
    pip install -r requirements.txt -q
    if [ $? -eq 0 ]; then
        echo "✓ 后端依赖已就绪"
    else
        echo "✗ 后端依赖安装失败，但继续启动..."
    fi
fi

# 检查并安装插件依赖
echo ""
echo "检查插件依赖..."
PLUGIN_DEPS_INSTALLED=0

for plugin_type in search download parser; do
    plugin_dir="plugins/$plugin_type"
    if [ -d "$plugin_dir" ]; then
        for req_file in "$plugin_dir"/*_requirements.txt; do
            if [ -f "$req_file" ]; then
                echo "  安装 $(basename $req_file)..."
                pip install -r "$req_file" -q
                if [ $? -eq 0 ]; then
                    PLUGIN_DEPS_INSTALLED=$((PLUGIN_DEPS_INSTALLED + 1))
                fi
            fi
        done
    fi
done

if [ $PLUGIN_DEPS_INSTALLED -gt 0 ]; then
    echo "✓ 已安装 $PLUGIN_DEPS_INSTALLED 个插件的依赖"
else
    echo "  未找到插件依赖文件"
fi

# 启动后端
echo ""
echo "启动后端服务..."
python main.py --log-level INFO &
BACKEND_PID=$!
echo "后端 PID: $BACKEND_PID"

# 等待后端启动
sleep 3

# 检查并安装前端依赖
echo ""
echo "检查前端依赖..."
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "安装前端依赖（首次运行可能需要较长时间）..."
    npm install
    if [ $? -eq 0 ]; then
        echo "✓ 前端依赖已安装"
    else
        echo "✗ 前端依赖安装失败"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
else
    echo "✓ 前端依赖已就绪"
fi

# 启动前端
echo ""
echo "启动前端服务..."
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
