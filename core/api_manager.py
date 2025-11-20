"""
高级API管理系统
支持多API提供商、负载均衡、故障转移、速率限制、成本优化等
"""

import os
import time
import asyncio
import hashlib
from typing import Dict, List, Optional, AsyncGenerator, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
from enum import Enum
import json

logger = logging.getLogger(__name__)


class APIProvider(Enum):
    """API提供商枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"  # Claude
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    COHERE = "cohere"
    MOONSHOT = "moonshot"
    ZEROONE = "zeroone"  # 零一万物
    QWEN = "qwen"  # 通义千问
    ERNIE = "ernie"  # 文心一言
    GLM = "glm"  # 智谱AI
    CUSTOM = "custom"  # 自定义API


@dataclass
class APIConfig:
    """API配置"""
    provider: APIProvider
    api_key: str
    base_url: Optional[str] = None
    model: str = "default"
    max_retries: int = 3
    timeout: int = 60
    rate_limit: int = 60  # 每分钟请求数
    cost_per_1k_tokens: float = 0.0  # 每1K token成本
    priority: int = 1  # 优先级，数字越小优先级越高
    enabled: bool = True
    metadata: Dict = field(default_factory=dict)


@dataclass
class APIStats:
    """API统计信息"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    avg_response_time: float = 0.0
    last_used: Optional[datetime] = None
    error_count: int = 0
    consecutive_errors: int = 0
    rate_limit_hits: int = 0


class RateLimiter:
    """速率限制器"""
    
    def __init__(self, max_requests: int, time_window: int = 60):
        """
        Args:
            max_requests: 时间窗口内最大请求数
            time_window: 时间窗口（秒）
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
        self.lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        """获取请求许可"""
        async with self.lock:
            now = time.time()
            # 移除过期的请求记录
            while self.requests and self.requests[0] < now - self.time_window:
                self.requests.popleft()
            
            # 检查是否超过限制
            if len(self.requests) >= self.max_requests:
                # 计算需要等待的时间
                wait_time = self.requests[0] + self.time_window - now
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    return await self.acquire()
            
            self.requests.append(now)
            return True


class APIPool:
    """API池管理器"""
    
    def __init__(self):
        self.apis: Dict[str, APIConfig] = {}
        self.stats: Dict[str, APIStats] = {}
        self.rate_limiters: Dict[str, RateLimiter] = {}
        self.cache: Dict[str, Tuple[str, datetime]] = {}  # 简单缓存
        self.cache_ttl = 3600  # 缓存1小时
    
    def add_api(self, name: str, config: APIConfig):
        """添加API到池中"""
        self.apis[name] = config
        self.stats[name] = APIStats()
        self.rate_limiters[name] = RateLimiter(
            config.rate_limit,
            time_window=60
        )
        logger.info(f"API已添加到池: {name} ({config.provider.value})")
    
    def get_available_apis(self, provider: Optional[APIProvider] = None) -> List[str]:
        """获取可用的API列表"""
        available = []
        for name, config in self.apis.items():
            if not config.enabled:
                continue
            if provider and config.provider != provider:
                continue
            
            stats = self.stats[name]
            # 如果连续错误太多，暂时禁用
            if stats.consecutive_errors >= 5:
                continue
            
            available.append(name)
        
        # 按优先级和成功率排序
        available.sort(key=lambda x: (
            self.apis[x].priority,
            -self.stats[x].successful_requests / max(self.stats[x].total_requests, 1)
        ))
        return available
    
    async def select_best_api(self, provider: Optional[APIProvider] = None) -> Optional[str]:
        """选择最佳API"""
        available = self.get_available_apis(provider)
        if not available:
            return None
        
        # 选择第一个可用的（已按优先级排序）
        for name in available:
            # 检查速率限制
            if await self.rate_limiters[name].acquire():
                return name
        
        return None
    
    def update_stats(self, name: str, success: bool, tokens: int = 0, 
                    response_time: float = 0.0, cost: float = 0.0):
        """更新API统计"""
        if name not in self.stats:
            return
        
        stats = self.stats[name]
        stats.total_requests += 1
        stats.last_used = datetime.now()
        stats.avg_response_time = (
            (stats.avg_response_time * (stats.total_requests - 1) + response_time) 
            / stats.total_requests
        )
        
        if success:
            stats.successful_requests += 1
            stats.consecutive_errors = 0
            stats.total_tokens += tokens
            stats.total_cost += cost
        else:
            stats.failed_requests += 1
            stats.error_count += 1
            stats.consecutive_errors += 1
    
    def get_cache_key(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """生成缓存键"""
        content = f"{system_prompt or ''}|{prompt}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_cached(self, cache_key: str) -> Optional[str]:
        """获取缓存结果"""
        if cache_key in self.cache:
            result, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < timedelta(seconds=self.cache_ttl):
                return result
            else:
                del self.cache[cache_key]
        return None
    
    def set_cache(self, cache_key: str, result: str):
        """设置缓存"""
        self.cache[cache_key] = (result, datetime.now())
        # 限制缓存大小
        if len(self.cache) > 1000:
            # 删除最旧的缓存
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
    
    def get_stats_report(self) -> Dict:
        """获取统计报告"""
        report = {}
        for name, stats in self.stats.items():
            config = self.apis[name]
            report[name] = {
                "provider": config.provider.value,
                "total_requests": stats.total_requests,
                "success_rate": (
                    stats.successful_requests / max(stats.total_requests, 1) * 100
                ),
                "total_tokens": stats.total_tokens,
                "total_cost": stats.total_cost,
                "avg_response_time": stats.avg_response_time,
                "consecutive_errors": stats.consecutive_errors,
                "enabled": config.enabled
            }
        return report


class UniversalAPIClient:
    """通用API客户端，支持所有主流API"""
    
    def __init__(self, api_pool: APIPool):
        self.api_pool = api_pool
        self.session_cache = {}
    
    async def _get_http_client(self):
        """获取HTTP客户端"""
        try:
            import aiohttp
            if 'session' not in self.session_cache:
                timeout = aiohttp.ClientTimeout(total=60)
                self.session_cache['session'] = aiohttp.ClientSession(timeout=timeout)
            return self.session_cache['session']
        except ImportError:
            raise ImportError("请安装aiohttp: pip install aiohttp")
    
    async def send_request(self, prompt: str, system_prompt: Optional[str] = None,
                          provider: Optional[APIProvider] = None, 
                          model: Optional[str] = None,
                          use_cache: bool = True,
                          max_retries: int = 3) -> str:
        """
        发送请求（自动选择最佳API）
        
        Args:
            prompt: 提示词
            system_prompt: 系统提示词
            provider: 指定API提供商（可选）
            model: 指定模型（可选）
            use_cache: 是否使用缓存
            max_retries: 最大重试次数
        
        Returns:
            API响应文本
        """
        # 检查缓存
        if use_cache:
            cache_key = self.api_pool.get_cache_key(prompt, system_prompt)
            cached = self.api_pool.get_cached(cache_key)
            if cached:
                logger.debug("使用缓存结果")
                return cached
        
        # 重试逻辑
        last_error = None
        for attempt in range(max_retries):
            # 选择API
            api_name = await self.api_pool.select_best_api(provider)
            if not api_name:
                raise RuntimeError("没有可用的API")
            
            config = self.api_pool.apis[api_name]
            start_time = time.time()
            
            try:
                # 调用对应的API
                result = await self._call_api(
                    api_name, config, prompt, system_prompt, model
                )
                
                # 更新统计
                response_time = time.time() - start_time
                tokens = self._estimate_tokens(prompt + (system_prompt or ""))
                cost = tokens / 1000 * config.cost_per_1k_tokens
                
                self.api_pool.update_stats(
                    api_name, True, tokens, response_time, cost
                )
                
                # 缓存结果
                if use_cache:
                    self.api_pool.set_cache(cache_key, result)
                
                return result
                
            except Exception as e:
                last_error = e
                response_time = time.time() - start_time
                self.api_pool.update_stats(api_name, False, 0, response_time, 0.0)
                
                logger.warning(f"API调用失败 ({api_name}): {e}, 尝试 {attempt + 1}/{max_retries}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # 指数退避
        
        raise RuntimeError(f"所有API调用失败: {last_error}")
    
    async def _call_api(self, api_name: str, config: APIConfig, 
                       prompt: str, system_prompt: Optional[str],
                       model: Optional[str]) -> str:
        """调用具体API"""
        model = model or config.model
        
        if config.provider == APIProvider.OPENAI:
            return await self._call_openai(config, prompt, system_prompt, model)
        elif config.provider == APIProvider.ANTHROPIC:
            return await self._call_anthropic(config, prompt, system_prompt, model)
        elif config.provider == APIProvider.GEMINI:
            return await self._call_gemini(config, prompt, system_prompt, model)
        elif config.provider == APIProvider.DEEPSEEK:
            return await self._call_deepseek(config, prompt, system_prompt, model)
        elif config.provider == APIProvider.MOONSHOT:
            return await self._call_moonshot(config, prompt, system_prompt, model)
        elif config.provider == APIProvider.ZEROONE:
            return await self._call_zeroone(config, prompt, system_prompt, model)
        elif config.provider == APIProvider.QWEN:
            return await self._call_qwen(config, prompt, system_prompt, model)
        elif config.provider == APIProvider.ERNIE:
            return await self._call_ernie(config, prompt, system_prompt, model)
        elif config.provider == APIProvider.GLM:
            return await self._call_glm(config, prompt, system_prompt, model)
        elif config.provider == APIProvider.CUSTOM:
            return await self._call_custom(config, prompt, system_prompt, model)
        else:
            raise ValueError(f"不支持的API提供商: {config.provider}")
    
    async def _call_openai(self, config: APIConfig, prompt: str, 
                          system_prompt: Optional[str], model: str) -> str:
        """调用OpenAI API"""
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=config.api_key, base_url=config.base_url)
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                timeout=config.timeout
            )
            return response.choices[0].message.content
        except ImportError:
            raise ImportError("请安装openai库: pip install openai")
    
    async def _call_anthropic(self, config: APIConfig, prompt: str,
                             system_prompt: Optional[str], model: str) -> str:
        """调用Anthropic (Claude) API"""
        try:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=config.api_key)
            
            messages = [{"role": "user", "content": prompt}]
            system = system_prompt if system_prompt else None
            
            response = await client.messages.create(
                model=model,
                max_tokens=4096,
                messages=messages,
                system=system,
                timeout=config.timeout
            )
            return response.content[0].text
        except ImportError:
            raise ImportError("请安装anthropic库: pip install anthropic")
    
    async def _call_gemini(self, config: APIConfig, prompt: str,
                          system_prompt: Optional[str], model: str) -> str:
        """调用Gemini API"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=config.api_key)
            model_obj = genai.GenerativeModel(model)
            
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = await asyncio.to_thread(
                model_obj.generate_content, full_prompt
            )
            return response.text
        except ImportError:
            raise ImportError("请安装google-generativeai库: pip install google-generativeai")
    
    async def _call_deepseek(self, config: APIConfig, prompt: str,
                            system_prompt: Optional[str], model: str) -> str:
        """调用DeepSeek API（兼容OpenAI）"""
        return await self._call_openai(config, prompt, system_prompt, model)
    
    async def _call_moonshot(self, config: APIConfig, prompt: str,
                            system_prompt: Optional[str], model: str) -> str:
        """调用Moonshot API（兼容OpenAI）"""
        config.base_url = config.base_url or "https://api.moonshot.cn/v1"
        return await self._call_openai(config, prompt, system_prompt, model)
    
    async def _call_zeroone(self, config: APIConfig, prompt: str,
                           system_prompt: Optional[str], model: str) -> str:
        """调用零一万物API（兼容OpenAI）"""
        config.base_url = config.base_url or "https://api.lingyiwanwu.com/v1"
        return await self._call_openai(config, prompt, system_prompt, model)
    
    async def _call_qwen(self, config: APIConfig, prompt: str,
                        system_prompt: Optional[str], model: str) -> str:
        """调用通义千问API"""
        session = await self._get_http_client()
        base_url = config.base_url or "https://dashscope.aliyuncs.com/api/v1"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        url = f"{base_url}/services/aigc/text-generation/generation"
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "input": {"messages": messages},
            "parameters": {}
        }
        
        async with session.post(url, json=data, headers=headers) as resp:
            result = await resp.json()
            if resp.status == 200:
                return result["output"]["choices"][0]["message"]["content"]
            else:
                raise RuntimeError(f"API调用失败: {result}")
    
    async def _call_ernie(self, config: APIConfig, prompt: str,
                         system_prompt: Optional[str], model: str) -> str:
        """调用文心一言API"""
        session = await self._get_http_client()
        base_url = config.base_url or "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat"
        
        messages = []
        if system_prompt:
            messages.append({"role": "user", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        url = f"{base_url}/{model}"
        params = {"access_token": config.api_key}
        data = {"messages": messages}
        
        async with session.post(url, json=data, params=params) as resp:
            result = await resp.json()
            if "result" in result:
                return result["result"]
            else:
                raise RuntimeError(f"API调用失败: {result}")
    
    async def _call_glm(self, config: APIConfig, prompt: str,
                       system_prompt: Optional[str], model: str) -> str:
        """调用智谱AI API"""
        session = await self._get_http_client()
        base_url = config.base_url or "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": messages
        }
        
        async with session.post(base_url, json=data, headers=headers) as resp:
            result = await resp.json()
            if resp.status == 200:
                return result["choices"][0]["message"]["content"]
            else:
                raise RuntimeError(f"API调用失败: {result}")
    
    async def _call_custom(self, config: APIConfig, prompt: str,
                          system_prompt: Optional[str], model: str) -> str:
        """调用自定义API"""
        session = await self._get_http_client()
        base_url = config.base_url or config.metadata.get("base_url")
        
        if not base_url:
            raise ValueError("自定义API需要提供base_url")
        
        # 使用自定义格式
        format_func = config.metadata.get("format_request")
        if format_func:
            data = format_func(prompt, system_prompt, model)
        else:
            # 默认OpenAI格式
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            data = {"model": model, "messages": messages}
        
        headers = config.metadata.get("headers", {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        })
        
        async with session.post(base_url, json=data, headers=headers) as resp:
            result = await resp.json()
            
            # 使用自定义解析函数
            parse_func = config.metadata.get("parse_response")
            if parse_func:
                return parse_func(result)
            else:
                # 默认解析
                if "choices" in result:
                    return result["choices"][0]["message"]["content"]
                elif "content" in result:
                    return result["content"]
                else:
                    raise RuntimeError(f"无法解析API响应: {result}")
    
    def _estimate_tokens(self, text: str) -> int:
        """估算token数量（简单实现）"""
        # 中文约1.5字符=1token，英文约4字符=1token
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        other_chars = len(text) - chinese_chars
        return int(chinese_chars / 1.5 + other_chars / 4)
    
    async def batch_request(self, prompts: List[str], 
                           system_prompt: Optional[str] = None,
                           max_concurrent: int = 10) -> List[str]:
        """批量请求（并发控制）"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def bounded_request(prompt):
            async with semaphore:
                return await self.send_request(prompt, system_prompt)
        
        tasks = [bounded_request(p) for p in prompts]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stream_request(self, prompt: str, system_prompt: Optional[str] = None,
                            provider: Optional[APIProvider] = None) -> AsyncGenerator[str, None]:
        """流式请求"""
        api_name = await self.api_pool.select_best_api(provider)
        if not api_name:
            raise RuntimeError("没有可用的API")
        
        config = self.api_pool.apis[api_name]
        
        if config.provider == APIProvider.OPENAI:
            async for chunk in self._stream_openai(config, prompt, system_prompt):
                yield chunk
        else:
            # 对于不支持流式的API，返回完整结果
            result = await self.send_request(prompt, system_prompt, provider)
            yield result
    
    async def _stream_openai(self, config: APIConfig, prompt: str,
                            system_prompt: Optional[str]) -> AsyncGenerator[str, None]:
        """OpenAI流式请求"""
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=config.api_key, base_url=config.base_url)
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            stream = await client.chat.completions.create(
                model=config.model,
                messages=messages,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except ImportError:
            raise ImportError("请安装openai库: pip install openai")

