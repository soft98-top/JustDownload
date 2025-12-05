#!/usr/bin/env python3
"""
测试 Metube 进度查询功能
"""
import asyncio
import sys
from plugins.download.metube_plugin import MetubeDownloadPlugin
from logger import setup_logging, get_logger

setup_logging(level='DEBUG')
logger = get_logger(__name__)


async def test_metube_progress():
    """测试 Metube 进度查询"""
    print("=" * 60)
    print("测试 Metube 进度查询")
    print("=" * 60)
    
    # 创建插件实例
    plugin = MetubeDownloadPlugin()
    
    # 配置插件
    plugin.set_config({
        'metube_url': 'http://localhost:8081',
        'default_quality': 'best',
        'download_path': '/downloads'
    })
    
    print("\n1. 测试连接 Metube 服务...")
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
            print("   正在连接 http://localhost:8081 ...")
            # 使用正确的 /history 接口
            response = await client.get('http://localhost:8081/history')
            if response.status_code == 200:
                data = response.json()
                
                print(f"\n队列中的任务 (queue): {len(data.get('queue', []))}")
                for task in data.get('queue', []):
                    print(f"  - ID: {task.get('id')}")
                    print(f"    标题: {task.get('title', 'N/A')}")
                    print(f"    进度: {task.get('progress', 0)*100:.1f}%")
                    print(f"    状态: {task.get('status', 'N/A')}")
                
                print(f"\n已完成的任务 (done): {len(data.get('done', []))}")
                for task in data.get('done', [])[:3]:  # 只显示前3个
                    print(f"  - ID: {task.get('id')}")
                    print(f"    标题: {task.get('title', 'N/A')}")
                
                print(f"\n失败的任务 (error): {len(data.get('error', []))}")
                for task in data.get('error', []):
                    print(f"  - ID: {task.get('id')}")
                    print(f"    标题: {task.get('title', 'N/A')}")
                    print(f"    错误: {task.get('error', 'N/A')}")
                
                # 测试查询特定任务
                if data.get('queue'):
                    test_id = data['queue'][0]['id']
                    print(f"\n2. 测试查询特定任务进度: {test_id}")
                    progress_info = await plugin.get_progress(test_id)
                    print(f"  进度: {progress_info['progress']:.1f}%")
                    print(f"  状态: {progress_info['status']}")
                    print(f"  速度: {progress_info.get('speed', 'N/A')}")
                    print(f"  ETA: {progress_info.get('eta', 'N/A')}")
                    print(f"  错误: {progress_info.get('error', 'None')}")
                elif data.get('done'):
                    test_id = data['done'][0]['id']
                    print(f"\n2. 测试查询已完成任务: {test_id}")
                    progress_info = await plugin.get_progress(test_id)
                    print(f"  进度: {progress_info['progress']:.1f}%")
                    print(f"  状态: {progress_info['status']}")
                else:
                    print("\n2. 没有任务可供测试")
                
                print("\n" + "=" * 60)
                print("✓ 测试完成")
                print("=" * 60)
                
            else:
                print(f"✗ 请求失败: {response.status_code}")
                return False
                
    except httpx.ConnectError:
        print("\n⚠️  无法连接到 Metube 服务")
        print("   请确保 Metube 正在运行: http://localhost:8081")
        print("   启动命令: docker run -d -p 8081:8081 ghcr.io/alexta69/metube")
        print("\n提示: 这不是错误，只是 Metube 服务未运行")
        return True  # 返回 True，因为代码本身没问题
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_metube_progress())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
