#!/bin/bash

# 安装所有依赖的脚本

echo "================================"
echo "安装 JustDownload 依赖"
echo "================================"

# 检查是否在正确的目录
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 安装后端核心依赖
echo ""
echo "1. 安装后端核心依赖..."
cd backend

if [ ! -f "requirements.txt" ]; then
    echo "✗ 未找到 requirements.txt"
    exit 1
fi

pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✓ 后端核心依赖安装成功"
else
    echo "✗ 后端核心依赖安装失败"
    exit 1
fi

# 安装插件依赖
echo ""
echo "2. 安装插件依赖..."
PLUGIN_COUNT=0
SUCCESS_COUNT=0

for plugin_type in search download parser; do
    plugin_dir="plugins/$plugin_type"
    if [ -d "$plugin_dir" ]; then
        for req_file in "$plugin_dir"/*_requirements.txt; do
            if [ -f "$req_file" ]; then
                PLUGIN_COUNT=$((PLUGIN_COUNT + 1))
                plugin_name=$(basename "$req_file" | sed 's/_requirements.txt//')
                echo "  安装 $plugin_type/$plugin_name 依赖..."
                pip install -r "$req_file"
                if [ $? -eq 0 ]; then
                    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
                    echo "  ✓ $plugin_name 依赖安装成功"
                else
                    echo "  ✗ $plugin_name 依赖安装失败"
                fi
            fi
        done
    fi
done

if [ $PLUGIN_COUNT -eq 0 ]; then
    echo "  未找到插件依赖文件"
else
    echo "✓ 插件依赖安装完成: $SUCCESS_COUNT/$PLUGIN_COUNT 成功"
fi

# 安装前端依赖
echo ""
echo "3. 安装前端依赖..."
cd ../frontend

if [ ! -f "package.json" ]; then
    echo "✗ 未找到 package.json"
    exit 1
fi

npm install
if [ $? -eq 0 ]; then
    echo "✓ 前端依赖安装成功"
else
    echo "✗ 前端依赖安装失败"
    exit 1
fi

echo ""
echo "================================"
echo "依赖安装完成！"
echo "================================"
echo ""
echo "现在可以运行以下命令启动服务:"
echo "  ./start_all.sh        (Linux/Mac)"
echo "  start_all.bat         (Windows)"
echo ""
echo "或分别启动:"
echo "  后端: cd backend && python main.py"
echo "  前端: cd frontend && npm run dev"
echo "================================"
