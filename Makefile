.PHONY: help build up down restart logs clean backup

help:
	@echo "JustDownload Docker 管理命令"
	@echo ""
	@echo "使用方法: make [命令]"
	@echo ""
	@echo "命令列表:"
	@echo "  build      - 构建 Docker 镜像"
	@echo "  up         - 启动所有服务"
	@echo "  down       - 停止所有服务"
	@echo "  restart    - 重启所有服务"
	@echo "  logs       - 查看服务日志"
	@echo "  logs-be    - 查看后端日志"
	@echo "  logs-fe    - 查看前端日志"
	@echo "  clean      - 清理容器和镜像"
	@echo "  backup     - 备份配置和数据"
	@echo "  ps         - 查看服务状态"
	@echo "  shell-be   - 进入后端容器"
	@echo "  shell-fe   - 进入前端容器"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-be:
	docker-compose logs -f backend

logs-fe:
	docker-compose logs -f frontend

ps:
	docker-compose ps

shell-be:
	docker-compose exec backend /bin/bash

shell-fe:
	docker-compose exec frontend /bin/sh

clean:
	docker-compose down -v
	docker system prune -f

backup:
	@mkdir -p backups
	@tar -czf backups/backup-$$(date +%Y%m%d-%H%M%S).tar.gz \
		backend/config \
		backend/data \
		backend/plugins
	@echo "备份完成: backups/backup-$$(date +%Y%m%d-%H%M%S).tar.gz"

rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d
