"""
统一错误处理模块
提供统一的错误处理装饰器和中间件
"""

import logging
import traceback
from functools import wraps
from typing import Callable, Any
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from core.exceptions import (
    NovelExtractorError,
    ConfigurationError,
    APIError,
    ValidationError,
    FileProcessingError,
    WorkflowError
)

logger = logging.getLogger(__name__)


# 异常到HTTP状态码的映射
EXCEPTION_STATUS_MAP = {
    ValidationError: 400,
    ConfigurationError: 500,
    FileProcessingError: 400,
    WorkflowError: 500,
    APIError: lambda e: e.status_code if hasattr(e, 'status_code') else 500,
    NovelExtractorError: 500,
}


def get_status_code(exception: Exception) -> int:
    """获取异常对应的HTTP状态码"""
    exception_type = type(exception)
    
    # 检查直接映射
    if exception_type in EXCEPTION_STATUS_MAP:
        handler = EXCEPTION_STATUS_MAP[exception_type]
        if callable(handler):
            return handler(exception)
        return handler
    
    # 检查父类映射
    for exc_type, status_code in EXCEPTION_STATUS_MAP.items():
        if isinstance(exception, exc_type):
            if callable(status_code):
                return status_code(exception)
            return status_code
    
    # 默认状态码
    return 500


def error_handler(func: Callable) -> Callable:
    """
    错误处理装饰器
    统一处理函数中的异常，转换为HTTP响应
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            # FastAPI的HTTPException直接抛出
            raise
        except NovelExtractorError as e:
            # 自定义异常转换为HTTPException
            status_code = get_status_code(e)
            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status_code,
                detail=str(e)
            )
        except Exception as e:
            # 其他异常记录详细信息并返回500
            logger.error(f"未处理的异常: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"内部服务器错误: {str(e)}"
            )
    
    return wrapper


def sync_error_handler(func: Callable) -> Callable:
    """
    同步函数错误处理装饰器
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPException:
            raise
        except NovelExtractorError as e:
            status_code = get_status_code(e)
            logger.error(f"{type(e).__name__}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status_code,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"未处理的异常: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"内部服务器错误: {str(e)}"
            )
    
    return wrapper


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    全局异常处理器
    用于FastAPI的异常处理
    """
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.status_code,
                    "message": exc.detail,
                    "type": "HTTPException"
                }
            }
        )
    
    if isinstance(exc, NovelExtractorError):
        status_code = get_status_code(exc)
        logger.error(f"{type(exc).__name__}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": status_code,
                    "message": str(exc),
                    "type": type(exc).__name__
                }
            }
        )
    
    # 未处理的异常
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "内部服务器错误",
                "type": type(exc).__name__
            }
        }
    )


def validate_request_data(data: dict, required_fields: list, field_types: dict = None):
    """
    验证请求数据
    
    Args:
        data: 要验证的数据字典
        required_fields: 必需字段列表
        field_types: 字段类型映射 {field_name: type}
    
    Raises:
        ValidationError: 验证失败时抛出
    """
    if not isinstance(data, dict):
        raise ValidationError("请求数据必须是字典类型")
    
    # 检查必需字段
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValidationError(f"缺少必需字段: {', '.join(missing_fields)}")
    
    # 检查字段类型
    if field_types:
        for field, expected_type in field_types.items():
            if field in data and not isinstance(data[field], expected_type):
                raise ValidationError(
                    f"字段 '{field}' 类型错误，期望 {expected_type.__name__}，"
                    f"实际 {type(data[field]).__name__}"
                )


def safe_execute(func: Callable, *args, default_return=None, **kwargs) -> Any:
    """
    安全执行函数，捕获所有异常
    
    Args:
        func: 要执行的函数
        *args: 位置参数
        default_return: 异常时的默认返回值
        **kwargs: 关键字参数
    
    Returns:
        函数返回值或默认返回值
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"安全执行失败: {e}")
        return default_return


