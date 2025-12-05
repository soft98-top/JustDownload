"""测试海洋CMS插件"""
import asyncio
from plugins.search.seacms_plugin import SeaCMSSearchPlugin


async def test_search():
    plugin = SeaCMSSearchPlugin()
    
    # 配置插件
    plugin.set_config({
        'resource_sites': [
            {
                "name": "茅台资源",
                "api_url": "https://caiji.maotaizy.cc/api.php/provide/vod/at/xml",
                "enabled": True
            }
        ],
        'm3u8_parsers': [
            {
                "name": "P2P商业加速",
                "parser_url": "https://mtjiexi.cc:966/?url=",
                "enabled": True
            },
            {
                "name": "备用解析",
                "parser_url": "https://www.mtjiexi.cc:966/?url=",
                "enabled": True
            }
        ],
        'only_m3u8': True,
        'use_proxy': False,
        'proxy_url': '',
        'timeout': 30
    })
    
    # 测试搜索
    print("=" * 60)
    print("测试搜索: 斗罗大陆")
    print("=" * 60)
    
    results = await plugin.search("斗罗大陆")
    
    print(f"\n找到 {len(results)} 个结果\n")
    
    for i, result in enumerate(results[:3], 1):  # 只显示前3个
        print(f"--- 结果 {i} ---")
        print(f"标题: {result.title}")
        print(f"来源: {result.platform}")
        print(f"封面: {result.thumbnail}")
        print(f"备注: {result.metadata.get('note', '')}")
        print(f"剧集数: {result.metadata.get('episode_count', 0)}")
        print(f"M3U8数量: {result.metadata.get('m3u8_count', 0)}")
        
        # 显示前2集
        episodes = result.metadata.get('episodes', [])
        if episodes:
            print(f"\n前2集信息:")
            for ep in episodes[:2]:
                print(f"  - {ep['name']} ({ep['flag']})")
                print(f"    原始: {ep['url'][:80]}...")
                if ep.get('parsed_urls'):
                    print(f"    解析:")
                    for parsed in ep['parsed_urls']:
                        print(f"      [{parsed['name']}] {parsed['url'][:80]}...")
        print()


if __name__ == "__main__":
    asyncio.run(test_search())
