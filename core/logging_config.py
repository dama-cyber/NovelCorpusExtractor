"""
日志配置模块
支持日志轮转、文件大小限制等功能
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_file: str = "novel_extractor.log",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    console_output: bool = True
) -> logging.Logger:
    """
    设置日志配置，支持日志轮转
    
    Args:
        log_level: 日志级别 (DEBUG/INFO/WARNING/ERROR)
        log_file: 日志文件路径
        max_bytes: 单个日志文件最大大小（字节）
        backup_count: 保留的备份文件数量
        console_output: 是否输出到控制台
    
    Returns:
        配置好的logger实例
    """
    # 创建日志目录（如果不存在）
    log_path = Path(log_file)
    if log_path.parent != Path("."):
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 获取日志级别
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # 配置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(log_format, date_format)
    
    # 创建处理器列表
    handlers = []
    
    # 文件处理器（带轮转）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    handlers.append(file_handler)
    
    # 控制台处理器（可选）
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        handlers.append(console_handler)
    
    # 配置根logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 清除现有处理器
    root_logger.handlers.clear()
    
    # 添加新处理器
    for handler in handlers:
        root_logger.addHandler(handler)
    
    # 设置第三方库的日志级别
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的logger"""
    return logging.getLogger(name)


