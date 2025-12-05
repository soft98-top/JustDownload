#!/usr/bin/env python3
"""
测试插件启用/禁用功能
"""
import asyncio
import httpx

BASE_URL = "http://localhost:8000"

async def test_list_plugins():
    """测试获取插件列表（包含启用状态）"""
    print("\n=== 测试：获取插件列表 ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/plugins")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n搜索插件:")
            for plugin in data.get('search', []):
                status = "✓ 已启用" if plugin.get('enabled', True) else "✗ 已禁用"
                print(f"  - {plugin['name']} (v{plugin['version']}) {status}")
            
            print("\n下载插件:")
            for plugin in data.get('download', []):
                status = "✓ 已启用" if plugin.get('enabled', True) else "✗ 已禁用"
                print(f"  - {plugin['name']} (v{plugin['version']}) {status}")
                print(f"    支持: {', '.join(plugin['supported_protocols'])}")
        else:
            print(f"错误: {response.status_code}")

async def test_disable_plugin():
    """测试禁用插件"""
    print("\n=== 测试：禁用 MeTube 插件 ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/plugins/download/metube/toggle",
            params={"enabled": False}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 操作成功: {data}")
        else:
            print(f"✗ 操作失败: {response.status_code}")
            print(f"  错误: {response.text}")

async def test_enable_plugin():
    """测试启用插件"""
    print("\n=== 测试：启用 MeTube 插件 ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/plugins/download/metube/toggle",
            params={"enabled": True}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 操作成功: {data}")
        else:
            print(f"✗ 操作失败: {response.status_code}")
            print(f"  错误: {response.text}")

async def test_query_with_disabled_plugin():
    """测试禁用插件后的查询"""
    print("\n=== 测试：禁用插件后查询下载记录 ===")
    
    async with httpx.AsyncClient() as client:
        # 先禁用 MeTube
        await client.post(
            f"{BASE_URL}/api/plugins/download/metube/toggle",
            params={"enabled": False}
        )
        print("已禁用 MeTube 插件")
        
        # 查询所有平台
        response = await client.get(f"{BASE_URL}/api/downloads?platform=all")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n查询结果:")
            print(f"  平台数: {len(data.get('platforms', []))}")
            
            for platform in data.get('platforms', []):
                print(f"  - {platform['name']}: {len(platform['downloads'])} 条记录")
            
            # 检查是否包含 MeTube
            has_metube = any(p['name'] == 'metube' for p in data.get('platforms', []))
            if has_metube:
                print("\n✗ 错误: 禁用的插件仍然被查询")
            else:
                print("\n✓ 正确: 禁用的插件已被跳过")
        else:
            print(f"✗ 查询失败: {response.status_code}")
        
        # 恢复启用
        await client.post(
            f"{BASE_URL}/api/plugins/download/metube/toggle",
            params={"enabled": True}
        )
        print("\n已恢复启用 MeTube 插件")

async def main():
    """运行所有测试"""
    print("=" * 60)
    print("插件启用/禁用功能测试")
    print("=" * 60)
    
    try:
        # 测试获取插件列表
        await test_list_plugins()
        await asyncio.sleep(1)
        
        # 测试禁用插件
        await test_disable_plugin()
        await asyncio.sleep(1)
        
        # 再次查看列表
        await test_list_plugins()
        await asyncio.sleep(1)
        
        # 测试启用插件
        await test_enable_plugin()
        await asyncio.sleep(1)
        
        # 测试禁用插件后的查询
        await test_query_with_disabled_plugin()
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
