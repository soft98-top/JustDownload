from typing import List, Optional
from base_plugin import DownloadPlugin
from models import ConfigField, DownloadTask
from logger import get_logger
import httpx
import asyncio
import json

logger = get_logger(__name__)

class MetubeDownloadPlugin(DownloadPlugin):
    
    @property
    def name(self) -> str:
        return "metube"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Metube 下载插件，支持 YouTube、m3u8 等"
    
    @property
    def supported_protocols(self) -> List[str]:
        return ["http", "https", "m3u8"]
    
    def get_config_schema(self) -> List[ConfigField]:
        return [
            ConfigField(
                name="metube_url",
                label="Metube 服务地址",
                type="text",
                default="http://localhost:8081",
                required=True,
                description="Metube API 地址"
            ),
            ConfigField(
                name="default_quality",
                label="默认画质",
                type="select",
                options=["best", "1080p", "720p", "480p"],
                default="best"
            ),
            ConfigField(
                name="download_path",
                label="下载路径",
                type="text",
                default="/downloads",
                required=True
            )
        ]
    
    async def download(self, task: DownloadTask) -> bool:
        # 获取Metube URL并移除末尾的斜杠
        metube_url = self.config.get('metube_url', 'http://localhost:8081').rstrip('/')
        
        logger.info(f"[Metube] 开始下载任务: {task.title}")
        logger.debug(f"[Metube] 任务ID: {task.id}")
        logger.debug(f"[Metube] URL: {task.url}")
        logger.debug(f"[Metube] Metube服务地址: {metube_url}")
        
        # 获取数据库实例
        from database import get_database
        db = get_database()
        
        # 配置httpx客户端，禁用代理
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, trust_env=False) as client:
            try:
                # 生成文件名：时间戳_视频名称
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                # 清理文件名中的非法字符
                safe_title = "".join(c for c in task.title if c.isalnum() or c in (' ', '-', '_', '.')).strip()
                custom_filename = f"{timestamp}_{safe_title}"
                
                # 构建payload - Metube API格式
                payload = {
                    "url": task.url,
                    "quality": self.config.get('default_quality', 'best'),
                    "custom_name_prefix": custom_filename  # 自定义文件名
                }
                
                # 如果配置了下载路径，添加folder参数
                download_path = self.config.get('download_path', '')
                if download_path and download_path != '/downloads':
                    payload["folder"] = download_path
                
                logger.debug(f"[Metube] 自定义文件名: {custom_filename}")
                
                logger.debug(f"[Metube] 请求payload: {payload}")
                logger.debug(f"[Metube] 请求URL: {metube_url}/add")
                
                # 发送POST请求
                response = await client.post(
                    f"{metube_url}/add",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                logger.debug(f"[Metube] 响应状态码: {response.status_code}")
                logger.debug(f"[Metube] 响应头: {dict(response.headers)}")
                
                # 记录完整响应内容
                response_text = response.text
                logger.debug(f"[Metube] 响应内容（完整）: {response_text}")
                
                # 检查HTTP状态码
                if response.status_code != 200:
                    logger.error(f"[Metube] HTTP错误: {response.status_code}")
                    logger.error(f"[Metube] 响应内容: {response_text}")
                    return False
                
                # 尝试解析JSON响应
                try:
                    result = response.json()
                    logger.debug(f"[Metube] JSON响应: {result}")
                    
                    # 检查status字段
                    status = result.get('status')
                    if status == 'error':
                        error_msg = result.get('msg', '未知错误')
                        logger.error(f"[Metube] 下载失败: {error_msg}")
                        
                        # 提供更友好的错误提示
                        if 'Unable to download' in error_msg:
                            logger.error(f"[Metube] 提示: 视频源可能不可访问或需要特殊处理")
                        elif 'Connection' in error_msg:
                            logger.error(f"[Metube] 提示: 网络连接问题，请检查Metube服务器的网络")
                        
                        return False
                    
                    elif status == 'ok' or status == 'success':
                        logger.info(f"[Metube] ✓ 下载任务添加成功: {task.id}")
                        
                        # Metube 的 /add 接口通常不直接返回任务 ID
                        # 我们使用 URL 作为标识符，稍后通过 /history 查询实际 ID
                        metube_id = result.get('id', task.url)
                        
                        # 如果没有返回 ID，等待一下然后查询
                        if metube_id == task.url:
                            logger.debug(f"[Metube] 未返回任务ID，等待后查询...")
                            await asyncio.sleep(1)  # 等待任务出现在队列中
                            
                            # 通过 URL 查询任务 ID
                            progress_info = await self.get_progress(task.url)
                            if progress_info.get('status') != 'unknown':
                                # 从 /history 响应中获取实际的任务 ID
                                # 注意：我们需要再次查询以获取完整信息
                                try:
                                    history_response = await client.get(f"{metube_url}/history")
                                    if history_response.status_code == 200:
                                        history_data = history_response.json()
                                        for download in history_data.get('queue', []):
                                            if download.get('url') == task.url:
                                                metube_id = download.get('id', task.url)
                                                logger.info(f"[Metube] 查询到任务ID: {metube_id}")
                                                break
                                except Exception as e:
                                    logger.warning(f"[Metube] 查询任务ID失败: {e}")
                        
                        logger.info(f"[Metube] Metube任务标识: {metube_id}")
                        
                        # 合并现有metadata
                        metadata = task.metadata.copy() if task.metadata else {}
                        metadata['metube_id'] = metube_id
                        
                        db.update_task(task.id, {
                            'status': 'downloading',
                            'metadata': metadata
                        })
                        return True
                    
                    else:
                        # 没有明确的status字段，检查是否有错误信息
                        if 'error' in result or 'msg' in result:
                            logger.warning(f"[Metube] 响应包含可能的错误: {result}")
                        
                        # 如果没有明确的错误，认为成功
                        logger.info(f"[Metube] 下载任务已提交: {task.id}")
                        
                        # 使用 URL 作为标识符
                        metadata = task.metadata.copy() if task.metadata else {}
                        metadata['metube_id'] = task.url
                        
                        db.update_task(task.id, {
                            'status': 'downloading',
                            'metadata': metadata
                        })
                        return True
                
                except ValueError as e:
                    # 不是JSON响应
                    logger.warning(f"[Metube] 响应不是JSON格式: {e}")
                    logger.debug(f"[Metube] 原始响应: {response_text[:500]}")
                    
                    # 检查响应内容是否包含错误关键词
                    if 'error' in response_text.lower() or 'fail' in response_text.lower():
                        logger.error(f"[Metube] 响应包含错误信息")
                        return False
                    
                    # 如果HTTP 200且没有明显错误，认为成功
                    logger.info(f"[Metube] 任务已提交（非JSON响应）: {task.id}")
                    
                    # 使用 URL 作为标识符
                    metadata = task.metadata.copy() if task.metadata else {}
                    metadata['metube_id'] = task.url
                    
                    db.update_task(task.id, {
                        'status': 'downloading',
                        'metadata': metadata
                    })
                    return True
                    
            except httpx.TimeoutException as e:
                logger.error(f"[Metube] ✗ 请求超时: {e}")
                logger.error(f"[Metube] 提示: 增加超时时间或检查网络")
                db.update_task(task.id, {'status': 'failed'})
                return False
            
            except httpx.ConnectError as e:
                logger.error(f"[Metube] ✗ 连接失败: {e}")
                logger.error(f"[Metube] 提示: 请检查Metube服务是否运行在 {metube_url}")
                logger.error(f"[Metube] 提示: 可以访问 {metube_url} 验证服务状态")
                db.update_task(task.id, {'status': 'failed'})
                return False
            
            except Exception as e:
                logger.error(f"[Metube] ✗ 下载异常: {e}", exc_info=True)
                db.update_task(task.id, {'status': 'failed'})
                return False
    
    async def get_progress(self, metube_id: str) -> dict:
        """获取下载进度和状态（通过 /history API）
        
        Args:
            metube_id: Metube平台的任务ID（可能是URL）
            
        Returns:
            dict: {'progress': float, 'status': str, 'error': str, 'where': str}
        """
        metube_url = self.config.get('metube_url', 'http://localhost:8081').rstrip('/')
        
        logger.debug(f"[Metube] 查询任务进度: {metube_id}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
                # 使用 /history 接口查询所有任务
                response = await client.get(f"{metube_url}/history")
                if response.status_code == 200:
                    data = response.json()
                    
                    # 检查队列中的任务（正在下载或等待中）
                    queue = data.get('queue', [])
                    for download in queue:
                        # 匹配 ID 或 URL
                        if download.get('id') == metube_id or download.get('url') == metube_id:
                            # Metube 的 percent 字段是百分比（0-100），但可能是 null
                            progress = download.get('percent')
                            if progress is None:
                                progress = 0.0
                            
                            # 获取任务状态
                            task_status = download.get('status', 'downloading')
                            
                            # 根据状态判断
                            if task_status == 'pending':
                                status = 'pending'
                            elif task_status == 'downloading':
                                status = 'downloading'
                            else:
                                status = 'downloading'
                            
                            logger.debug(f"[Metube] 任务 {metube_id} 状态: {task_status}, 进度: {progress:.1f}%")
                            
                            return {
                                'progress': progress,
                                'status': status,
                                'error': None,
                                'speed': download.get('speed') or '',
                                'eta': download.get('eta') or '',
                                'where': 'queue',  # 标记任务位置，用于删除
                                'title': download.get('title', '')
                            }
                    
                    # 检查已完成的任务
                    done = data.get('done', [])
                    for download in done:
                        if download.get('id') == metube_id or download.get('url') == metube_id:
                            logger.debug(f"[Metube] 任务 {metube_id} 已完成")
                            return {
                                'progress': 100.0,
                                'status': 'completed',
                                'error': None,
                                'speed': '',
                                'eta': '',
                                'where': 'done',
                                'title': download.get('title', '')
                            }
                    
                    # 任务不在任何列表中，可能已被删除或未找到
                    logger.warning(f"[Metube] 未找到任务: {metube_id}")
                    return {
                        'progress': 0.0,
                        'status': 'unknown',
                        'error': 'Task not found in Metube',
                        'speed': '',
                        'eta': '',
                        'where': None
                    }
                else:
                    logger.error(f"[Metube] API 请求失败: {response.status_code}")
                            
        except Exception as e:
            logger.error(f"[Metube] 获取进度失败: {e}", exc_info=True)
        
        return {
            'progress': 0.0,
            'status': 'unknown',
            'error': 'Failed to fetch progress',
            'speed': '',
            'eta': '',
            'where': None
        }
    
    async def cancel(self, metube_id: str) -> bool:
        """取消/删除下载任务
        
        Args:
            metube_id: Metube平台的任务ID（可能是URL）
            
        Returns:
            bool: 是否成功取消
        """
        metube_url = self.config.get('metube_url', 'http://localhost:8081').rstrip('/')
        
        logger.info(f"[Metube] 取消任务: {metube_id}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
                # 首先查询任务在哪个列表中（queue 或 done）
                progress_info = await self.get_progress(metube_id)
                where = progress_info.get('where', 'queue')
                
                if where is None:
                    logger.warning(f"[Metube] 任务不存在，无法取消: {metube_id}")
                    return False
                
                # 使用正确的 Payload 格式删除任务
                # 必须包含 ids（列表）和 where（'queue' 或 'done'）
                payload = {
                    "ids": [metube_id],
                    "where": where
                }
                
                logger.debug(f"[Metube] 删除请求: {payload}")
                
                response = await client.post(
                    f"{metube_url}/delete",
                    json=payload
                )
                
                if response.status_code == 200:
                    logger.info(f"[Metube] ✓ 任务取消成功: {metube_id} (from {where})")
                    return True
                else:
                    logger.error(f"[Metube] 取消任务失败: {response.status_code}")
                    logger.error(f"[Metube] 响应内容: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"[Metube] ✗ 取消任务异常: {e}", exc_info=True)
            return False
    
    async def get_downloads(self) -> list:
        """获取Metube平台的所有下载记录"""
        metube_url = self.config.get('metube_url', 'http://localhost:8081').rstrip('/')
        
        logger.debug(f"[Metube] 获取下载列表")
        
        downloads = []
        
        try:
            async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
                response = await client.get(f"{metube_url}/history")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 处理队列中的任务（正在下载或等待）
                    for download in data.get('queue', []):
                        downloads.append({
                            'id': download.get('id', download.get('url')),
                            'platform': self.name,
                            'title': download.get('title', '未知标题'),
                            'url': download.get('url', ''),
                            'status': self._map_status(download.get('status', 'downloading')),
                            'progress': download.get('percent') or 0.0,
                            'speed': download.get('speed', ''),
                            'eta': download.get('eta', ''),
                            'created_at': None  # Metube不提供创建时间
                        })
                    
                    # 处理已完成的任务
                    for download in data.get('done', []):
                        downloads.append({
                            'id': download.get('id', download.get('url')),
                            'platform': self.name,
                            'title': download.get('title', '未知标题'),
                            'url': download.get('url', ''),
                            'status': 'completed',
                            'progress': 100.0,
                            'speed': '',
                            'eta': '',
                            'created_at': None
                        })
                    
                    logger.info(f"[Metube] 获取到 {len(downloads)} 条下载记录")
                else:
                    logger.error(f"[Metube] 获取下载列表失败: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"[Metube] 获取下载列表异常: {e}", exc_info=True)
        
        return downloads
    
    def _map_status(self, metube_status: str) -> str:
        """映射Metube状态到统一状态"""
        status_map = {
            'pending': 'pending',
            'downloading': 'downloading',
            'finished': 'completed',
            'error': 'failed'
        }
        return status_map.get(metube_status, 'downloading')
    
    def get_web_ui_url(self) -> str:
        """获取Metube的Web UI地址"""
        return self.config.get('metube_url', 'http://localhost:8081').rstrip('/')
