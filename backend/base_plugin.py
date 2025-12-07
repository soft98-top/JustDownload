from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from models import ConfigField, SearchResult, DownloadTask
from logger import get_logger

logger = get_logger(__name__)


class BasePlugin(ABC):
    """插件基类，提供通用配置处理方法"""
    
    def __init__(self):
        self.config = {}
    
    def _get_config_int(self, key: str, default: int) -> int:
        """安全地获取整数配置值"""
        value = self.config.get(key, default)
        if value == '' or value is None:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            logger.warning(f"[{self.name}] 配置项 {key} 的值 '{value}' 无效，使用默认值 {default}")
            return default
    
    def _get_config_float(self, key: str, default: float) -> float:
        """安全地获取浮点数配置值"""
        value = self.config.get(key, default)
        if value == '' or value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            logger.warning(f"[{self.name}] 配置项 {key} 的值 '{value}' 无效，使用默认值 {default}")
            return default
    
    def _get_config_bool(self, key: str, default: bool) -> bool:
        """安全地获取布尔配置值"""
        value = self.config.get(key, default)
        if value == '' or value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)
    
    def _get_config_str(self, key: str, default: str) -> str:
        """安全地获取字符串配置值"""
        value = self.config.get(key, default)
        if value is None:
            return default
        return str(value)
    
    def set_config(self, config: Dict[str, Any]):
        """设置配置"""
        self.config = config


class ParserPlugin(BasePlugin):
    """视频解析器插件基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称（唯一标识）"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """插件版本"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """插件描述（显示给用户）"""
        pass
    
    @abstractmethod
    def get_config_schema(self) -> List[ConfigField]:
        """获取配置字段定义"""
        pass
    
    @abstractmethod
    def parse_url(self, original_url: str) -> List[Dict[str, str]]:
        """解析视频URL，返回解析后的播放链接列表
        
        Args:
            original_url: 原始视频URL
            
        Returns:
            List[Dict]: 解析后的链接列表，每项包含:
                - name: 解析器名称
                - url: 解析后的URL
        """
        pass

class SearchPlugin(BasePlugin):
    """搜索插件基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称（唯一标识）"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """插件版本"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """插件描述（显示给用户）"""
        pass
    
    @abstractmethod
    def get_config_schema(self) -> List[ConfigField]:
        """获取配置字段定义"""
        pass
    
    @abstractmethod
    async def search(self, keyword: str, **kwargs) -> List[SearchResult]:
        pass
    
    @abstractmethod
    async def get_video_info(self, url: str) -> SearchResult:
        pass

class DownloadPlugin(BasePlugin):
    """下载插件基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        pass
    
    @property
    @abstractmethod
    def supported_protocols(self) -> List[str]:
        pass
    
    @abstractmethod
    def get_config_schema(self) -> List[ConfigField]:
        pass
    
    @abstractmethod
    async def download(self, task: DownloadTask) -> bool:
        pass
    
    @abstractmethod
    async def get_progress(self, platform_id: str) -> dict:
        """获取下载进度
        
        Args:
            platform_id: 下载平台的任务ID
            
        Returns:
            dict: {'progress': float, 'status': str, 'error': str}
        """
        pass
    
    @abstractmethod
    async def cancel(self, platform_id: str) -> bool:
        """取消/删除下载任务
        
        Args:
            platform_id: 下载平台的任务ID
            
        Returns:
            bool: 是否成功取消
        """
        pass
    
    @abstractmethod
    async def get_downloads(self) -> List[Dict[str, Any]]:
        """获取该平台的所有下载记录
        
        Returns:
            List[Dict]: 下载记录列表，每条记录包含:
                - id: 平台任务ID
                - platform: 平台名称
                - title: 标题
                - url: 下载链接
                - status: 状态 (pending/downloading/completed/failed)
                - progress: 进度 (0-100)
                - speed: 下载速度（可选）
                - eta: 预计剩余时间（可选）
                - created_at: 创建时间（可选）
        """
        pass
    
    @abstractmethod
    def get_web_ui_url(self) -> str:
        """获取该平台的 Web UI 地址
        
        Returns:
            str: Web UI 地址，如 "http://localhost:8081"
        """
        pass
