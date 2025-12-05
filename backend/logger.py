"""
日志配置模块
支持不同级别的日志输出和详细调试模式
"""
import logging
import sys
from datetime import datetime
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""
    
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # 添加颜色
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        
        # 格式化消息
        result = super().format(record)
        
        # 重置levelname以避免影响其他handler
        record.levelname = levelname
        
        return result


def setup_logger(name: str = "app", log_level: str = "INFO", verbose: bool = False):
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        verbose: 是否启用详细模式（会输出更多调试信息）
    
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    
    # 如果已经配置过，直接返回
    if logger.handlers:
        return logger
    
    # 设置日志级别
    if verbose:
        log_level = "DEBUG"
    
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # 详细模式的格式
    if verbose:
        console_format = ColoredFormatter(
            '%(levelname)s [%(asctime)s] %(name)s.%(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        console_format = ColoredFormatter(
            '%(levelname)s [%(asctime)s] %(name)s - %(message)s',
            datefmt='%H:%M:%S'
        )
    
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # 文件处理器（可选）
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(
        log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log",
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # 文件总是记录DEBUG级别
    
    file_format = logging.Formatter(
        '%(levelname)s [%(asctime)s] %(name)s.%(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    return logger


def setup_logging(level: str = "INFO", verbose: bool = False):
    """
    全局日志配置
    
    Args:
        level: 日志级别
        verbose: 是否启用详细模式
    """
    # 配置根日志记录器
    root_logger = logging.getLogger()
    
    # 清除现有的处理器
    root_logger.handlers.clear()
    
    # 设置日志级别
    if verbose:
        level = "DEBUG"
    
    log_level = getattr(logging, level.upper(), logging.INFO)
    root_logger.setLevel(log_level)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # 详细模式的格式
    if verbose:
        console_format = ColoredFormatter(
            '%(levelname)s [%(asctime)s] %(name)s.%(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        console_format = ColoredFormatter(
            '%(levelname)s [%(asctime)s] %(name)s - %(message)s',
            datefmt='%H:%M:%S'
        )
    
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)
    
    # 文件处理器
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(
        log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log",
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # 文件总是记录DEBUG级别
    
    file_format = logging.Formatter(
        '%(levelname)s [%(asctime)s] %(name)s.%(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    root_logger.addHandler(file_handler)


def get_logger(name: str = None):
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称，如果为None则使用调用者的模块名
    
    Returns:
        logging.Logger: 日志记录器
    """
    if name is None:
        # 自动获取调用者的模块名
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'app')
    
    return logging.getLogger(name)
