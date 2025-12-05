"""
测试视频解析器插件功能
"""
import asyncio
import sys
sys.path.insert(0, '.')

from plugin_manager import PluginManager
from plugins.parser.m3u8_parser_plugin import M3U8ParserPlugin
from plugins.search.seacms_plugin import SeaCMSSearchPlugin

async def test_parser_plugin():
    """测试解析器插件"""
    print("=" * 60)
    print("测试视频解析器插件")
    print("=" * 60)
    
    # 创建插件管理器
    pm = PluginManager()
    
    # 注册解析器插件
    parser = M3U8ParserPlugin()
    pm.register_parser_plugin(parser)
    
    # 配置解析器
    parser_config = {
        "parsers_list": [
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
        ]
    }
    pm.set_plugin_config("parser", "m3u8", parser_config)
    
    print("\n✓ 解析器插件已注册并配置")
    print(f"  - 插件名称: {parser.name}")
    print(f"  - 插件版本: {parser.version}")
    print(f"  - 解析器数量: {len(parser_config['parsers_list'])}")
    
    # 测试解析URL
    test_url = "https://example.com/video/episode1.m3u8"
    print(f"\n测试解析URL: {test_url}")
    
    parsed_urls = parser.parse_url(test_url)
    print(f"\n✓ 生成了 {len(parsed_urls)} 个解析链接:")
    for i, parsed in enumerate(parsed_urls, 1):
        print(f"  {i}. {parsed['name']}")
        print(f"     {parsed['url']}")
    
    # 测试剧集解析
    print("\n" + "=" * 60)
    print("测试剧集批量解析")
    print("=" * 60)
    
    episodes = [
        {"episode_name": "第1集", "play_url": "https://example.com/ep1.m3u8"},
        {"episode_name": "第2集", "play_url": "https://example.com/ep2.m3u8"},
        {"episode_name": "第3集", "play_url": "https://example.com/ep3.m3u8"}
    ]
    
    enhanced_episodes = pm.parse_video_urls(episodes)
    
    print(f"\n✓ 处理了 {len(enhanced_episodes)} 个剧集:")
    for ep in enhanced_episodes:
        print(f"\n  {ep['episode_name']}:")
        print(f"    原始链接: {ep['play_url']}")
        print(f"    解析链接数: {len(ep.get('parsed_urls', []))}")
        for parsed in ep.get('parsed_urls', []):
            print(f"      - {parsed['name']}")
    
    # 测试配置迁移
    print("\n" + "=" * 60)
    print("测试配置迁移")
    print("=" * 60)
    
    # 模拟旧配置
    from config_storage import get_config_storage
    storage = get_config_storage()
    
    old_seacms_config = {
        "resource_sites_list": [],
        "m3u8_parsers_list": [
            {"name": "旧解析器1", "parser_url": "http://old1.com/?url=", "enabled": True},
            {"name": "旧解析器2", "parser_url": "http://old2.com/?url=", "enabled": True}
        ],
        "only_m3u8": True
    }
    
    storage.set("search", "seacms", old_seacms_config)
    print("\n✓ 已设置旧的seacms配置（包含m3u8_parsers_list）")
    
    # 创建新的插件管理器触发迁移
    pm2 = PluginManager()
    pm2.register_parser_plugin(M3U8ParserPlugin())
    pm2.register_search_plugin(SeaCMSSearchPlugin())
    
    # 检查迁移结果
    new_parser_config = storage.get("parser", "m3u8")
    new_seacms_config = storage.get("search", "seacms")
    
    print("\n✓ 配置迁移完成:")
    print(f"  - parser:m3u8 配置: {len(new_parser_config.get('parsers_list', []))} 个解析器")
    print(f"  - search:seacms 是否还有旧字段: {'m3u8_parsers_list' in new_seacms_config}")
    
    if new_parser_config.get('parsers_list'):
        print("\n  迁移后的解析器:")
        for p in new_parser_config['parsers_list']:
            print(f"    - {p['name']}: {p['parser_url']}")
    
    print("\n" + "=" * 60)
    print("✓ 所有测试完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_parser_plugin())
