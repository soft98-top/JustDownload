from typing import Dict, List, Any, Optional
from base_plugin import SearchPlugin, DownloadPlugin, ParserPlugin
from config_storage import get_config_storage
from logger import get_logger

logger = get_logger(__name__)

class PluginManager:
    """插件管理器"""
    
    def __init__(self):
        self.search_plugins: Dict[str, SearchPlugin] = {}
        self.download_plugins: Dict[str, DownloadPlugin] = {}
        self.parser_plugins: Dict[str, ParserPlugin] = {}
        self.config_storage = get_config_storage()
        self._migrate_old_config()
    
    def register_search_plugin(self, plugin: SearchPlugin):
        self.search_plugins[plugin.name] = plugin
        logger.info(f"✓ 注册搜索插件: {plugin.name} v{plugin.version}")
        
        # 加载保存的配置
        saved_config = self.config_storage.get("search", plugin.name)
        if saved_config:
            plugin.set_config(saved_config)
            logger.info(f"已加载插件配置: {plugin.name}")
    
    def register_download_plugin(self, plugin: DownloadPlugin):
        self.download_plugins[plugin.name] = plugin
        logger.info(f"✓ 注册下载插件: {plugin.name} v{plugin.version}")
        
        # 加载保存的配置
        saved_config = self.config_storage.get("download", plugin.name)
        if saved_config:
            plugin.set_config(saved_config)
            logger.info(f"已加载插件配置: {plugin.name}")
    
    def register_parser_plugin(self, plugin: ParserPlugin):
        self.parser_plugins[plugin.name] = plugin
        logger.info(f"✓ 注册解析器插件: {plugin.name} v{plugin.version}")
        
        # 加载保存的配置
        saved_config = self.config_storage.get("parser", plugin.name)
        if saved_config:
            plugin.set_config(saved_config)
            logger.info(f"已加载插件配置: {plugin.name}")
    
    def get_search_plugin(self, name: str) -> Optional[SearchPlugin]:
        return self.search_plugins.get(name)
    
    def get_download_plugin(self, name: str) -> Optional[DownloadPlugin]:
        return self.download_plugins.get(name)
    
    def get_parser_plugin(self, name: str) -> Optional[ParserPlugin]:
        return self.parser_plugins.get(name)
    
    def list_plugins(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "search": [
                {
                    "name": p.name,
                    "version": p.version,
                    "description": p.description,
                    "config_schema": [f.model_dump() for f in p.get_config_schema()],
                    "enabled": self.config_storage.is_enabled("search", p.name)
                }
                for p in self.search_plugins.values()
            ],
            "download": [
                {
                    "name": p.name,
                    "version": p.version,
                    "description": p.description,
                    "supported_protocols": p.supported_protocols,
                    "config_schema": [f.model_dump() for f in p.get_config_schema()],
                    "enabled": self.config_storage.is_enabled("download", p.name)
                }
                for p in self.download_plugins.values()
            ],
            "parser": [
                {
                    "name": p.name,
                    "version": p.version,
                    "description": p.description,
                    "config_schema": [f.model_dump() for f in p.get_config_schema()],
                    "enabled": self.config_storage.is_enabled("parser", p.name)
                }
                for p in self.parser_plugins.values()
            ]
        }
    
    def get_enabled_plugins(self, plugin_type: str) -> List[str]:
        """获取已启用的插件名称列表"""
        if plugin_type == "search":
            return [p.name for p in self.search_plugins.values() 
                    if self.config_storage.is_enabled("search", p.name)]
        elif plugin_type == "download":
            return [p.name for p in self.download_plugins.values() 
                    if self.config_storage.is_enabled("download", p.name)]
        elif plugin_type == "parser":
            return [p.name for p in self.parser_plugins.values() 
                    if self.config_storage.is_enabled("parser", p.name)]
        return []
    
    def set_plugin_config(self, plugin_type: str, plugin_name: str, config: Dict[str, Any]):
        if plugin_type == "search":
            plugin = self.search_plugins.get(plugin_name)
        elif plugin_type == "download":
            plugin = self.download_plugins.get(plugin_name)
        elif plugin_type == "parser":
            plugin = self.parser_plugins.get(plugin_name)
        else:
            plugin = None
        
        if plugin:
            plugin.set_config(config)
            # 持久化保存配置
            self.config_storage.set(plugin_type, plugin_name, config)
            logger.info(f"插件配置已保存: {plugin_type}/{plugin_name}")
    
    def get_suitable_download_plugin(self, url: str) -> Optional[DownloadPlugin]:
        if url.startswith("magnet:") or url.endswith(".torrent"):
            for plugin in self.download_plugins.values():
                if "magnet" in plugin.supported_protocols or "torrent" in plugin.supported_protocols:
                    return plugin
        elif ".m3u8" in url:
            for plugin in self.download_plugins.values():
                if "m3u8" in plugin.supported_protocols:
                    return plugin
        else:
            for plugin in self.download_plugins.values():
                if "http" in plugin.supported_protocols or "https" in plugin.supported_protocols:
                    return plugin
        
        return None
    
    def get_active_parsers(self) -> List[ParserPlugin]:
        """获取所有启用的解析器插件"""
        return [
            plugin for plugin in self.parser_plugins.values()
            if self.config_storage.is_enabled("parser", plugin.name)
        ]
    
    def parse_video_urls(self, episodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """为视频剧集添加解析后的播放链接
        
        Args:
            episodes: 剧集列表，每项包含 episode_name 和 play_url
            
        Returns:
            增强后的剧集列表，每项增加 parsed_urls 字段
        """
        active_parsers = self.get_active_parsers()
        logger.debug(f"活跃的解析器数量: {len(active_parsers)}")
        
        if not active_parsers:
            logger.warning("没有启用的解析器插件")
            return episodes
        
        for episode in episodes:
            original_url = episode.get("play_url", "")
            parsed_urls = []
            
            # 使用所有启用的解析器
            for parser in active_parsers:
                parsed_list = parser.parse_url(original_url)
                parsed_urls.extend(parsed_list)
                logger.debug(f"解析器 {parser.name} 为 {original_url[:50]} 生成了 {len(parsed_list)} 个链接")
            
            episode["parsed_urls"] = parsed_urls
        
        logger.info(f"为 {len(episodes)} 个剧集添加了解析链接")
        return episodes
    
    def _migrate_old_config(self):
        """迁移旧配置：将seacms的m3u8_parsers_list迁移到parser插件"""
        try:
            seacms_config = self.config_storage.get("search", "seacms")
            
            # 检查是否有旧的m3u8_parsers_list配置
            if "m3u8_parsers_list" in seacms_config:
                logger.info("检测到旧的M3U8解析器配置，开始迁移...")
                
                # 迁移到parser:m3u8配置
                parser_config = self.config_storage.get("parser", "m3u8")
                if not parser_config.get("parsers_list"):
                    parser_config["parsers_list"] = seacms_config["m3u8_parsers_list"]
                    self.config_storage.set("parser", "m3u8", parser_config)
                    logger.info(f"已迁移 {len(parser_config['parsers_list'])} 个解析器配置")
                
                # 从seacms配置中移除旧字段
                del seacms_config["m3u8_parsers_list"]
                self.config_storage.set("search", "seacms", seacms_config)
                logger.info("旧配置迁移完成")
        except Exception as e:
            logger.warning(f"配置迁移失败（可能是首次运行）: {e}")
