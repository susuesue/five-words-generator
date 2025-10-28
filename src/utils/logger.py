"""
日志配置模块
统一管理项目日志
"""
import logging
import sys
from logging.handlers import RotatingFileHandler

from .config import (
    LOG_FILE,
    LOG_ERROR_FILE,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
    LOG_LEVEL,
    LOG_MAX_SIZE,
    LOG_BACKUP_COUNT
)


def setup_logger(name: str = __name__) -> logging.Logger:
    """
    创建并配置日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    logger.setLevel(LOG_LEVEL)
    
    # 创建格式化器
    formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（所有日志）
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=LOG_MAX_SIZE * 1024 * 1024,  # 转换为字节
        backupCount=LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 错误文件处理器（只记录错误）
    error_handler = RotatingFileHandler(
        LOG_ERROR_FILE,
        maxBytes=LOG_MAX_SIZE * 1024 * 1024,
        backupCount=LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger


# 创建默认日志记录器
logger = setup_logger("three_words_generator")


def get_logger(name: str = None) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称，默认使用调用者的模块名
        
    Returns:
        日志记录器
    """
    if name is None:
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'unknown')
    
    return setup_logger(name)


if __name__ == "__main__":
    # 测试日志功能
    test_logger = get_logger("test")
    test_logger.debug("这是一条 DEBUG 消息")
    test_logger.info("这是一条 INFO 消息")
    test_logger.warning("这是一条 WARNING 消息")
    test_logger.error("这是一条 ERROR 消息")
    test_logger.critical("这是一条 CRITICAL 消息")


