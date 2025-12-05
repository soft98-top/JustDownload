#!/usr/bin/env python3
"""测试SeaCMS插件的改进功能"""

import asyncio
import json
from plugins.search.seacms_plugin import SeaCMSSearchPlugin


async def test_url_cleaning():
    """测试URL清理功能（去除前缀和后缀）"""
    print("\n=== 测试URL清理功能 ===")
    
    plugin = SeaCMSSearchPlugin()
    
    # 测试用例
    test_cases = [
        {
            "url": "https://1080p.huyall.com/play/mep3QRQd/index.m3u8$hym3u8",
            "site": {"url_prefix": "", "url_suffix": "$hym3u8"},
            "expected": "https://1080p.huyall.com/play/mep3QRQd/index.m3u8"
        },
        {
            "url": "prefix_https://example.com/video.m3u8",
            "site": {"url_prefix": "prefix_", "url_suffix": ""},
            "expected": "https://example.com/video.m3u8"
        },
        {
            "url": "prefix_https://example.com/video.m3u8$suffix",
            "site": {"url_prefix": "prefix_", "url_suffix": "$suffix"},
            "expected": "https://example.com/video.m3u8"
        },
        {
            "url": "https://example.com/video.m3u8",
            "site": {"url_prefix": "", "url_suffix": ""},
            "expected": "https://example.com/video.m3u8"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        result = plugin._clean_url(test["url"], test["site"])
        status = "✓" if result == test["expected"] else "✗"
        print(f"{status} 测试 {i}:")
        print(f"  原始URL: {test['url']}")
        print(f"  配置: prefix='{test['site']['url_prefix']}', suffix='{test['site']['url_suffix']}'")
        print(f"  期望结果: {test['expected']}")
        print(f"  实际结果: {result}")
        if result != test["expected"]:
            print(f"  ❌ 测试失败！")
        print()


async def test_config_schema():
    """测试配置字段是否包含前缀/后缀选项"""
    print("\n=== 测试配置字段 ===")
    
    plugin = SeaCMSSearchPlugin()
    schema = plugin.get_config_schema()
    
    # 查找resource_sites_list字段
    resource_sites_field = None
    for field in schema:
        if field.name == "resource_sites_list":
            resource_sites_field = field
            break
    
    if resource_sites_field:
        print("✓ 找到resource_sites_list字段")
        print(f"  描述: {resource_sites_field.description}")
        
        # 解析默认值
        try:
            default_sites = json.loads(resource_sites_field.default)
            if default_sites and len(default_sites) > 0:
                first_site = default_sites[0]
                print(f"  默认站点示例: {first_site['name']}")
                
                # 检查是否包含url_prefix和url_suffix字段
                has_prefix = 'url_prefix' in first_site
                has_suffix = 'url_suffix' in first_site
                
                print(f"  {'✓' if has_prefix else '✗'} 包含url_prefix字段")
                print(f"  {'✓' if has_suffix else '✗'} 包含url_suffix字段")
                
                if has_prefix and has_suffix:
                    print("\n✓ 配置字段测试通过！")
                else:
                    print("\n✗ 配置字段缺少前缀/后缀选项")
        except Exception as e:
            print(f"✗ 解析默认配置失败: {e}")
    else:
        print("✗ 未找到resource_sites_list字段")


async def test_description_field():
    """测试描述字段"""
    print("\n=== 测试描述字段 ===")
    
    plugin = SeaCMSSearchPlugin()
    
    # 测试插件描述
    print(f"插件名称: {plugin.name}")
    print(f"插件版本: {plugin.version}")
    print(f"插件描述: {plugin.description}")
    
    # 测试SearchResult是否支持description字段
    from models import SearchResult
    
    try:
        result = SearchResult(
            title="测试视频",
            url="https://example.com/video.m3u8",
            platform="test",
            description="这是一个测试描述"
        )
        print(f"\n✓ SearchResult支持description字段")
        print(f"  描述内容: {result.description}")
    except Exception as e:
        print(f"\n✗ SearchResult不支持description字段: {e}")


async def main():
    """运行所有测试"""
    print("=" * 60)
    print("SeaCMS插件改进功能测试")
    print("=" * 60)
    
    await test_url_cleaning()
    await test_config_schema()
    await test_description_field()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
