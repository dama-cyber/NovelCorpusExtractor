"""
通用工具函数模块
提供项目中常用的工具函数，减少代码重复
"""

import json
import yaml
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def generate_id() -> str:
    """
    生成唯一ID（UUID）
    
    Returns:
        UUID字符串
    """
    return str(uuid.uuid4())


def ensure_dir(path: Union[str, Path]) -> Path:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        path: 目录路径
    
    Returns:
        Path对象
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_read_json(file_path: Union[str, Path], default: Dict = None) -> Dict[str, Any]:
    """
    安全读取JSON文件
    
    Args:
        file_path: 文件路径
        default: 默认值（如果文件不存在或读取失败）
    
    Returns:
        JSON数据字典
    """
    file_path = Path(file_path)
    default = default or {}
    
    if not file_path.exists():
        return default
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f) or default
    except Exception as e:
        logger.warning(f"读取JSON文件失败 {file_path}: {e}")
        return default


def safe_write_json(
    file_path: Union[str, Path],
    data: Dict[str, Any],
    indent: int = 2,
    ensure_ascii: bool = False
) -> bool:
    """
    安全写入JSON文件
    
    Args:
        file_path: 文件路径
        data: 要写入的数据
        indent: 缩进空格数
        ensure_ascii: 是否确保ASCII编码
    
    Returns:
        是否成功
    """
    file_path = Path(file_path)
    ensure_dir(file_path.parent)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
        return True
    except Exception as e:
        logger.error(f"写入JSON文件失败 {file_path}: {e}")
        return False


def safe_read_yaml(file_path: Union[str, Path], default: Dict = None) -> Dict[str, Any]:
    """
    安全读取YAML文件
    
    Args:
        file_path: 文件路径
        default: 默认值（如果文件不存在或读取失败）
    
    Returns:
        YAML数据字典
    """
    file_path = Path(file_path)
    default = default or {}
    
    if not file_path.exists():
        return default
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or default
    except Exception as e:
        logger.warning(f"读取YAML文件失败 {file_path}: {e}")
        return default


def safe_write_yaml(
    file_path: Union[str, Path],
    data: Dict[str, Any],
    default_flow_style: bool = False
) -> bool:
    """
    安全写入YAML文件
    
    Args:
        file_path: 文件路径
        data: 要写入的数据
        default_flow_style: 是否使用流式风格
    
    Returns:
        是否成功
    """
    file_path = Path(file_path)
    ensure_dir(file_path.parent)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=default_flow_style)
        return True
    except Exception as e:
        logger.error(f"写入YAML文件失败 {file_path}: {e}")
        return False


def get_timestamp() -> str:
    """
    获取当前时间戳（ISO格式）
    
    Returns:
        ISO格式时间戳字符串
    """
    return datetime.now().isoformat()


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    合并多个字典
    
    Args:
        *dicts: 要合并的字典
    
    Returns:
        合并后的字典
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def deep_merge_dicts(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    """
    深度合并字典（递归合并嵌套字典）
    
    Args:
        base: 基础字典
        update: 要合并的字典
    
    Returns:
        合并后的字典
    """
    result = base.copy()
    
    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def filter_dict(data: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """
    过滤字典，只保留指定的键
    
    Args:
        data: 原始字典
        keys: 要保留的键列表
    
    Returns:
        过滤后的字典
    """
    return {k: v for k, v in data.items() if k in keys}


def exclude_dict(data: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """
    排除字典中的指定键
    
    Args:
        data: 原始字典
        keys: 要排除的键列表
    
    Returns:
        排除后的字典
    """
    return {k: v for k, v in data.items() if k not in keys}


def validate_uuid(uuid_string: str) -> bool:
    """
    验证UUID格式
    
    Args:
        uuid_string: UUID字符串
    
    Returns:
        是否为有效UUID
    """
    try:
        uuid.UUID(uuid_string)
        return True
    except (ValueError, AttributeError):
        return False


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除不安全字符
    
    Args:
        filename: 原始文件名
    
    Returns:
        清理后的文件名
    """
    import re
    # 移除或替换不安全字符
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 移除前后空格和点
    filename = filename.strip(' .')
    return filename


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    将列表分割成指定大小的块
    
    Args:
        lst: 要分割的列表
        chunk_size: 每块的大小
    
    Returns:
        分割后的列表列表
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    展平嵌套字典
    
    Args:
        d: 嵌套字典
        parent_key: 父键前缀
        sep: 分隔符
    
    Returns:
        展平后的字典
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def safe_get(data: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """
    安全获取嵌套字典的值
    
    Args:
        data: 字典
        *keys: 键路径
        default: 默认值
    
    Returns:
        值或默认值
    """
    result = data
    for key in keys:
        if isinstance(result, dict) and key in result:
            result = result[key]
        else:
            return default
    return result


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 字节数
    
    Returns:
        格式化后的字符串（如 "1.5 MB"）
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def truncate_string(s: str, max_length: int, suffix: str = "...") -> str:
    """
    截断字符串
    
    Args:
        s: 原始字符串
        max_length: 最大长度
        suffix: 后缀
    
    Returns:
        截断后的字符串
    """
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix


