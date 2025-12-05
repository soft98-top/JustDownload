"""Metube服务诊断工具"""
import asyncio
import httpx
import sys
from logger import setup_logging, get_logger

setup_logging(level="DEBUG", verbose=True)
logger = get_logger(__name__)


async def diagnose_metube(metube_url: str):
    """诊断Metube服务"""
    
    logger.info("=" * 70)
    logger.info("Metube 服务诊断工具")
    logger.info("=" * 70)
    logger.info(f"服务地址: {metube_url}")
    logger.info("")
    
    # 测试1: 基本连接
    logger.info("【测试1】检查服务连接...")
    logger.info("-" * 70)
    try:
        async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
            response = await client.get(metube_url)
            logger.info(f"✓ 服务可访问")
            logger.info(f"  状态码: {response.status_code}")
            logger.info(f"  服务器: {response.headers.get('Server', 'Unknown')}")
            logger.debug(f"  响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                logger.info(f"  响应长度: {len(response.text)} 字节")
    except httpx.ConnectError as e:
        logger.error(f"✗ 无法连接到服务")
        logger.error(f"  错误: {e}")
        logger.error(f"  请检查:")
        logger.error(f"    1. Metube服务是否正在运行")
        logger.error(f"    2. 地址和端口是否正确")
        logger.error(f"    3. 防火墙设置")
        return False
    except Exception as e:
        logger.error(f"✗ 连接测试失败: {e}")
        return False
    
    logger.info("")
    
    # 测试2: API端点测试
    logger.info("【测试2】测试 /add 端点...")
    logger.info("-" * 70)
    
    test_cases = [
        {
            "name": "YouTube视频",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "quality": "best"
        },
        {
            "name": "M3U8流媒体",
            "url": "https://vodcnd04.kunyu.com.cn/20250414/bzSRAhJZ/index.m3u8",
            "quality": "best"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n测试用例 {i}: {test_case['name']}")
        logger.info(f"URL: {test_case['url']}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
                payload = {
                    "url": test_case['url'],
                    "quality": test_case['quality']
                }
                
                logger.debug(f"请求payload: {payload}")
                
                response = await client.post(
                    f"{metube_url}/add",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                logger.info(f"响应状态码: {response.status_code}")
                
                # 解析响应
                try:
                    result = response.json()
                    logger.info(f"响应JSON: {result}")
                    
                    status = result.get('status')
                    if status == 'error':
                        logger.error(f"✗ 添加失败")
                        logger.error(f"  错误信息: {result.get('msg', '未知错误')}")
                    elif status in ['ok', 'success']:
                        logger.info(f"✓ 添加成功")
                        if 'id' in result:
                            logger.info(f"  任务ID: {result['id']}")
                    else:
                        logger.warning(f"? 状态未知: {status}")
                        
                except ValueError:
                    logger.warning(f"响应不是JSON格式")
                    logger.info(f"响应内容: {response.text[:200]}")
                    
        except Exception as e:
            logger.error(f"✗ 测试失败: {e}")
    
    logger.info("")
    
    # 测试3: 查询下载列表
    logger.info("【测试3】查询下载列表...")
    logger.info("-" * 70)
    try:
        async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
            # 尝试不同的端点
            endpoints = ['/downloads', '/queue', '/status']
            
            for endpoint in endpoints:
                try:
                    response = await client.get(f"{metube_url}{endpoint}")
                    if response.status_code == 200:
                        logger.info(f"✓ 端点 {endpoint} 可用")
                        try:
                            data = response.json()
                            logger.info(f"  数据类型: {type(data)}")
                            if isinstance(data, list):
                                logger.info(f"  任务数量: {len(data)}")
                            elif isinstance(data, dict):
                                logger.info(f"  数据键: {list(data.keys())}")
                        except:
                            logger.info(f"  响应长度: {len(response.text)} 字节")
                except:
                    logger.debug(f"端点 {endpoint} 不可用")
                    
    except Exception as e:
        logger.warning(f"查询列表失败: {e}")
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("诊断完成")
    logger.info("=" * 70)
    logger.info("")
    logger.info("建议:")
    logger.info("1. 如果连接失败，检查Metube服务是否运行")
    logger.info("2. 如果添加任务失败，查看错误信息")
    logger.info("3. 某些URL可能需要特殊配置（如代理、cookies等）")
    logger.info("4. 检查Metube的日志获取更多信息")
    
    return True


if __name__ == "__main__":
    # 从命令行参数获取URL，或使用默认值
    metube_url = sys.argv[1] if len(sys.argv) > 1 else "http://192.168.0.106:10013"
    
    asyncio.run(diagnose_metube(metube_url))
