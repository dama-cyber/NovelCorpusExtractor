"""
限流器测试
"""

import unittest
import time
from core.rate_limiter import RateLimiter, APIRateLimiter


class TestRateLimiter(unittest.TestCase):
    """限流器测试"""
    
    def test_rate_limiter_basic(self):
        """测试基本限流功能"""
        limiter = RateLimiter(max_requests=5, time_window=60)
        
        # 前5次应该允许
        for i in range(5):
            self.assertTrue(limiter.is_allowed("test"))
        
        # 第6次应该被限制
        self.assertFalse(limiter.is_allowed("test"))
    
    def test_rate_limiter_reset(self):
        """测试重置功能"""
        limiter = RateLimiter(max_requests=2, time_window=60)
        
        self.assertTrue(limiter.is_allowed("test"))
        self.assertTrue(limiter.is_allowed("test"))
        self.assertFalse(limiter.is_allowed("test"))
        
        limiter.reset("test")
        self.assertTrue(limiter.is_allowed("test"))
    
    def test_rate_limiter_remaining(self):
        """测试剩余请求数"""
        limiter = RateLimiter(max_requests=5, time_window=60)
        
        self.assertEqual(limiter.get_remaining("test"), 5)
        limiter.is_allowed("test")
        self.assertEqual(limiter.get_remaining("test"), 4)
    
    def test_api_rate_limiter(self):
        """测试API限流器"""
        api_limiter = APIRateLimiter()
        
        is_allowed, remaining = api_limiter.check_rate_limit(
            "/api/test", "user1", max_requests=3, time_window=60
        )
        self.assertTrue(is_allowed)
        self.assertEqual(remaining, 2)


if __name__ == '__main__':
    unittest.main()


