#!/usr/bin/env python3
"""
测试新的下载管理API
"""
import asyncio
import httpx

BASE_URL = "http://localhost:8000"

async def test_get_all_downloads():
    """测试获取所有平台的下载记录"""
    print("\n=== 测试：获取所有平台的下载记录 ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/downloads?platform=all")
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"平台: {data.get('platform')}")
            print(f"总记录数: {data.get('total')}")
            
            for platform_info in data.get('platforms', []):
                print(f"\n平台: {platform_info['name']}")
                print(f"Web UI: {platform_info['web_ui_url']}")
                print(f"下载数: {len(platform_info['downloads'])}")
                
                for download in platform_info['downloads'][:3]:  # 只显示前3条
                    print(f"  - {download['title'][:50]}... ({download['status']}, {download['progress']:.1f}%)")
        else:
            print(f"错误: {response.text}")

async def test_get_metube_downloads():
    """测试获取MeTube的下载记录"""
    print("\n=== 测试：获取MeTube的下载记录 ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/downloads?platform=metube")
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"平台: {data.get('platform')}")
            print(f"Web UI: {data.get('web_ui_url')}")
            print(f"下载数: {len(data.get('downloads', []))}")
            
            for download in data.get('downloads', [])[:5]:
                print(f"  ID: {download['id']}")
                print(f"  标题: {download['title']}")
                print(f"  状态: {download['status']}")
                print(f"  进度: {download['progress']:.1f}%")
                if download.get('speed'):
                    print(f"  速度: {download['speed']}")
                if download.get('eta'):
                    print(f"  ETA: {download['eta']}")
                print()
        else:
            print(f"错误: {response.text}")

async def test_get_qbittorrent_downloads():
    """测试获取qBittorrent的下载记录"""
    print("\n=== 测试：获取qBittorrent的下载记录 ===")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/downloads?platform=qbittorrent")
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"平台: {data.get('platform')}")
            print(f"Web UI: {data.get('web_ui_url')}")
            print(f"下载数: {len(data.get('downloads', []))}")
            
            for download in data.get('downloads', [])[:5]:
                print(f"  ID: {download['id']}")
                print(f"  标题: {download['title']}")
                print(f"  状态: {download['status']}")
                print(f"  进度: {download['progress']:.1f}%")
                if download.get('speed'):
                    print(f"  速度: {download['speed']}")
                if download.get('eta'):
                    print(f"  ETA: {download['eta']}")
                print()
        else:
            print(f"错误: {response.text}")

async def test_cancel_download():
    """测试取消下载（需要手动提供ID）"""
    print("\n=== 测试：取消下载 ===")
    print("注意：这个测试需要手动提供有效的平台和下载ID")
    print("跳过实际取消操作...")
    
    # 示例代码（需要实际的ID）
    # async with httpx.AsyncClient() as client:
    #     response = await client.post(
    #         f"{BASE_URL}/api/downloads/cancel",
    #         json={
    #             "platform": "metube",
    #             "download_id": "your_download_id_here"
    #         }
    #     )
    #     print(f"状态码: {response.status_code}")
    #     print(f"响应: {response.json()}")

async def main():
    """运行所有测试"""
    print("=" * 60)
    print("下载管理API测试")
    print("=" * 60)
    
    try:
        # 测试获取所有平台
        await test_get_all_downloads()
        
        # 等待一下
        await asyncio.sleep(1)
        
        # 测试获取MeTube
        await test_get_metube_downloads()
        
        # 等待一下
        await asyncio.sleep(1)
        
        # 测试获取qBittorrent
        await test_get_qbittorrent_downloads()
        
        # 测试取消（示例）
        await test_cancel_download()
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
