"""
性能测试
测试系统性能和负载能力
"""

import unittest
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.rate_limiter import get_rate_limiter
from core.cache_manager import get_cache_manager
from core.performance_monitor import get_performance_monitor


class TestPerformance(unittest.TestCase):
    """性能测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.rate_limiter = get_rate_limiter()
        self.cache_manager = get_cache_manager()
        self.performance_monitor = get_performance_monitor()
    
    def test_rate_limiter_performance(self):
        """测试限流器性能"""
        start_time = time.time()
        
        # 执行1000次检查
        for _ in range(1000):
            self.rate_limiter.check_rate_limit("test_key")
        
        elapsed = time.time() - start_time
        # 应该在1秒内完成
        self.assertLess(elapsed, 1.0, f"限流器性能测试耗时 {elapsed} 秒")
    
    def test_cache_performance(self):
        """测试缓存性能"""
        start_time = time.time()
        
        # 写入1000个缓存项
        for i in range(1000):
            self.cache_manager.set(f"key_{i}", f"value_{i}", ttl=60)
        
        # 读取1000个缓存项
        for i in range(1000):
            self.cache_manager.get(f"key_{i}")
        
        elapsed = time.time() - start_time
        # 应该在2秒内完成
        self.assertLess(elapsed, 2.0, f"缓存性能测试耗时 {elapsed} 秒")
    
    def test_concurrent_requests(self):
        """测试并发请求处理"""
        def make_request(request_id):
            """模拟请求"""
            start = time.time()
            self.rate_limiter.check_rate_limit(f"key_{request_id}")
            self.cache_manager.set(f"req_{request_id}", "data", ttl=60)
            return time.time() - start
        
        # 并发执行100个请求
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(100)]
            results = [f.result() for f in as_completed(futures)]
        
        # 平均响应时间应该小于0.1秒
        avg_time = sum(results) / len(results)
        self.assertLess(avg_time, 0.1, f"平均响应时间 {avg_time} 秒")
    
    def test_memory_usage(self):
        """测试内存使用"""
        import sys
        
        # 记录初始内存
        initial_size = sys.getsizeof(self.cache_manager._cache)
        
        # 添加大量数据
        for i in range(10000):
            self.cache_manager.set(f"large_key_{i}", "x" * 100, ttl=60)
        
        # 记录最终内存
        final_size = sys.getsizeof(self.cache_manager._cache)
        
        # 内存增长应该合理（小于100MB）
        size_diff = (final_size - initial_size) / (1024 * 1024)
        self.assertLess(size_diff, 100, f"内存增长 {size_diff} MB")


if __name__ == '__main__':
    unittest.main()


