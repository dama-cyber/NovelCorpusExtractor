"""
拓扑管理器
支持线性串行、三角协同、专家蜂群三种处理模式
"""

from typing import Dict, List, Optional, Callable
import logging
import asyncio
from enum import Enum

logger = logging.getLogger(__name__)


class TopologyMode(Enum):
    """拓扑模式枚举"""
    LINEAR = "linear"  # 线性串行
    TRIANGULAR = "triangular"  # 三角协同
    SWARM = "swarm"  # 专家蜂群
    AUTO = "auto"  # 自动检测


class TopologyManager:
    """拓扑管理器"""
    
    def __init__(self, mode: TopologyMode, available_apis: int = 1):
        """
        初始化拓扑管理器
        Args:
            mode: 拓扑模式
            available_apis: 可用API数量
        """
        self.mode = mode
        self.available_apis = available_apis
        
        # 如果模式是AUTO，自动检测
        if mode == TopologyMode.AUTO:
            self.mode = self._auto_detect_mode(available_apis)
        
        logger.info(f"拓扑模式: {self.mode.value}, 可用API: {available_apis}")
    
    def _auto_detect_mode(self, available_apis: int) -> TopologyMode:
        """自动检测合适的拓扑模式"""
        if available_apis >= 5:
            return TopologyMode.SWARM
        elif available_apis >= 3:
            return TopologyMode.TRIANGULAR
        else:
            return TopologyMode.LINEAR
    
    async def execute_linear(self, pipeline: Callable, chunks: List[Dict]) -> List[Dict]:
        """线性串行模式执行"""
        results = []
        for chunk in chunks:
            result = await pipeline(chunk)
            results.append(result)
        return results
    
    async def execute_triangular(self, scanner: Callable, extractor: Callable, 
                                 memory_keeper: Callable, chunks: List[Dict]) -> List[Dict]:
        """三角协同模式执行"""
        # Scanner扫描 -> Extractor提取 -> Memory Keeper校验
        results = []
        
        # 创建任务队列
        scan_queue = asyncio.Queue()
        extract_queue = asyncio.Queue()
        
        # Scanner任务
        async def scanner_task():
            for chunk in chunks:
                scanned = await scanner(chunk)
                await scan_queue.put(scanned)
            await scan_queue.put(None)  # 结束标记
        
        # Extractor任务
        async def extractor_task():
            while True:
                scanned_chunk = await scan_queue.get()
                if scanned_chunk is None:
                    await extract_queue.put(None)
                    break
                extracted = await extractor(scanned_chunk)
                await extract_queue.put(extracted)
        
        # Memory Keeper任务
        async def memory_keeper_task():
            while True:
                extracted = await extract_queue.get()
                if extracted is None:
                    break
                validated = await memory_keeper(extracted)
                results.append(validated)
        
        # 并行执行
        await asyncio.gather(
            scanner_task(),
            extractor_task(),
            memory_keeper_task()
        )
        
        return results
    
    async def execute_swarm(self, agents: Dict[str, Callable], chunks: List[Dict]) -> List[Dict]:
        """专家蜂群模式执行"""
        # 所有Agent并行工作
        tasks = []
        
        for chunk in chunks:
            # 为每个块创建并行任务
            chunk_tasks = []
            for agent_name, agent_func in agents.items():
                task = agent_func(chunk)
                chunk_tasks.append(task)
            
            # 等待所有Agent完成
            chunk_results = await asyncio.gather(*chunk_tasks)
            tasks.append(chunk_results)
        
        # 汇总结果
        results = []
        for chunk_results in tasks:
            # 合并各Agent的结果
            merged_result = {}
            for result in chunk_results:
                merged_result.update(result)
            results.append(merged_result)
        
        return results
    
    async def execute(self, **kwargs) -> List[Dict]:
        """执行处理流程"""
        if self.mode == TopologyMode.LINEAR:
            return await self.execute_linear(
                kwargs.get("pipeline"),
                kwargs.get("chunks", [])
            )
        elif self.mode == TopologyMode.TRIANGULAR:
            return await self.execute_triangular(
                kwargs.get("scanner"),
                kwargs.get("extractor"),
                kwargs.get("memory_keeper"),
                kwargs.get("chunks", [])
            )
        elif self.mode == TopologyMode.SWARM:
            return await self.execute_swarm(
                kwargs.get("agents", {}),
                kwargs.get("chunks", [])
            )
        else:
            raise ValueError(f"不支持的拓扑模式: {self.mode}")


class DynamicTopologyResolver:
    """动态拓扑解析器"""
    
    @staticmethod
    def detect_available_apis(configs: List[Dict]) -> int:
        """检测可用API数量"""
        import os
        available = 0
        for config in configs:
            # 检查配置中的api_key或环境变量
            api_key = config.get("api_key")
            if not api_key:
                # 根据模型类型检查对应的环境变量
                model_type = config.get("model", "openai").lower()
                if model_type == "openai" or model_type.startswith("gpt"):
                    api_key = os.getenv("OPENAI_API_KEY")
                elif model_type == "gemini":
                    api_key = os.getenv("GEMINI_API_KEY")
                elif model_type == "deepseek":
                    api_key = os.getenv("DEEPSEEK_API_KEY")
            
            if api_key:
                available += 1
        return available
    
    @staticmethod
    def build_execution_flow(mode: TopologyMode, available_apis: int) -> Dict:
        """构建执行流程图"""
        flow = {
            "mode": mode.value,
            "available_apis": available_apis,
            "agents": [],
            "parallelism": 1
        }
        
        if mode == TopologyMode.LINEAR:
            flow["agents"] = ["Reader", "Analyst", "Archivist"]
            flow["parallelism"] = 1
        elif mode == TopologyMode.TRIANGULAR:
            flow["agents"] = ["Scanner", "Extractor", "MemoryKeeper"]
            flow["parallelism"] = 3
        elif mode == TopologyMode.SWARM:
            flow["agents"] = ["Reader", "Scanner", "Analyst", "Extractor", 
                            "Planner", "Stylist", "Archivist"]
            flow["parallelism"] = available_apis
        
        return flow

