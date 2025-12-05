from typing import List
from base_plugin import SearchPlugin
from models import ConfigField, SearchResult
import httpx

class YouTubeSearchPlugin(SearchPlugin):
    
    @property
    def name(self) -> str:
        return "youtube"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "YouTube 视频搜索插件"
    
    def get_config_schema(self) -> List[ConfigField]:
        return [
            ConfigField(
                name="api_key",
                label="API Key",
                type="password",
                required=True,
                description="YouTube Data API v3 密钥"
            ),
            ConfigField(
                name="max_results",
                label="最大结果数",
                type="number",
                default=10,
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
        results = []
        
        api_key = self.config.get('api_key')
        max_results = self.config.get('max_results', 10)
        
        if not api_key:
            return results
        
        # 配置代理
        client_kwargs = {'timeout': 30.0}
        if self.config.get('use_proxy') and self.config.get('proxy_url'):
            client_kwargs['proxy'] = self.config.get('proxy_url')
        
        async with httpx.AsyncClient(**client_kwargs) as client:
            try:
                response = await client.get(
                    "https://www.googleapis.com/youtube/v3/search",
                    params={
                        "part": "snippet",
                        "q": keyword,
                        "maxResults": max_results,
                        "key": api_key,
                        "type": "video"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('items', []):
                        results.append(SearchResult(
                            title=item['snippet']['title'],
                            url=f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                            thumbnail=item['snippet']['thumbnails']['default']['url'],
                            platform="youtube",
                            metadata=item
                        ))
            except Exception as e:
                print(f"YouTube search error: {e}")
        
        return results
    
    async def get_video_info(self, url: str) -> SearchResult:
        # 简化实现
        return SearchResult(
            title="Video",
            url=url,
            platform="youtube"
        )
