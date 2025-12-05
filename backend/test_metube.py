"""测试Metube API"""
import asyncio
import httpx
from logger import setup_logging, get_logger

setup_logging(level="DEBUG", verbose=True)
logger = get_logger(__name__)


async def test_metube_api():
    """测试Metube API"""
    metube_url = "http://192.168.0.106:10013"
    
    logger.info("=" * 60)
    logger.info("测试Metube API")
    logger.info(f"服务地址: {metube_url}")
    logger.info("=" * 60)
    
    # 测试1: 检查服务是否可访问
    logger.info("\n1. 测试服务连接...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(metube_url)
            logger.info(f"✓ 服务可访问，状态码: {response.status_code}")
            logger.debug(f"响应头: {dict(response.headers)}")
    except Exception as e:
        logger.error(f"✗ 服务不可访问: {e}")
        return
    
    # 测试2: 测试添加下载任务（简单URL）
    logger.info("\n2. 测试添加下载任务（测试URL）...")
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "url": test_url,
                "quality": "best"
            }
            logger.debug(f"请求payload: {payload}")
            
            response = await client.post(
                f"{metube_url}/add",
                json=payload
            )
            
            logger.info(f"响应状态码: {response.status_code}")
            logger.info(f"响应内容: {response.text}")
            
            # 尝试解析JSON
            try:
                result = response.json()
                logger.info(f"JSON解析成功: {result}")
                
                if result.get('status') == 'error':
                    logger.error(f"✗ 下载失败: {result.get('msg')}")
                else:
                    logger.info(f"✓ 下载任务添加成功")
            except:
                logger.info("响应不是JSON格式")
                
    except Exception as e:
        logger.error(f"✗ 请求失败: {e}", exc_info=True)
    
    # 测试3: 测试添加下载任务（m3u8 URL）
    logger.info("\n3. 测试添加下载任务（m3u8 URL）...")
    m3u8_url = "https://vodcnd04.kunyu.com.cn/20250414/bzSRAhJZ/index.m3u8"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "url": m3u8_url,
                "quality": "best",
                "folder": "/downloads"
            }
            logger.debug(f"请求payload: {payload}")
            
            response = await client.post(
                f"{metube_url}/add",
                json=payload
            )
            
            logger.info(f"响应状态码: {response.status_code}")
            logger.info(f"响应内容: {response.text}")
            
            # 尝试解析JSON
            try:
                result = response.json()
                logger.info(f"JSON解析成功: {result}")
                
                if result.get('status') == 'error':
                    logger.error(f"✗ 下载失败: {result.get('msg')}")
                else:
                    logger.info(f"✓ 下载任务添加成功")
            except:
                logger.info("响应不是JSON格式")
                
    except Exception as e:
        logger.error(f"✗ 请求失败: {e}", exc_info=True)
    
    # 测试4: 查看所有任务
    logger.info("\n4. 查看下载队列...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{metube_url}/downloads")
            logger.info(f"响应状态码: {response.status_code}")
            
            try:
                downloads = response.json()
                logger.info(f"当前任务数: {len(downloads)}")
                for i, task in enumerate(downloads[:3], 1):
                    logger.info(f"  任务{i}: {task.get('title', 'N/A')} - {task.get('status', 'N/A')}")
            except:
                logger.info(f"响应内容: {response.text[:200]}")
    except Exception as e:
        logger.error(f"✗ 查询失败: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info("测试完成")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_metube_api())
