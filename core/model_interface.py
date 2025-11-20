"""
多模型后端适配接口
支持OpenAI、Gemini、DeepSeek等多种模型
"""

import os
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, AsyncGenerator
import logging

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    """抽象LLM客户端接口"""
    
    @abstractmethod
    def send_prompt(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """发送提示词并返回响应"""
        pass
    
    @abstractmethod
    async def send_prompt_async(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """异步发送提示词"""
        pass
    
    @abstractmethod
    async def stream_prompt(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> AsyncGenerator[str, None]:
        """流式发送提示词"""
        pass


class OpenAIClient(LLMClient):
    """OpenAI模型客户端"""
    
    def __init__(self, api_key: str, model: str = "gpt-4", base_url: Optional[str] = None):
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
            self.model = model
        except ImportError:
            raise ImportError("请安装openai库: pip install openai")
    
    def send_prompt(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {e}")
            raise
    
    async def send_prompt_async(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        import asyncio
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=self.client.api_key, base_url=self.client.base_url)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI异步API调用失败: {e}")
            raise
    
    async def stream_prompt(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> AsyncGenerator[str, None]:
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=self.client.api_key, base_url=self.client.base_url)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            stream = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                **kwargs
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"OpenAI流式API调用失败: {e}")
            raise


class GeminiClient(LLMClient):
    """Google Gemini模型客户端"""
    
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model)
            self.model_name = model
        except ImportError:
            raise ImportError("请安装google-generativeai库: pip install google-generativeai")
    
    def send_prompt(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        try:
            response = self.model.generate_content(full_prompt, **kwargs)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API调用失败: {e}")
            raise
    
    async def send_prompt_async(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        # Gemini异步调用实现
        return self.send_prompt(prompt, system_prompt, **kwargs)
    
    async def stream_prompt(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> AsyncGenerator[str, None]:
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        try:
            response = self.model.generate_content(full_prompt, stream=True, **kwargs)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Gemini流式API调用失败: {e}")
            raise


class DeepSeekClient(LLMClient):
    """DeepSeek模型客户端（兼容OpenAI接口）"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com", model: str = "deepseek-chat"):
        self.client = OpenAIClient(api_key=api_key, model=model, base_url=base_url)
    
    def send_prompt(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        return self.client.send_prompt(prompt, system_prompt, **kwargs)
    
    async def send_prompt_async(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        return await self.client.send_prompt_async(prompt, system_prompt, **kwargs)
    
    async def stream_prompt(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> AsyncGenerator[str, None]:
        async for chunk in self.client.stream_prompt(prompt, system_prompt, **kwargs):
            yield chunk


class ModelFactory:
    """模型工厂类，根据配置创建对应的客户端"""
    
    @staticmethod
    def create_client(config: Dict) -> LLMClient:
        """根据配置创建模型客户端"""
        model_type = config.get("model", "openai").lower()
        
        # 尝试从配置或环境变量获取API密钥
        api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY")
        if model_type == "gemini":
            api_key = api_key or os.getenv("GEMINI_API_KEY")
        elif model_type == "deepseek":
            api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        
        if not api_key:
            raise ValueError(
                f"未找到{model_type}的API密钥。"
                f"请在配置文件中设置api_key，或设置环境变量："
                f"{'OPENAI_API_KEY' if model_type == 'openai' else 'GEMINI_API_KEY' if model_type == 'gemini' else 'DEEPSEEK_API_KEY'}"
            )
        
        if model_type == "openai" or model_type.startswith("gpt"):
            model_name = config.get("model_name", "gpt-4")
            base_url = config.get("base_url", None)
            return OpenAIClient(api_key=api_key, model=model_name, base_url=base_url)
        
        elif model_type == "gemini":
            model_name = config.get("model_name", "gemini-pro")
            return GeminiClient(api_key=api_key, model=model_name)
        
        elif model_type == "deepseek":
            base_url = config.get("base_url", "https://api.deepseek.com")
            model_name = config.get("model_name", "deepseek-chat")
            return DeepSeekClient(api_key=api_key, base_url=base_url, model=model_name)
        
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")

