"""
配置存储模块
负责插件配置的持久化存储
"""
import json
from pathlib import Path
from typing import Dict, Any
from logger import get_logger

logger = get_logger(__name__)


class ConfigStorage:
    """配置存储管理器"""
    
    def __init__(self, config_file: str = "config/plugins.json"):
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self._config: Dict[str, Dict[str, Any]] = {}
        self._load()
    
    def _load(self):
        """从文件加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                logger.info(f"配置加载成功: {len(self._config)} 个插件")
                logger.debug(f"配置内容: {list(self._config.keys())}")
            except Exception as e:
                logger.error(f"配置加载失败: {e}", exc_info=True)
                self._config = {}
        else:
            logger.info("配置文件不存在，使用空配置")
            self._config = {}
    
    def _save(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            logger.info(f"配置保存成功: {self.config_file}")
            logger.debug(f"保存了 {len(self._config)} 个插件配置")
        except Exception as e:
            logger.error(f"配置保存失败: {e}", exc_info=True)
    
    def get(self, plugin_type: str, plugin_name: str) -> Dict[str, Any]:
        """获取插件配置"""
        key = f"{plugin_type}:{plugin_name}"
        config = self._config.get(key, {})
        logger.debug(f"获取配置: {key} -> {bool(config)}")
        return config
    
    def set(self, plugin_type: str, plugin_name: str, config: Dict[str, Any]):
        """设置插件配置"""
        key = f"{plugin_type}:{plugin_name}"
        self._config[key] = config
        self._save()
        logger.info(f"配置已更新并保存: {key}")
    
    def is_enabled(self, plugin_type: str, plugin_name: str) -> bool:
        """检查插件是否启用"""
        config = self.get(plugin_type, plugin_name)
        # 默认启用，除非明确设置为 False
        return config.get('_enabled', True)
    
    def set_enabled(self, plugin_type: str, plugin_name: str, enabled: bool):
        """设置插件启用状态"""
        config = self.get(plugin_type, plugin_name)
        config['_enabled'] = enabled
        self.set(plugin_type, plugin_name, config)
    
    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """获取所有配置"""
        return self._config.copy()
    
    def delete(self, plugin_type: str, plugin_name: str):
        """删除插件配置"""
        key = f"{plugin_type}:{plugin_name}"
        if key in self._config:
            del self._config[key]
            self._save()
            logger.info(f"配置已删除: {key}")


# 全局配置存储实例
_storage = None


def get_config_storage() -> ConfigStorage:
    """获取配置存储实例（单例）"""
    global _storage
    if _storage is None:
        _storage = ConfigStorage()
    return _storage
