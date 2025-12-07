from typing import List, Dict, Any
from base_plugin import SearchPlugin
from models import ConfigField, SearchResult
from logger import get_logger
import httpx
import xml.etree.ElementTree as ET
import asyncio

logger = get_logger(__name__)


class SeaCMSSearchPlugin(SearchPlugin):
    """海洋CMS资源采集插件"""
    
    @property
    def name(self) -> str:
        return "seacms"
    
    @property
    def version(self) -> str:
        return "2.0.0"
    
    @property
    def description(self) -> str:
        return "海洋CMS资源采集插件（支持多资源站）"
    
    def get_config_schema(self) -> List[ConfigField]:
        return [
            ConfigField(
                name="resource_sites_list",
                label="资源站",
                type="list",
                default=[],
                required=True,
                description='添加多个资源站，支持所有海洋CMS兼容的API',
                fields=[
                    {"name": "name", "label": "资源站名称", "type": "text", "default": ""},
                    {"name": "api_url", "label": "API地址", "type": "text", "default": ""},
                    {"name": "url_prefix", "label": "URL前缀（可选）", "type": "text", "default": ""},
                    {"name": "url_suffix", "label": "URL后缀（可选，如$hym3u8）", "type": "text", "default": ""},
                    {"name": "enabled", "label": "启用", "type": "boolean", "default": True}
                ]
            ),
            ConfigField(
                name="only_m3u8",
                label="只采集M3U8资源",
                type="boolean",
                default=True,
                description="开启后只返回包含m3u8的视频"
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
            ),
            ConfigField(
                name="timeout",
                label="请求超时时间（秒）",
                type="number",
                default=30,
                description="API请求超时时间"
            )
        ]
    
    def _parse_resource_sites(self) -> List[Dict[str, Any]]:
        """解析资源站配置"""
        import json
        try:
            # 兼容新旧字段名
            sites_str = self.config.get('resource_sites_list') or self.config.get('resource_sites', '[]')
            sites = json.loads(sites_str) if isinstance(sites_str, str) else sites_str
            return [site for site in sites if site.get('enabled', True)]
        except Exception as e:
            logger.error(f"解析资源站配置失败: {e}")
            return []
    
    def _clean_url(self, url: str, site: Dict[str, Any]) -> str:
        """清理URL，去除个性化前缀和后缀
        
        例如: https://1080p.huyall.com/play/mep3QRQd/index.m3u8$hym3u8
        如果配置了url_suffix="$hym3u8"，则返回: https://1080p.huyall.com/play/mep3QRQd/index.m3u8
        """
        cleaned_url = url
        
        # 去除后缀
        url_suffix = site.get('url_suffix', '').strip()
        if url_suffix and cleaned_url.endswith(url_suffix):
            cleaned_url = cleaned_url[:-len(url_suffix)]
        
        # 去除前缀
        url_prefix = site.get('url_prefix', '').strip()
        if url_prefix and cleaned_url.startswith(url_prefix):
            cleaned_url = cleaned_url[len(url_prefix):]
        
        return cleaned_url
    
    def _parse_xml_response(self, xml_content: str, site_name: str, site: Dict[str, Any]) -> List[SearchResult]:
        """解析海洋CMS的XML响应"""
        results = []
        only_m3u8 = self.config.get('only_m3u8', True)
        
        try:
            root = ET.fromstring(xml_content)
            
            # 遍历所有video节点
            for video in root.findall('.//video'):
                video_id = video.findtext('last', '')
                title = video.findtext('name', '')
                pic = video.findtext('pic', '')
                note = video.findtext('note', '')
                desc = video.findtext('des', '') or ''  # 获取描述字段，确保是字符串
                
                # 解析播放地址
                dl_node = video.find('dl')
                if dl_node is None:
                    continue
                
                episodes = []
                m3u8_urls = []
                
                # 遍历所有dd节点（不同播放源）
                for dd in dl_node.findall('dd'):
                    flag = dd.get('flag', '未知播放器')
                    play_data = dd.text or ''
                    
                    # 解析剧集：格式为 "第1集$url1#第2集$url2"
                    if play_data:
                        episode_list = play_data.split('#')
                        for ep in episode_list:
                            if '$' in ep:
                                ep_name, ep_url = ep.split('$', 1)
                                
                                # 清理URL（去除前缀和后缀）
                                ep_url = self._clean_url(ep_url.strip(), site)
                                
                                # 检查是否包含m3u8
                                is_m3u8 = '.m3u8' in ep_url.lower()
                                
                                if only_m3u8 and not is_m3u8:
                                    continue
                                
                                episodes.append({
                                    'episode_name': ep_name.strip(),
                                    'play_url': ep_url,
                                    'flag': flag,
                                    'is_m3u8': is_m3u8
                                })
                                
                                if is_m3u8:
                                    m3u8_urls.append(ep_url)
                
                # 如果没有m3u8资源且设置了only_m3u8，跳过
                if only_m3u8 and not m3u8_urls:
                    continue
                
                # 如果有剧集，使用第一集的URL作为主URL
                main_url = episodes[0]['play_url'] if episodes else ''
                
                # 生成简短描述（取前100字符）
                # 确保 desc 是字符串类型
                desc_str = str(desc) if desc else ''
                short_desc = (desc_str[:100] + '...') if len(desc_str) > 100 else desc_str
                
                results.append(SearchResult(
                    title=title,
                    url=main_url,
                    thumbnail=pic,
                    platform=site_name,
                    description=short_desc,  # 简短描述用于列表展示
                    metadata={
                        'video_id': str(video_id) if video_id else '',  # 确保是字符串
                        'note': str(note) if note else '',  # 确保是字符串
                        'full_description': desc_str,  # 完整描述用于详情浮窗
                        'episodes': episodes,
                        'episode_count': len(episodes),
                        'has_m3u8': len(m3u8_urls) > 0,
                        'm3u8_count': len(m3u8_urls)
                    }
                ))
        
        except ET.ParseError as e:
            print(f"XML解析错误 [{site_name}]: {e}")
        except Exception as e:
            print(f"处理视频数据错误 [{site_name}]: {e}")
        
        return results
    
    async def _search_single_site(self, site: Dict[str, Any], keyword: str) -> List[SearchResult]:
        """在单个资源站搜索"""
        site_name = site.get('name', '未知站点')
        api_url = site.get('api_url', '')
        
        if not api_url:
            return []
        
        timeout = self.config.get('timeout', 30)
        use_proxy = self.config.get('use_proxy', False)
        proxy_url = self.config.get('proxy_url', '')
        
        # 配置httpx客户端（trust_env=False避免使用系统代理）
        if use_proxy and proxy_url:
            client = httpx.AsyncClient(timeout=timeout, follow_redirects=True, proxy=proxy_url)
        else:
            client = httpx.AsyncClient(timeout=timeout, follow_redirects=True, trust_env=False)
        
        try:
            async with client:
                # 构建搜索URL，使用ac=detail获取完整信息包括播放地址
                search_url = f"{api_url}?ac=detail&wd={keyword}"
                
                print(f"正在搜索 [{site_name}]: {search_url}")
                
                response = await client.get(search_url)
                
                if response.status_code == 200:
                    return self._parse_xml_response(response.text, site_name, site)
                else:
                    print(f"搜索失败 [{site_name}]: HTTP {response.status_code}")
                    return []
        
        except Exception as e:
            print(f"搜索异常 [{site_name}]: {e}")
            return []
    
    async def search(self, keyword: str, **kwargs) -> List[SearchResult]:
        """搜索视频资源（使用ac=detail获取完整信息）"""
        sites = self._parse_resource_sites()
        
        if not sites:
            print("未配置资源站或所有资源站已禁用")
            return []
        
        # 并发搜索所有资源站
        tasks = [self._search_single_site(site, keyword) for site in sites]
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 合并所有结果
        all_results = []
        for results in results_list:
            if isinstance(results, list):
                all_results.extend(results)
            elif isinstance(results, Exception):
                print(f"搜索任务异常: {results}")
        
        print(f"搜索完成，共找到 {len(all_results)} 个结果")
        return all_results
    
    async def get_video_info(self, url: str) -> SearchResult:
        """获取视频详细信息（通过video_id）"""
        # 简化实现，实际可以通过ids参数获取详情
        return SearchResult(
            title="视频详情",
            url=url,
            platform="seacms"
        )
