"""
API优化器
实现智能路由、成本优化、性能优化等高级功能
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
from .api_manager import APIPool, APIConfig, APIProvider, APIStats

logger = logging.getLogger(__name__)


@dataclass
class OptimizationStrategy:
    """优化策略"""
    minimize_cost: bool = False  # 最小化成本
    maximize_speed: bool = False  # 最大化速度
    maximize_quality: bool = False  # 最大化质量
    balance: bool = True  # 平衡模式


class APIOptimizer:
    """API优化器"""
    
    def __init__(self, api_pool: APIPool):
        self.api_pool = api_pool
        self.strategy = OptimizationStrategy()
    
    def set_strategy(self, strategy: OptimizationStrategy):
        """设置优化策略"""
        self.strategy = strategy
    
    async def select_optimal_api(self, prompt_length: int, 
                                 provider: Optional[APIProvider] = None) -> Optional[str]:
        """
        根据优化策略选择最优API
        Args:
            prompt_length: 提示词长度（字符数）
            provider: 指定提供商（可选）
        """
        available = self.api_pool.get_available_apis(provider)
        if not available:
            return None
        
        # 估算token数
        estimated_tokens = prompt_length // 2  # 简单估算
        
        # 根据策略选择
        if self.strategy.minimize_cost:
            return self._select_by_cost(available, estimated_tokens)
        elif self.strategy.maximize_speed:
            return self._select_by_speed(available)
        elif self.strategy.maximize_quality:
            return self._select_by_quality(available)
        else:  # balance
            return self._select_balanced(available, estimated_tokens)
    
    def _select_by_cost(self, available: List[str], tokens: int) -> Optional[str]:
        """按成本选择"""
        best_api = None
        best_cost = float('inf')
        
        for name in available:
            config = self.api_pool.apis[name]
            cost = (tokens / 1000) * config.cost_per_1k_tokens
            
            if cost < best_cost:
                best_cost = cost
                best_api = name
        
        return best_api
    
    def _select_by_speed(self, available: List[str]) -> Optional[str]:
        """按速度选择"""
        best_api = None
        best_time = float('inf')
        
        for name in available:
            stats = self.api_pool.stats[name]
            if stats.total_requests > 0:
                avg_time = stats.avg_response_time
                if avg_time < best_time:
                    best_time = avg_time
                    best_api = name
        
        # 如果没有统计数据，按优先级选择
        if not best_api and available:
            return available[0]
        
        return best_api
    
    def _select_by_quality(self, available: List[str]) -> Optional[str]:
        """按质量选择（成功率）"""
        best_api = None
        best_rate = 0.0
        
        for name in available:
            stats = self.api_pool.stats[name]
            if stats.total_requests > 0:
                success_rate = stats.successful_requests / stats.total_requests
                if success_rate > best_rate:
                    best_rate = success_rate
                    best_api = name
        
        if not best_api and available:
            return available[0]
        
        return best_api
    
    def _select_balanced(self, available: List[str], tokens: int) -> Optional[str]:
        """平衡选择（综合考虑成本、速度、质量）"""
        scores = {}
        
        for name in available:
            config = self.api_pool.apis[name]
            stats = self.api_pool.stats[name]
            
            # 成本分数（越低越好，转换为越高越好）
            cost = (tokens / 1000) * config.cost_per_1k_tokens
            cost_score = 1.0 / (cost + 0.001)  # 避免除零
            
            # 速度分数（越快越好）
            if stats.total_requests > 0:
                speed_score = 1.0 / (stats.avg_response_time + 0.1)
            else:
                speed_score = 1.0
            
            # 质量分数（成功率）
            if stats.total_requests > 0:
                quality_score = stats.successful_requests / stats.total_requests
            else:
                quality_score = 1.0
            
            # 综合分数（加权平均）
            total_score = (
                cost_score * 0.3 +  # 成本权重30%
                speed_score * 0.4 +  # 速度权重40%
                quality_score * 0.3  # 质量权重30%
            )
            
            scores[name] = total_score
        
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return available[0] if available else None
    
    async def optimize_batch_requests(self, prompts: List[str],
                                     max_concurrent: Optional[int] = None) -> List[Tuple[str, str]]:
        """
        优化批量请求
        Returns:
            [(api_name, result), ...] 列表
        """
        if max_concurrent is None:
            # 根据可用API数量自动调整
            available_count = len(self.api_pool.get_available_apis())
            max_concurrent = min(available_count * 10, 50)
        
        semaphore = asyncio.Semaphore(max_concurrent)
        results = []
        
        async def process_prompt(prompt):
            async with semaphore:
                api_name = await self.select_optimal_api(len(prompt))
                if api_name:
                    # 这里需要调用实际的API，简化处理
                    return (api_name, prompt)
                return (None, prompt)
        
        tasks = [process_prompt(p) for p in prompts]
        results = await asyncio.gather(*tasks)
        
        return results
    
    def get_optimization_report(self) -> Dict:
        """获取优化报告"""
        available = self.api_pool.get_available_apis()
        
        report = {
            "strategy": {
                "minimize_cost": self.strategy.minimize_cost,
                "maximize_speed": self.strategy.maximize_speed,
                "maximize_quality": self.strategy.maximize_quality,
                "balance": self.strategy.balance
            },
            "available_apis": len(available),
            "api_recommendations": {}
        }
        
        # 为不同场景推荐API
        test_prompt_length = 1000
        
        if available:
            report["api_recommendations"] = {
                "cost_optimized": self._select_by_cost(available, test_prompt_length),
                "speed_optimized": self._select_by_speed(available),
                "quality_optimized": self._select_by_quality(available),
                "balanced": self._select_balanced(available, test_prompt_length)
            }
        
        return report

