"""
搜索插件模板

使用此模板创建新的搜索插件。
复制此文件并修改相应的方法即可。
"""

from typing import List
from base_plugin import SearchPlugin
from models import ConfigField, SearchResult
import httpx


class TemplateSearchPlugin(SearchPlugin):
    """搜索插件模板"""
    
    @property
    def name(self) -> str:
        """插件名称（唯一标识）"""
        return "template"
    
    @property
    def version(self) -> str:
        """插件版本"""
        return "1.0.0"
    
    @property
    def description(self) -> str:
        """插件描述"""
        return "搜索插件模板 - 用于创建新插件"
    
    def get_config_schema(self) -> List[ConfigField]:
        """
        定义插件的配置项
        
        支持的字段类型:
        - text: 文本输入
        - password: 密码输入
        - number: 数字输入
        - boolean: 开关
        """
        return [
            ConfigField(
                name="api_key",
                label="API密钥",
                type="password",
                required=True,
                description="平台API密钥"
            ),
            ConfigField(
                name="max_results",
                label="最大结果数",
                type="number",
                default=20,
                description="每次搜索返回的最大结果数"
            ),
            ConfigField(
                name="use_proxy",
                label="使用代理",
                type="boolean",
                default=False
            ),
            ConfigField(
                name="proxy_url",
                label="代理地址",
                type="text",
                default="",
                description="例如: http://127.0.0.1:7890"
            )
        ]
    
    async def search(self, keyword: str, **kwargs) -> List[SearchResult]:
        """
        搜索方法
        
        Args:
            keyword: 搜索关键词
            **kwargs: 额外参数
            
        Returns:
            搜索结果列表
        """
        results = []
        
        # 从配置中获取参数（使用辅助方法安全获取）
        api_key = self._get_config_str('api_key', '')
        max_results = self._get_config_int('max_results', 20)
        use_proxy = self._get_config_bool('use_proxy', False)
        proxy_url = self._get_config_str('proxy_url', '')
        
        # 检查必需配置
        if not api_key:
            return results
        
        # 配置HTTP客户端
        client_kwargs = {'timeout': 30.0}
        if use_proxy and proxy_url:
            client_kwargs['proxy'] = proxy_url
        
        # 发送请求
        async with httpx.AsyncClient(**client_kwargs) as client:
            try:
                # TODO: 实现你的搜索逻辑
                # 示例:
                # response = await client.get(
                #     "https://api.example.com/search",
                #     params={"q": keyword, "limit": max_results}
                # )
                # 
                # if response.status_code == 200:
                #     data = response.json()
                #     for item in data.get('items', []):
                #         results.append(SearchResult(
                #             title=item['title'],
                #             url=item['url'],
                #             thumbnail=item.get('thumbnail', ''),
                #             platform="YourPlatform",
                #             metadata=item
                #         ))
                
                pass
                
            except Exception as e:
                print(f"搜索错误: {e}")
        
        return results
    
    async def get_video_info(self, url: str) -> SearchResult:
        """
        获取视频详细信息
        
        Args:
            url: 视频URL
            
        Returns:
            视频详细信息
        """
        # TODO: 实现获取视频详情的逻辑
        return SearchResult(
            title="视频标题",
            url=url,
            platform="YourPlatform"
        )
