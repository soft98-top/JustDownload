#!/bin/bash

echo "================================"
echo "JustDownload Docker 部署"
echo "================================"
echo ""

# 检�?Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "�?错误: Docker 未安�?
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检�?Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "�?错误: Docker Compose 未安�?
    echo "请先安装 Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "�?Docker 环境检查通过"
echo ""

# 创建必要的目�?echo "创建必要的目�?.."
mkdir -p backend/config backend/data backend/logs
echo "�?目录创建完成"
echo ""

# 构建并启动服�?echo "构建并启动服�?.."
docker-compose up -d --build

if [ $? -eq 0 ]; then
    echo ""
    echo "================================"
    echo "�?部署成功�?
    echo "================================"
    echo ""
    echo "访问地址:"
    echo "  前端: http://localhost"
    echo "  后端: http://localhost:8000"
    echo "  API文档: http://localhost:8000/docs"
    echo ""
    echo "常用命令:"
    echo "  查看日志: docker-compose logs -f"
    echo "  停止服务: docker-compose down"
    echo "  重启服务: docker-compose restart"
    echo ""
else
    echo ""
    echo "�?部署失败，请查看错误信息"
    exit 1
fi
