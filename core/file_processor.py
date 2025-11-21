"""
文件处理优化模块
提供高效的文件读写和处理功能
"""

import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

logger = logging.getLogger(__name__)


class FileProcessor:
    """文件处理器（优化版）"""
    
    def __init__(self, max_workers: int = 4):
        """
        初始化文件处理器
        
        Args:
            max_workers: 最大并发工作线程数
        """
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = threading.Lock()
        self._cache: Dict[str, Any] = {}
    
    def read_json(self, file_path: Union[str, Path], use_cache: bool = True) -> Dict[str, Any]:
        """
        读取JSON文件（带缓存）
        
        Args:
            file_path: 文件路径
            use_cache: 是否使用缓存
        
        Returns:
            JSON数据字典
        """
        file_path = Path(file_path)
        cache_key = str(file_path.absolute())
        
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if use_cache:
                with self._lock:
                    self._cache[cache_key] = data
            
            return data
        except FileNotFoundError:
            logger.error(f"文件不存在: {file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败 {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"读取文件失败 {file_path}: {e}")
            raise
    
    def write_json(
        self,
        file_path: Union[str, Path],
        data: Dict[str, Any],
        indent: int = 2,
        ensure_ascii: bool = False
    ):
        """
        写入JSON文件
        
        Args:
            file_path: 文件路径
            data: 要写入的数据
            indent: 缩进空格数
            ensure_ascii: 是否确保ASCII编码
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
            
            # 更新缓存
            cache_key = str(file_path.absolute())
            with self._lock:
                self._cache[cache_key] = data
            
            logger.debug(f"JSON文件已保存: {file_path}")
        except Exception as e:
            logger.error(f"写入文件失败 {file_path}: {e}")
            raise
    
    def read_yaml(self, file_path: Union[str, Path], use_cache: bool = True) -> Dict[str, Any]:
        """
        读取YAML文件（带缓存）
        
        Args:
            file_path: 文件路径
            use_cache: 是否使用缓存
        
        Returns:
            YAML数据字典
        """
        file_path = Path(file_path)
        cache_key = str(file_path.absolute())
        
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            
            if use_cache:
                with self._lock:
                    self._cache[cache_key] = data
            
            return data
        except FileNotFoundError:
            logger.error(f"文件不存在: {file_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"YAML解析失败 {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"读取文件失败 {file_path}: {e}")
            raise
    
    def write_yaml(
        self,
        file_path: Union[str, Path],
        data: Dict[str, Any],
        default_flow_style: bool = False
    ):
        """
        写入YAML文件
        
        Args:
            file_path: 文件路径
            data: 要写入的数据
            default_flow_style: 是否使用流式风格
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=default_flow_style)
            
            # 更新缓存
            cache_key = str(file_path.absolute())
            with self._lock:
                self._cache[cache_key] = data
            
            logger.debug(f"YAML文件已保存: {file_path}")
        except Exception as e:
            logger.error(f"写入文件失败 {file_path}: {e}")
            raise
    
    def read_json_batch(
        self,
        file_paths: List[Union[str, Path]],
        use_cache: bool = True
    ) -> Dict[str, Dict[str, Any]]:
        """
        批量读取JSON文件
        
        Args:
            file_paths: 文件路径列表
            use_cache: 是否使用缓存
        
        Returns:
            文件路径到数据的映射字典
        """
        results = {}
        futures = {}
        
        for file_path in file_paths:
            future = self.executor.submit(self.read_json, file_path, use_cache)
            futures[future] = file_path
        
        for future in as_completed(futures):
            file_path = futures[future]
            try:
                results[str(file_path)] = future.result()
            except Exception as e:
                logger.error(f"读取文件失败 {file_path}: {e}")
        
        return results
    
    def write_json_batch(
        self,
        file_data: Dict[Union[str, Path], Dict[str, Any]],
        indent: int = 2
    ):
        """
        批量写入JSON文件
        
        Args:
            file_data: 文件路径到数据的映射字典
            indent: 缩进空格数
        """
        futures = []
        
        for file_path, data in file_data.items():
            future = self.executor.submit(
                self.write_json, file_path, data, indent
            )
            futures.append(future)
        
        # 等待所有写入完成
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"写入文件失败: {e}")
    
    def clear_cache(self, file_path: Optional[Union[str, Path]] = None):
        """
        清除缓存
        
        Args:
            file_path: 要清除的文件路径（None表示清除所有缓存）
        """
        with self._lock:
            if file_path is None:
                self._cache.clear()
            else:
                cache_key = str(Path(file_path).absolute())
                self._cache.pop(cache_key, None)
    
    def invalidate_cache(self, file_path: Union[str, Path]):
        """使指定文件的缓存失效"""
        self.clear_cache(file_path)
    
    def close(self):
        """关闭文件处理器"""
        self.executor.shutdown(wait=True)
        self.clear_cache()


# 全局文件处理器实例
_file_processor: Optional[FileProcessor] = None


def get_file_processor() -> FileProcessor:
    """获取文件处理器实例（单例模式）"""
    global _file_processor
    if _file_processor is None:
        _file_processor = FileProcessor()
    return _file_processor


