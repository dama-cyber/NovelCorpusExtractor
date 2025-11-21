"""
缓存管理器
实现多级缓存机制，提高系统性能
"""

import time
import hashlib
import json
import logging
from typing import Dict, Optional, Any, Callable
from pathlib import Path
from threading import Lock
from collections import OrderedDict

logger = logging.getLogger(__name__)


class LRUCache:
    """LRU（最近最少使用）缓存"""
    
    def __init__(self, max_size: int = 100):
        """
        初始化LRU缓存
        
        Args:
            max_size: 最大缓存项数量
        """
        self.max_size = max_size
        self.cache: OrderedDict = OrderedDict()
        self.lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self.lock:
            if key in self.cache:
                # 移动到末尾（最近使用）
                self.cache.move_to_end(key)
                return self.cache[key]
            return None
    
    def set(self, key: str, value: Any):
        """设置缓存值"""
        with self.lock:
            if key in self.cache:
                # 更新现有项
                self.cache.move_to_end(key)
                self.cache[key] = value
            else:
                # 添加新项
                if len(self.cache) >= self.max_size:
                    # 删除最旧的项（第一个）
                    self.cache.popitem(last=False)
                self.cache[key] = value
    
    def delete(self, key: str):
        """删除缓存项"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
    
    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
    
    def size(self) -> int:
        """获取缓存大小"""
        return len(self.cache)


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, memory_cache_size: int = 100, disk_cache_dir: str = "cache"):
        """
        初始化缓存管理器
        
        Args:
            memory_cache_size: 内存缓存大小
            disk_cache_dir: 磁盘缓存目录
        """
        self.memory_cache = LRUCache(memory_cache_size)
        self.disk_cache_dir = Path(disk_cache_dir)
        self.disk_cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = 3600  # 默认TTL（秒）
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = {
            "prefix": prefix,
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True, ensure_ascii=False)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def _get_disk_cache_path(self, key: str) -> Path:
        """获取磁盘缓存文件路径"""
        return self.disk_cache_dir / f"{key}.json"
    
    def get(self, key: str, use_disk: bool = True) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            use_disk: 是否使用磁盘缓存
        
        Returns:
            缓存值，如果不存在则返回None
        """
        # 先检查内存缓存
        value = self.memory_cache.get(key)
        if value is not None:
            return value
        
        # 检查磁盘缓存
        if use_disk:
            cache_path = self._get_disk_cache_path(key)
            if cache_path.exists():
                try:
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    # 检查TTL
                    if 'expires_at' in cache_data:
                        if time.time() > cache_data['expires_at']:
                            # 已过期，删除
                            cache_path.unlink()
                            return None
                    
                    value = cache_data.get('value')
                    # 加载到内存缓存
                    if value is not None:
                        self.memory_cache.set(key, value)
                    return value
                except Exception as e:
                    logger.warning(f"读取磁盘缓存失败 {key}: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, use_disk: bool = True):
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒），None表示使用默认值
            use_disk: 是否使用磁盘缓存
        """
        # 设置内存缓存
        self.memory_cache.set(key, value)
        
        # 设置磁盘缓存
        if use_disk:
            cache_path = self._get_disk_cache_path(key)
            ttl = ttl or self.default_ttl
            cache_data = {
                'value': value,
                'created_at': time.time(),
                'expires_at': time.time() + ttl
            }
            try:
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, ensure_ascii=False)
            except Exception as e:
                logger.warning(f"写入磁盘缓存失败 {key}: {e}")
    
    def delete(self, key: str):
        """删除缓存项"""
        self.memory_cache.delete(key)
        cache_path = self._get_disk_cache_path(key)
        if cache_path.exists():
            try:
                cache_path.unlink()
            except Exception as e:
                logger.warning(f"删除磁盘缓存失败 {key}: {e}")
    
    def clear(self, memory_only: bool = False):
        """
        清空缓存
        
        Args:
            memory_only: 是否只清空内存缓存
        """
        self.memory_cache.clear()
        if not memory_only:
            try:
                for cache_file in self.disk_cache_dir.glob("*.json"):
                    cache_file.unlink()
            except Exception as e:
                logger.warning(f"清空磁盘缓存失败: {e}")
    
    def cached(self, prefix: str = "default", ttl: Optional[int] = None, use_disk: bool = True):
        """
        缓存装饰器
        
        Args:
            prefix: 缓存键前缀
            ttl: 生存时间（秒）
            use_disk: 是否使用磁盘缓存
        """
        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                # 生成缓存键
                cache_key = self._generate_key(prefix, *args, **kwargs)
                
                # 尝试从缓存获取
                cached_value = self.get(cache_key, use_disk=use_disk)
                if cached_value is not None:
                    return cached_value
                
                # 执行函数
                result = func(*args, **kwargs)
                
                # 保存到缓存
                self.set(cache_key, result, ttl=ttl, use_disk=use_disk)
                
                return result
            return wrapper
        return decorator


# 全局缓存管理器实例
_global_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """获取缓存管理器实例（单例模式）"""
    global _global_cache_manager
    if _global_cache_manager is None:
        _global_cache_manager = CacheManager()
    return _global_cache_manager


