"""
数据库模块
使用 SQLite 存储下载任务
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from logger import get_logger

logger = get_logger(__name__)


class Database:
    """数据库管理类"""
    
    def __init__(self, db_path: str = "data/downloads.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建下载任务表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS download_tasks (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        url TEXT NOT NULL,
                        status TEXT NOT NULL,
                        progress REAL DEFAULT 0.0,
                        plugin_name TEXT NOT NULL,
                        save_path TEXT,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 创建索引
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_status 
                    ON download_tasks(status)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_created_at 
                    ON download_tasks(created_at DESC)
                """)
                
                conn.commit()
                logger.info(f"数据库初始化成功: {self.db_path}")
                
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}", exc_info=True)
    
    def add_task(self, task: Dict[str, Any]) -> bool:
        """添加下载任务"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO download_tasks 
                    (id, title, url, status, progress, plugin_name, save_path, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    task['id'],
                    task['title'],
                    task['url'],
                    task['status'],
                    task.get('progress', 0.0),
                    task['plugin_name'],
                    task.get('save_path', ''),
                    json.dumps(task.get('metadata', {}))
                ))
                
                conn.commit()
                logger.info(f"任务已添加: {task['id']} - {task['title']}")
                return True
                
        except Exception as e:
            logger.error(f"添加任务失败: {e}", exc_info=True)
            return False
    
    def get_all_tasks(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取所有任务"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM download_tasks 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,))
                
                rows = cursor.fetchall()
                tasks = []
                
                for row in rows:
                    task = dict(row)
                    # 解析 metadata JSON
                    if task['metadata']:
                        try:
                            task['metadata'] = json.loads(task['metadata'])
                        except:
                            task['metadata'] = {}
                    else:
                        task['metadata'] = {}
                    tasks.append(task)
                
                return tasks
                
        except Exception as e:
            logger.error(f"获取任务列表失败: {e}", exc_info=True)
            return []
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取单个任务"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM download_tasks WHERE id = ?
                """, (task_id,))
                
                row = cursor.fetchone()
                if row:
                    task = dict(row)
                    if task['metadata']:
                        try:
                            task['metadata'] = json.loads(task['metadata'])
                        except:
                            task['metadata'] = {}
                    return task
                
                return None
                
        except Exception as e:
            logger.error(f"获取任务失败: {e}", exc_info=True)
            return None
    
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """更新任务"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 构建更新语句
                set_clauses = []
                values = []
                
                for key, value in updates.items():
                    if key == 'metadata':
                        value = json.dumps(value)
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
                
                set_clauses.append("updated_at = CURRENT_TIMESTAMP")
                values.append(task_id)
                
                sql = f"""
                    UPDATE download_tasks 
                    SET {', '.join(set_clauses)}
                    WHERE id = ?
                """
                
                cursor.execute(sql, values)
                conn.commit()
                
                logger.debug(f"任务已更新: {task_id}")
                return True
                
        except Exception as e:
            logger.error(f"更新任务失败: {e}", exc_info=True)
            return False
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM download_tasks WHERE id = ?
                """, (task_id,))
                
                conn.commit()
                logger.info(f"任务已删除: {task_id}")
                return True
                
        except Exception as e:
            logger.error(f"删除任务失败: {e}", exc_info=True)
            return False
    
    def get_tasks_by_status(self, status: str) -> List[Dict[str, Any]]:
        """根据状态获取任务"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM download_tasks 
                    WHERE status = ?
                    ORDER BY created_at DESC
                """, (status,))
                
                rows = cursor.fetchall()
                tasks = []
                
                for row in rows:
                    task = dict(row)
                    if task['metadata']:
                        try:
                            task['metadata'] = json.loads(task['metadata'])
                        except:
                            task['metadata'] = {}
                    tasks.append(task)
                
                return tasks
                
        except Exception as e:
            logger.error(f"获取任务失败: {e}", exc_info=True)
            return []


# 全局数据库实例
_db = None


def get_database() -> Database:
    """获取数据库实例（单例）"""
    global _db
    if _db is None:
        _db = Database()
    return _db
