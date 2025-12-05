"""测试日志系统"""
from logger import setup_logging, get_logger

# 测试不同级别的日志
def test_logging():
    print("\n" + "="*60)
    print("测试日志系统")
    print("="*60 + "\n")
    
    # 测试INFO级别
    print("1. 测试 INFO 级别日志:")
    print("-" * 60)
    setup_logging(level="INFO", verbose=False)
    logger = get_logger("test")
    
    logger.debug("这是DEBUG日志 - 不应该显示")
    logger.info("这是INFO日志 - 应该显示")
    logger.warning("这是WARNING日志 - 应该显示")
    logger.error("这是ERROR日志 - 应该显示")
    
    print("\n2. 测试 DEBUG 级别日志（详细模式）:")
    print("-" * 60)
    
    # 清除之前的配置
    import logging
    logging.getLogger().handlers.clear()
    
    setup_logging(level="DEBUG", verbose=True)
    logger = get_logger("test_verbose")
    
    logger.debug("这是DEBUG日志 - 应该显示，包含函数名和行号")
    logger.info("这是INFO日志 - 应该显示")
    logger.warning("这是WARNING日志 - 应该显示")
    logger.error("这是ERROR日志 - 应该显示")
    
    print("\n3. 测试异常日志:")
    print("-" * 60)
    
    try:
        result = 1 / 0
    except Exception as e:
        logger.error(f"捕获异常: {e}", exc_info=True)
    
    print("\n" + "="*60)
    print("日志测试完成！")
    print("日志文件保存在: logs/app_*.log")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_logging()
