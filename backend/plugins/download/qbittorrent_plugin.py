from typing import List
from base_plugin import DownloadPlugin
from models import ConfigField, DownloadTask
from logger import get_logger
import httpx

logger = get_logger(__name__)

class QBittorrentDownloadPlugin(DownloadPlugin):
    
    @property
    def name(self) -> str:
        return "qbittorrent"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "qBittorrent 下载插件，支持 BT/磁力链接"
    
    @property
    def supported_protocols(self) -> List[str]:
        return ["magnet", "torrent"]
    
    def get_config_schema(self) -> List[ConfigField]:
        return [
            ConfigField(
                name="host",
                label="qBittorrent 地址",
                type="text",
                default="http://localhost:8080",
                required=True
            ),
            ConfigField(
                name="username",
                label="用户名",
                type="text",
                default="admin",
                required=True
            ),
            ConfigField(
                name="password",
                label="密码",
                type="password",
                required=True
            ),
            ConfigField(
                name="download_path",
                label="下载路径",
                type="text",
                default="/downloads/torrents"
            ),
            ConfigField(
                name="category",
                label="分类",
                type="text",
                default=""
            )
        ]
    
    async def download(self, task: DownloadTask) -> bool:
        host = self.config.get('host', 'http://localhost:8080')
        
        # 获取数据库实例
        from database import get_database
        db = get_database()
        
        logger.info(f"[qBittorrent] 开始下载任务: {task.title}")
        logger.debug(f"[qBittorrent] 任务ID: {task.id}")
        logger.debug(f"[qBittorrent] URL: {task.url}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                login_response = await client.post(
                    f"{host}/api/v2/auth/login",
                    data={
                        "username": self.config.get('username', 'admin'),
                        "password": self.config.get('password', '')
                    }
                )
                
                if login_response.status_code != 200:
                    logger.error(f"[qBittorrent] 登录失败")
                    db.update_task(task.id, {'status': 'failed'})
                    return False
                
                add_response = await client.post(
                    f"{host}/api/v2/torrents/add",
                    data={
                        "urls": task.url,
                        "savepath": self.config.get('download_path', '/downloads/torrents'),
                        "category": self.config.get('category', '')
                    }
                )
                
                if add_response.status_code == 200:
                    logger.info(f"[qBittorrent] ✓ 下载任务添加成功: {task.id}")
                    db.update_task(task.id, {'status': 'downloading'})
                    return True
                else:
                    logger.error(f"[qBittorrent] 添加任务失败: {add_response.status_code}")
                    db.update_task(task.id, {'status': 'failed'})
                    return False
                    
            except Exception as e:
                logger.error(f"[qBittorrent] ✗ 下载异常: {e}", exc_info=True)
                db.update_task(task.id, {'status': 'failed'})
                return False
    
    async def get_progress(self, torrent_hash: str) -> dict:
        """获取下载进度
        
        Args:
            torrent_hash: qBittorrent的种子hash
            
        Returns:
            dict: {'progress': float, 'status': str, 'error': str}
        """
        host = self.config.get('host', 'http://localhost:8080')
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 登录
                await client.post(
                    f"{host}/api/v2/auth/login",
                    data={
                        "username": self.config.get('username', 'admin'),
                        "password": self.config.get('password', '')
                    }
                )
                
                # 获取种子信息
                response = await client.get(
                    f"{host}/api/v2/torrents/info",
                    params={"hashes": torrent_hash}
                )
                
                if response.status_code == 200:
                    torrents = response.json()
                    if torrents:
                        torrent = torrents[0]
                        progress = torrent.get('progress', 0.0) * 100
                        state = torrent.get('state', 'unknown')
                        
                        # 映射qBittorrent状态
                        status_map = {
                            'downloading': 'downloading',
                            'uploading': 'completed',
                            'pausedDL': 'paused',
                            'pausedUP': 'completed',
                            'error': 'failed',
                            'missingFiles': 'failed',
                            'queuedDL': 'pending',
                            'queuedUP': 'completed'
                        }
                        
                        status = status_map.get(state, 'downloading')
                        
                        return {
                            'progress': progress,
                            'status': status,
                            'error': None
                        }
                        
        except Exception as e:
            logger.error(f"[qBittorrent] 获取进度失败: {e}")
        
        return {'progress': 0.0, 'status': 'unknown', 'error': None}
    
    async def cancel(self, torrent_hash: str) -> bool:
        """取消/删除下载任务
        
        Args:
            torrent_hash: qBittorrent的种子hash
            
        Returns:
            bool: 是否成功取消
        """
        host = self.config.get('host', 'http://localhost:8080')
        
        logger.info(f"[qBittorrent] 取消任务: {torrent_hash}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 登录
                await client.post(
                    f"{host}/api/v2/auth/login",
                    data={
                        "username": self.config.get('username', 'admin'),
                        "password": self.config.get('password', '')
                    }
                )
                
                # 删除种子
                response = await client.post(
                    f"{host}/api/v2/torrents/delete",
                    data={
                        "hashes": torrent_hash,
                        "deleteFiles": "true"
                    }
                )
                
                if response.status_code == 200:
                    logger.info(f"[qBittorrent] ✓ 任务取消成功: {torrent_hash}")
                    return True
                else:
                    logger.error(f"[qBittorrent] 取消任务失败: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"[qBittorrent] ✗ 取消任务异常: {e}", exc_info=True)
            return False
    
    async def get_downloads(self) -> list:
        """获取qBittorrent平台的所有下载记录"""
        host = self.config.get('host', 'http://localhost:8080')
        
        logger.debug(f"[qBittorrent] 获取下载列表")
        
        downloads = []
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 登录
                login_response = await client.post(
                    f"{host}/api/v2/auth/login",
                    data={
                        "username": self.config.get('username', 'admin'),
                        "password": self.config.get('password', '')
                    }
                )
                
                if login_response.status_code != 200:
                    logger.error(f"[qBittorrent] 登录失败")
                    return downloads
                
                # 获取所有种子
                response = await client.get(f"{host}/api/v2/torrents/info")
                
                if response.status_code == 200:
                    torrents = response.json()
                    
                    for torrent in torrents:
                        # 映射状态
                        state = torrent.get('state', 'unknown')
                        status = self._map_status(state)
                        
                        # 计算进度（qBittorrent返回0-1的小数）
                        progress = torrent.get('progress', 0.0) * 100
                        
                        # 格式化速度
                        speed = self._format_speed(torrent.get('dlspeed', 0))
                        
                        # 格式化ETA
                        eta = self._format_eta(torrent.get('eta', 0))
                        
                        downloads.append({
                            'id': torrent.get('hash'),
                            'platform': self.name,
                            'title': torrent.get('name', '未知标题'),
                            'url': torrent.get('magnet_uri', ''),
                            'status': status,
                            'progress': progress,
                            'speed': speed,
                            'eta': eta,
                            'created_at': torrent.get('added_on')  # Unix时间戳
                        })
                    
                    logger.info(f"[qBittorrent] 获取到 {len(downloads)} 条下载记录")
                else:
                    logger.error(f"[qBittorrent] 获取下载列表失败: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"[qBittorrent] 获取下载列表异常: {e}", exc_info=True)
        
        return downloads
    
    def _map_status(self, qb_state: str) -> str:
        """映射qBittorrent状态到统一状态"""
        status_map = {
            'downloading': 'downloading',
            'uploading': 'completed',
            'pausedDL': 'paused',
            'pausedUP': 'completed',
            'stalledDL': 'downloading',
            'stalledUP': 'completed',
            'queuedDL': 'pending',
            'queuedUP': 'completed',
            'checkingDL': 'downloading',
            'checkingUP': 'completed',
            'error': 'failed',
            'missingFiles': 'failed',
            'allocating': 'pending'
        }
        return status_map.get(qb_state, 'downloading')
    
    def _format_speed(self, speed_bytes: int) -> str:
        """格式化速度（字节/秒 -> 可读格式）"""
        if speed_bytes == 0:
            return ''
        
        units = ['B/s', 'KB/s', 'MB/s', 'GB/s']
        unit_index = 0
        speed = float(speed_bytes)
        
        while speed >= 1024 and unit_index < len(units) - 1:
            speed /= 1024
            unit_index += 1
        
        return f"{speed:.1f} {units[unit_index]}"
    
    def _format_eta(self, eta_seconds: int) -> str:
        """格式化ETA（秒 -> 可读格式）"""
        if eta_seconds <= 0 or eta_seconds == 8640000:  # 8640000 表示无限大
            return ''
        
        hours = eta_seconds // 3600
        minutes = (eta_seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def get_web_ui_url(self) -> str:
        """获取qBittorrent的Web UI地址"""
        return self.config.get('host', 'http://localhost:8080')
