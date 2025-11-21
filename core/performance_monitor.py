"""
性能监控模块
收集和报告系统性能指标
"""

import time
import logging
from typing import Dict, List, Optional, Callable
from collections import defaultdict
from threading import Lock
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """性能指标"""
    name: str
    value: float
    unit: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.counters: Dict[str, int] = defaultdict(int)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self.lock = Lock()
        self.max_metrics = 1000  # 最大保留指标数
    
    def record_metric(self, name: str, value: float, unit: str = "", metadata: Dict = None):
        """
        记录性能指标
        
        Args:
            name: 指标名称
            value: 指标值
            unit: 单位
            metadata: 元数据
        """
        with self.lock:
            metric = PerformanceMetric(
                name=name,
                value=value,
                unit=unit,
                metadata=metadata or {}
            )
            self.metrics.append(metric)
            
            # 限制指标数量
            if len(self.metrics) > self.max_metrics:
                self.metrics = self.metrics[-self.max_metrics:]
    
    def increment_counter(self, name: str, value: int = 1):
        """
        增加计数器
        
        Args:
            name: 计数器名称
            value: 增加值
        """
        with self.lock:
            self.counters[name] += value
    
    def start_timer(self, name: str) -> float:
        """
        开始计时
        
        Args:
            name: 计时器名称
        
        Returns:
            开始时间戳
        """
        return time.time()
    
    def end_timer(self, name: str, start_time: float):
        """
        结束计时并记录
        
        Args:
            name: 计时器名称
            start_time: 开始时间戳
        """
        duration = time.time() - start_time
        with self.lock:
            self.timers[name].append(duration)
            # 限制每个计时器的记录数
            if len(self.timers[name]) > 100:
                self.timers[name] = self.timers[name][-100:]
    
    def timer(self, name: str):
        """计时器上下文管理器"""
        return TimerContext(self, name)
    
    def get_metrics(self, name: Optional[str] = None, limit: int = 100) -> List[PerformanceMetric]:
        """
        获取性能指标
        
        Args:
            name: 指标名称（可选，用于过滤）
            limit: 返回数量限制
        
        Returns:
            性能指标列表
        """
        with self.lock:
            metrics = self.metrics
            if name:
                metrics = [m for m in metrics if m.name == name]
            return metrics[-limit:]
    
    def get_counters(self) -> Dict[str, int]:
        """获取所有计数器值"""
        with self.lock:
            return dict(self.counters)
    
    def get_timer_stats(self, name: str) -> Dict[str, float]:
        """
        获取计时器统计信息
        
        Args:
            name: 计时器名称
        
        Returns:
            统计信息（平均值、最大值、最小值、总数）
        """
        with self.lock:
            times = self.timers.get(name, [])
            if not times:
                return {}
            
            return {
                "count": len(times),
                "avg": sum(times) / len(times),
                "min": min(times),
                "max": max(times),
                "total": sum(times)
            }
    
    def get_summary(self) -> Dict:
        """获取性能摘要"""
        with self.lock:
            return {
                "metrics_count": len(self.metrics),
                "counters": dict(self.counters),
                "timers": {
                    name: self.get_timer_stats(name)
                    for name in self.timers.keys()
                }
            }
    
    def reset(self):
        """重置所有指标"""
        with self.lock:
            self.metrics.clear()
            self.counters.clear()
            self.timers.clear()


class TimerContext:
    """计时器上下文管理器"""
    
    def __init__(self, monitor: PerformanceMonitor, name: str):
        self.monitor = monitor
        self.name = name
        self.start_time: Optional[float] = None
    
    def __enter__(self):
        self.start_time = self.monitor.start_timer(self.name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            self.monitor.end_timer(self.name, self.start_time)


# 全局性能监控器实例
_global_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """获取性能监控器实例（单例模式）"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor


