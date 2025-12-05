from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from enum import Enum

class PluginType(Enum):
    SEARCH = "search"
    DOWNLOAD = "download"

class ConfigField(BaseModel):
    """插件配置字段定义"""
    name: str
    label: str
    type: str  # text, password, number, boolean, select, list
    default: Any = None
    required: bool = False
    options: List[str] = []
    description: str = ""
    fields: List[Dict[str, Any]] = []  # 用于list类型的子字段定义

class SearchResult(BaseModel):
    """搜索结果"""
    title: str
    url: str
    thumbnail: Optional[str] = None
    duration: Optional[str] = None
    platform: str
    description: Optional[str] = None  # 资源描述
    metadata: Dict[str, Any] = {}

class DownloadTask(BaseModel):
    """下载任务"""
    id: str
    url: str
    title: str
    status: str  # pending, downloading, completed, failed
    progress: float = 0.0
    plugin_name: str
    save_path: str
    metadata: Dict[str, Any] = {}
