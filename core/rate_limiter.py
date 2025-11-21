"""
API限流器
实现请求频率控制和限流功能
"""

import time
from collections import defaultdict
from typing import Dict, Optional, Tuple
from threading import Lock


class RateLimiter:
    """简单的令牌桶限流器"""
    
    def __init__(self, max_requests: int = 60, time_window: int = 60):
        """
        初始化限流器
        
        Args:
            max_requests: 时间窗口内最大请求数
            time_window: 时间窗口（秒）
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = Lock()
    
    def is_allowed(self, key: str = "default") -> bool:
        """
        检查是否允许请求
        
        Args:
            key: 限流键（可用于区分不同用户或API）
        
        Returns:
            是否允许请求
        """
        with self.lock:
            now = time.time()
            # 清理过期记录
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if now - req_time < self.time_window
            ]
            
            # 检查是否超过限制
            if len(self.requests[key]) >= self.max_requests:
                return False
            
            # 记录本次请求
            self.requests[key].append(now)
            return True
    
    def get_remaining(self, key: str = "default") -> int:
        """
        获取剩余请求次数
        
        Args:
            key: 限流键
        
        Returns:
            剩余请求次数
        """
        with self.lock:
            now = time.time()
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if now - req_time < self.time_window
            ]
            return max(0, self.max_requests - len(self.requests[key]))
    
    def reset(self, key: str = "default"):
        """重置指定键的限流记录"""
        with self.lock:
            self.requests[key] = []


class APIRateLimiter:
    """API限流管理器"""
    
    def __init__(self):
        self.limiters: Dict[str, RateLimiter] = {}
        self.default_limiter = RateLimiter(max_requests=60, time_window=60)
    
    def get_limiter(self, endpoint: str, max_requests: int = 60, time_window: int = 60) -> RateLimiter:
        """
        获取或创建指定端点的限流器
        
        Args:
            endpoint: API端点路径
            max_requests: 最大请求数
            time_window: 时间窗口（秒）
        
        Returns:
            限流器实例
        """
        if endpoint not in self.limiters:
            self.limiters[endpoint] = RateLimiter(max_requests, time_window)
        return self.limiters[endpoint]
    
    def check_rate_limit(self, endpoint: str, key: str = "default", 
                        max_requests: int = 60, time_window: int = 60) -> Tuple[bool, int]:
        """
        检查是否超过限流
        
        Args:
            endpoint: API端点路径
            key: 限流键（如用户ID、IP地址等）
            max_requests: 最大请求数
            time_window: 时间窗口（秒）
        
        Returns:
            (是否允许, 剩余请求数)
        """
        limiter = self.get_limiter(endpoint, max_requests, time_window)
        is_allowed = limiter.is_allowed(key)
        remaining = limiter.get_remaining(key)
        return is_allowed, remaining


# 全局限流器实例
_global_rate_limiter: Optional[APIRateLimiter] = None


def get_rate_limiter() -> APIRateLimiter:
    """获取全局限流器实例（单例模式）"""
    global _global_rate_limiter
    if _global_rate_limiter is None:
        _global_rate_limiter = APIRateLimiter()
    return _global_rate_limiter

