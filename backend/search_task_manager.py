"""异步搜索任务管理器"""
import asyncio
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel
from logger import get_logger

logger = get_logger(__name__)


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"  # 等待中
    RUNNING = "running"  # 执行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败


class SearchTask(BaseModel):
    """搜索任务"""
    id: str
    plugin_name: str
    keyword: str
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: List[Dict[str, Any]] = []
    error: Optional[str] = None
    progress: int = 0  # 0-100
    progress_message: str = ""


class SearchTaskManager:
    """搜索任务管理器"""
    
    def __init__(self):
        self.tasks: Dict[str, SearchTask] = {}
        self._cleanup_task = None
        
    def start_cleanup_task(self):
        """启动清理任务"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_old_tasks())
            logger.info("搜索任务清理器已启动")
    
    async def _cleanup_old_tasks(self):
        """定期清理旧任务（保留24小时）"""
        while True:
            try:
                await asyncio.sleep(3600)  # 每小时清理一次
                now = datetime.now()
                expired_ids = []
                
                for task_id, task in self.tasks.items():
                    # 删除24小时前的任务
                    if (now - task.created_at) > timedelta(hours=24):
                        expired_ids.append(task_id)
                
                for task_id in expired_ids:
                    del self.tasks[task_id]
                    logger.debug(f"清理过期任务: {task_id}")
                
                if expired_ids:
                    logger.info(f"清理了 {len(expired_ids)} 个过期任务")
                    
            except Exception as e:
                logger.error(f"清理任务异常: {e}")
    
    def create_task(self, plugin_name: str, keyword: str) -> str:
        """创建搜索任务"""
        task_id = str(uuid.uuid4())
        task = SearchTask(
            id=task_id,
            plugin_name=plugin_name,
            keyword=keyword,
            status=TaskStatus.PENDING,
            created_at=datetime.now()
        )
        self.tasks[task_id] = task
        logger.info(f"创建搜索任务: {task_id} ({plugin_name}: {keyword})")
        return task_id
    
    def get_task(self, task_id: str) -> Optional[SearchTask]:
        """获取任务"""
        return self.tasks.get(task_id)
    
    def update_task_status(self, task_id: str, status: TaskStatus, error: Optional[str] = None):
        """更新任务状态"""
        task = self.tasks.get(task_id)
        if task:
            task.status = status
            if status == TaskStatus.RUNNING and task.started_at is None:
                task.started_at = datetime.now()
            elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                task.completed_at = datetime.now()
            if error:
                task.error = error
            logger.debug(f"任务 {task_id} 状态更新: {status}")
    
    def update_task_progress(self, task_id: str, progress: int, message: str = ""):
        """更新任务进度"""
        task = self.tasks.get(task_id)
        if task:
            task.progress = progress
            task.progress_message = message
            logger.debug(f"任务 {task_id} 进度: {progress}% - {message}")
    
    def set_task_results(self, task_id: str, results: List[Dict[str, Any]]):
        """设置任务结果"""
        task = self.tasks.get(task_id)
        if task:
            task.results = results
            logger.info(f"任务 {task_id} 完成，结果数: {len(results)}")
    
    async def execute_search(self, task_id: str, plugin, keyword: str):
        """执行搜索任务"""
        try:
            self.update_task_status(task_id, TaskStatus.RUNNING)
            self.update_task_progress(task_id, 10, "开始搜索...")
            
            # 执行搜索
            results = await plugin.search(keyword)
            
            # 转换为字典
            results_dict = [r.model_dump() for r in results]
            
            self.update_task_progress(task_id, 100, "搜索完成")
            self.set_task_results(task_id, results_dict)
            self.update_task_status(task_id, TaskStatus.COMPLETED)
            
        except Exception as e:
            logger.error(f"搜索任务 {task_id} 失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            self.update_task_status(task_id, TaskStatus.FAILED, str(e))


# 全局任务管理器实例
_task_manager: Optional[SearchTaskManager] = None


def get_task_manager() -> SearchTaskManager:
    """获取任务管理器实例"""
    global _task_manager
    if _task_manager is None:
        _task_manager = SearchTaskManager()
        _task_manager.start_cleanup_task()
    return _task_manager
