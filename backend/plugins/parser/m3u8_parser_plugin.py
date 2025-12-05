"""
M3U8 视频解析器插件
支持配置多个解析器地址，为M3U8链接生成解析后的播放地址
"""
from typing import List, Dict, Any
from base_plugin import ParserPlugin
from models import ConfigField
from logger import get_logger

logger = get_logger(__name__)


class M3U8ParserPlugin(ParserPlugin):
    """M3U8解析器插件"""
    
    @property
    def name(self) -> str:
        return "m3u8"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "M3U8视频解析器 - 支持配置多个解析地址"
    
    def get_config_schema(self) -> List[ConfigField]:
        return [
            ConfigField(
                name="parsers_list",
                label="解析器列表",
                type="list",
                default=[
                    {
                        "name": "P2P商业加速",
                        "parser_url": "https://mtjiexi.cc:966/?url=",
                        "enabled": True
                    }
                ],
                required=True,
                description="M3U8解析器配置列表，每个解析器包含名称、URL和启用状态",
                fields=[
                    {"name": "name", "label": "解析器名称", "type": "text", "default": ""},
                    {"name": "parser_url", "label": "解析器地址", "type": "text", "default": ""},
                    {"name": "enabled", "label": "启用", "type": "boolean", "default": True}
                ]
            )
        ]
    
    def parse_url(self, original_url: str) -> List[Dict[str, str]]:
        """为M3U8链接生成解析后的播放地址
        
        Args:
            original_url: 原始M3U8链接
            
        Returns:
            解析后的链接列表
        """
        parsers_list = self.config.get("parsers_list", [])
        parsed_urls = []
        
        # 只处理M3U8链接
        if ".m3u8" not in original_url.lower():
            return parsed_urls
        
        for parser in parsers_list:
            if not parser.get("enabled", True):
                continue
            
            parser_name = parser.get("name", "未命名解析器")
            parser_url = parser.get("parser_url", "")
            
            if parser_url:
                parsed_url = f"{parser_url}{original_url}"
                parsed_urls.append({
                    "name": parser_name,
                    "url": parsed_url
                })
                logger.debug(f"生成解析链接: {parser_name} -> {parsed_url[:50]}...")
        
        return parsed_urls
