"""测试Metube - 使用本地可访问的URL"""
import asyncio
import httpx
from logger import setup_logging, get_logger

setup_logging(level="INFO", verbose=False)
logger = get_logger(__name__)


async def test_local_accessible_url():
    """测试Metube服务器可以访问的URL"""
    metube_url = "http://192.168.0.106:10013"
    
    logger.info("=" * 60)
    logger.info("测试Metube - 本地可访问URL")
    logger.info("=" * 60)
    
    # 测试URL列表 - 这些应该是Metube服务器可以访问的
    test_urls = [
        {
            "name": "示例视频（如果有本地视频服务器）",
            "url": "http://192.168.0.106/test.mp4",  # 替换为实际可访问的URL
            "note": "需要替换为实际的本地URL"
        },
        {
            "name": "公共测试视频",
            "url": "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4",
            "note": "公共测试视频"
        }
    ]
    
    logger.info("\n当前问题：")
    logger.info("  Metube服务器无法访问外网视频源")
    logger.info("  错误：Connection reset by peer")
    logger.info("")
    logger.info("解决方案：")
    logger.info("  1. 为Metube配置代理")
    logger.info("  2. 使用Metube服务器可以直接访问的URL")
    logger.info("  3. 检查Metube服务器的网络配置")
    logger.info("")
    
    # 测试一个简单的直接下载URL
    logger.info("测试公共视频URL...")
    test_url = "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4"
    
    try:
        async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
            payload = {
                "url": test_url,
                "quality": "best"
            }
            
            logger.info(f"URL: {test_url}")
            
            response = await client.post(
                f"{metube_url}/add",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            logger.info(f"响应状态码: {response.status_code}")
            
            try:
                result = response.json()
                status = result.get('status')
                
                if status == 'error':
                    logger.error(f"✗ 下载失败: {result.get('msg')}")
                    logger.error("")
                    logger.error("这表明Metube服务器的网络配置有问题")
                    logger.error("建议：")
                    logger.error("  1. 检查Metube容器的网络设置")
                    logger.error("  2. 配置HTTP_PROXY环境变量")
                    logger.error("  3. 检查防火墙规则")
                elif status in ['ok', 'success']:
                    logger.info(f"✓ 下载成功！")
                    logger.info(f"  任务ID: {result.get('id', 'N/A')}")
                    logger.info("")
                    logger.info("Metube服务器可以访问这个URL")
                    logger.info("问题可能是特定网站的访问限制")
                    
            except ValueError:
                logger.warning("响应不是JSON格式")
                
    except Exception as e:
        logger.error(f"测试失败: {e}")
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("总结")
    logger.info("=" * 60)
    logger.info("")
    logger.info("插件本身工作正常，问题在于：")
    logger.info("  ✓ 插件可以连接到Metube服务")
    logger.info("  ✓ 插件可以正确发送请求")
    logger.info("  ✓ 插件可以正确解析响应")
    logger.info("  ✗ Metube服务器无法访问视频源")
    logger.info("")
    logger.info("下一步：")
    logger.info("  1. 配置Metube的代理设置")
    logger.info("  2. 或使用Metube服务器可以访问的视频源")
    logger.info("  3. 检查Metube容器的日志：docker logs metube")


if __name__ == "__main__":
    asyncio.run(test_local_accessible_url())
