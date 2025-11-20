"""
增强的模型接口
集成UniversalAPIClient，提供统一的LLMClient接口
"""

from typing import Optional, AsyncGenerator
import logging
from .api_manager import (
    UniversalAPIClient, APIPool, APIConfig, APIProvider
)
from .model_interface import LLMClient

logger = logging.getLogger(__name__)


class EnhancedLLMClient(LLMClient):
    """增强的LLM客户端，支持多API、负载均衡等"""
    
    def __init__(self, api_pool: APIPool, default_provider: Optional[APIProvider] = None):
        """
        初始化增强客户端
        Args:
            api_pool: API池
            default_provider: 默认API提供商
        """
        self.api_pool = api_pool
        self.client = UniversalAPIClient(api_pool)
        self.default_provider = default_provider
    
    def send_prompt(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """同步发送提示词（使用异步实现）"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.send_prompt_async(prompt, system_prompt, **kwargs)
        )
    
    async def send_prompt_async(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """异步发送提示词"""
        provider = kwargs.get("provider")
        if isinstance(provider, str):
            provider = APIProvider(provider)
        elif provider is None:
            provider = self.default_provider
        
        model = kwargs.get("model")
        use_cache = kwargs.get("use_cache", True)
        max_retries = kwargs.get("max_retries", 3)
        
        return await self.client.send_request(
            prompt=prompt,
            system_prompt=system_prompt,
            provider=provider,
            model=model,
            use_cache=use_cache,
            max_retries=max_retries
        )
    
    async def stream_prompt(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> AsyncGenerator[str, None]:
        """流式发送提示词"""
        provider = kwargs.get("provider")
        if isinstance(provider, str):
            provider = APIProvider(provider)
        elif provider is None:
            provider = self.default_provider
        
        async for chunk in self.client.stream_request(prompt, system_prompt, provider):
            yield chunk
    
    def get_stats(self) -> dict:
        """获取API统计信息"""
        return self.api_pool.get_stats_report()
    
    def add_api(self, name: str, config: APIConfig):
        """添加API到池中"""
        self.api_pool.add_api(name, config)


def create_enhanced_client_from_config(configs: list) -> EnhancedLLMClient:
    """
    从配置列表创建增强客户端
    Args:
        configs: API配置列表，每个配置包含provider, api_key等
    Returns:
        EnhancedLLMClient实例
    """
    api_pool = APIPool()
    
    for i, cfg in enumerate(configs):
        provider_str = cfg.get("provider", "openai").lower()
        try:
            provider = APIProvider(provider_str)
        except ValueError:
            logger.warning(f"未知的API提供商: {provider_str}，跳过")
            continue
        
        api_config = APIConfig(
            provider=provider,
            api_key=cfg.get("api_key", ""),
            base_url=cfg.get("base_url"),
            model=cfg.get("model", "default"),
            max_retries=cfg.get("max_retries", 3),
            timeout=cfg.get("timeout", 60),
            rate_limit=cfg.get("rate_limit", 60),
            cost_per_1k_tokens=cfg.get("cost_per_1k_tokens", 0.0),
            priority=cfg.get("priority", i + 1),
            enabled=cfg.get("enabled", True),
            metadata=cfg.get("metadata", {})
        )
        
        api_name = cfg.get("name", f"{provider.value}_{i}")
        api_pool.add_api(api_name, api_config)
    
    default_provider = None
    if configs:
        default_provider = APIProvider(configs[0].get("provider", "openai").lower())
    
    return EnhancedLLMClient(api_pool, default_provider)

