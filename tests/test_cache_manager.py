"""
缓存管理器测试
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from core.cache_manager import LRUCache, CacheManager


class TestLRUCache(unittest.TestCase):
    """LRU缓存测试"""
    
    def test_lru_cache_basic(self):
        """测试基本缓存功能"""
        cache = LRUCache(max_size=3)
        
        cache.set("key1", "value1")
        self.assertEqual(cache.get("key1"), "value1")
        
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        # 添加第4个，应该删除key1
        cache.set("key4", "value4")
        self.assertIsNone(cache.get("key1"))
        self.assertEqual(cache.get("key4"), "value4")
    
    def test_lru_cache_delete(self):
        """测试删除功能"""
        cache = LRUCache(max_size=3)
        
        cache.set("key1", "value1")
        cache.delete("key1")
        self.assertIsNone(cache.get("key1"))
    
    def test_lru_cache_clear(self):
        """测试清空功能"""
        cache = LRUCache(max_size=3)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        
        self.assertEqual(cache.size(), 0)
        self.assertIsNone(cache.get("key1"))


class TestCacheManager(unittest.TestCase):
    """缓存管理器测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_manager = CacheManager(
            memory_cache_size=10,
            disk_cache_dir=self.temp_dir
        )
    
    def tearDown(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir)
    
    def test_cache_manager_basic(self):
        """测试基本缓存功能"""
        self.cache_manager.set("test_key", "test_value")
        self.assertEqual(self.cache_manager.get("test_key"), "test_value")
    
    def test_cache_manager_ttl(self):
        """测试TTL功能"""
        self.cache_manager.set("test_key", "test_value", ttl=1)
        self.assertEqual(self.cache_manager.get("test_key"), "test_value")
        
        # 等待过期
        import time
        time.sleep(1.1)
        self.assertIsNone(self.cache_manager.get("test_key"))


if __name__ == '__main__':
    unittest.main()


