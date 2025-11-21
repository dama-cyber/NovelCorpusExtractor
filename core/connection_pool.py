"""
连接池管理模块
管理HTTP连接池，优化API调用性能
"""

import asyncio
from typing import Optional, Dict, Any
import logging
from contextlib import asynccontextmanager

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    logging.warning("aiohttp未安装，连接池功能不可用")

logger = logging.getLogger(__name__)


class ConnectionPool:
    """HTTP连接池管理器"""
    
    def __init__(
        self,
        max_connections: int = 100,
        max_connections_per_host: int = 30,
        timeout: int = 30,
        keepalive_timeout: int = 30
    ):
        """
        初始化连接池
        
        Args:
            max_connections: 最大连接数
            max_connections_per_host: 每个主机的最大连接数
            timeout: 请求超时时间（秒）
            keepalive_timeout: 连接保持时间（秒）
        """
        if not AIOHTTP_AVAILABLE:
            raise ImportError("请安装aiohttp: pip install aiohttp")
        
        self.max_connections = max_connections
        self.max_connections_per_host = max_connections_per_host
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.keepalive_timeout = keepalive_timeout
        
        self._session: Optional[aiohttp.ClientSession] = None
        self._lock = asyncio.Lock()
    
    async def get_session(self) -> aiohttp.ClientSession:
        """
        获取连接会话（单例模式）
        
        Returns:
            aiohttp.ClientSession实例
        """
        if self._session is None or self._session.closed:
            async with self._lock:
                if self._session is None or self._session.closed:
                    connector = aiohttp.TCPConnector(
                        limit=self.max_connections,
                        limit_per_host=self.max_connections_per_host,
                        keepalive_timeout=self.keepalive_timeout
                    )
                    
                    self._session = aiohttp.ClientSession(
                        connector=connector,
                        timeout=self.timeout
                    )
                    logger.info("创建新的HTTP连接池")
        
        return self._session
    
    async def close(self):
        """关闭连接池"""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("关闭HTTP连接池")
    
    @asynccontextmanager
    async def request(
        self,
        method: str,
        url: str,
        **kwargs
    ):
        """
        执行HTTP请求（上下文管理器）
        
        Args:
            method: HTTP方法
            url: 请求URL
            **kwargs: 其他请求参数
        
        Yields:
            响应对象
        """
        session = await self.get_session()
        async with session.request(method, url, **kwargs) as response:
            yield response
    
    async def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        执行GET请求
        
        Args:
            url: 请求URL
            **kwargs: 其他请求参数
        
        Returns:
            响应数据（JSON格式）
        """
        async with self.request('GET', url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()
    
    async def post(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        执行POST请求
        
        Args:
            url: 请求URL
            **kwargs: 其他请求参数
        
        Returns:
            响应数据（JSON格式）
        """
        async with self.request('POST', url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()
    
    async def put(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        执行PUT请求
        
        Args:
            url: 请求URL
            **kwargs: 其他请求参数
        
        Returns:
            响应数据（JSON格式）
        """
        async with self.request('PUT', url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()
    
    async def delete(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        执行DELETE请求
        
        Args:
            url: 请求URL
            **kwargs: 其他请求参数
        
        Returns:
            响应数据（JSON格式）
        """
        async with self.request('DELETE', url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()


# 全局连接池实例
_connection_pool: Optional[ConnectionPool] = None


def get_connection_pool() -> ConnectionPool:
    """获取连接池实例（单例模式）"""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = ConnectionPool()
    return _connection_pool


