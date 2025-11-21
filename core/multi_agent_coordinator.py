"""
多Agent协同管理器
根据可用API数量（1-5）智能分配Agent角色和协同策略
"""

from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import logging
import asyncio
from dataclasses import dataclass

from .model_interface import LLMClient
from .enhanced_model_interface import EnhancedLLMClient
from .api_manager import APIPool, APIProvider

logger = logging.getLogger(__name__)


class AgentRole(str, Enum):
    """Agent角色枚举"""
    READER = "reader"           # 阅读者：分析上下文
    ANALYST = "analyst"         # 分析者：深度分析
    PLANNER = "planner"         # 规划者：制定计划
    WRITER = "writer"           # 写作者：执行写作
    CRITIC = "critic"           # 评论者：质量审查
    EXTRACTOR = "extractor"     # 提取者：语料库检索
    STYLIST = "stylist"         # 风格师：优化风格
    ARCHIVIST = "archivist"     # 档案员：保存记录


@dataclass
class AgentAssignment:
    """Agent分配信息"""
    role: AgentRole
    api_index: int  # 使用的API索引
    priority: int   # 优先级（1-5，1最高）
    can_parallel: bool  # 是否可以并行执行


class MultiAgentCoordinator:
    """多Agent协同管理器"""
    
    def __init__(self, llm_client: LLMClient, available_apis: int):
        """
        初始化协同管理器
        Args:
            llm_client: LLM客户端（可能是EnhancedLLMClient）
            available_apis: 可用API数量（1-5）
        """
        self.llm_client = llm_client
        self.available_apis = min(max(available_apis, 1), 5)  # 限制在1-5之间
        
        # 检测是否为EnhancedLLMClient
        self.has_api_pool = hasattr(llm_client, 'api_pool') and llm_client.api_pool
        if self.has_api_pool:
            self.api_pool = llm_client.api_pool
            # 获取实际可用的API列表
            self.api_names = list(self.api_pool.apis.keys())[:self.available_apis]
        else:
            self.api_pool = None
            self.api_names = [f"api_{i}" for i in range(self.available_apis)]
        
        # 根据API数量选择协同策略
        self.strategy = self._select_strategy()
        logger.info(f"多Agent协同管理器初始化: {self.available_apis}个API, 策略={self.strategy['name']}")
    
    def _select_strategy(self) -> Dict[str, Any]:
        """根据API数量选择协同策略"""
        strategies = {
            1: {
                "name": "单API串行模式",
                "description": "所有Agent串行执行，共享单个API",
                "assignments": [
                    AgentAssignment(AgentRole.READER, 0, 1, False),
                    AgentAssignment(AgentRole.ANALYST, 0, 2, False),
                    AgentAssignment(AgentRole.PLANNER, 0, 3, False),
                    AgentAssignment(AgentRole.WRITER, 0, 4, False),
                    AgentAssignment(AgentRole.CRITIC, 0, 5, False),
                ]
            },
            2: {
                "name": "双API并行模式",
                "description": "核心Agent并行，辅助Agent串行",
                "assignments": [
                    AgentAssignment(AgentRole.READER, 0, 1, True),
                    AgentAssignment(AgentRole.ANALYST, 1, 1, True),
                    AgentAssignment(AgentRole.PLANNER, 0, 2, False),
                    AgentAssignment(AgentRole.WRITER, 1, 3, False),
                    AgentAssignment(AgentRole.CRITIC, 0, 4, False),
                ]
            },
            3: {
                "name": "三API三角模式",
                "description": "分析-规划-写作三角协同，评论串行",
                "assignments": [
                    AgentAssignment(AgentRole.READER, 0, 1, True),
                    AgentAssignment(AgentRole.ANALYST, 1, 1, True),
                    AgentAssignment(AgentRole.EXTRACTOR, 2, 1, True),
                    AgentAssignment(AgentRole.PLANNER, 0, 2, False),
                    AgentAssignment(AgentRole.WRITER, 1, 3, False),
                    AgentAssignment(AgentRole.STYLIST, 2, 3, True),
                    AgentAssignment(AgentRole.CRITIC, 0, 4, False),
                ]
            },
            4: {
                "name": "四API协同模式",
                "description": "多阶段并行，质量审查独立",
                "assignments": [
                    AgentAssignment(AgentRole.READER, 0, 1, True),
                    AgentAssignment(AgentRole.ANALYST, 1, 1, True),
                    AgentAssignment(AgentRole.EXTRACTOR, 2, 1, True),
                    AgentAssignment(AgentRole.PLANNER, 3, 1, True),
                    AgentAssignment(AgentRole.WRITER, 0, 2, False),
                    AgentAssignment(AgentRole.STYLIST, 1, 2, True),
                    AgentAssignment(AgentRole.CRITIC, 2, 3, False),
                    AgentAssignment(AgentRole.ARCHIVIST, 3, 4, False),
                ]
            },
            5: {
                "name": "五API蜂群模式",
                "description": "全功能并行，最大化效率",
                "assignments": [
                    AgentAssignment(AgentRole.READER, 0, 1, True),
                    AgentAssignment(AgentRole.ANALYST, 1, 1, True),
                    AgentAssignment(AgentRole.EXTRACTOR, 2, 1, True),
                    AgentAssignment(AgentRole.PLANNER, 3, 1, True),
                    AgentAssignment(AgentRole.WRITER, 4, 2, False),
                    AgentAssignment(AgentRole.STYLIST, 0, 2, True),
                    AgentAssignment(AgentRole.CRITIC, 1, 3, True),
                    AgentAssignment(AgentRole.ARCHIVIST, 2, 4, False),
                ]
            }
        }
        
        return strategies.get(self.available_apis, strategies[1])
    
    def get_agent_assignments(self) -> List[AgentAssignment]:
        """获取Agent分配列表"""
        return self.strategy["assignments"]
    
    def get_api_for_agent(self, role: AgentRole) -> Optional[str]:
        """为指定Agent获取分配的API"""
        for assignment in self.strategy["assignments"]:
            if assignment.role == role:
                api_index = assignment.api_index
                if api_index < len(self.api_names):
                    return self.api_names[api_index]
        return None
    
    def get_parallel_agents(self, priority: int) -> List[AgentRole]:
        """获取指定优先级可以并行执行的Agent列表"""
        parallel_agents = []
        for assignment in self.strategy["assignments"]:
            if assignment.priority == priority and assignment.can_parallel:
                parallel_agents.append(assignment.role)
        return parallel_agents
    
    async def execute_agents_parallel(
        self, 
        agent_functions: Dict[AgentRole, Callable],
        context: Dict[str, Any]
    ) -> Dict[AgentRole, Any]:
        """
        并行执行多个Agent
        Args:
            agent_functions: Agent角色到执行函数的映射
            context: 共享上下文
        Returns:
            Agent角色到结果的映射
        """
        # 按优先级分组
        priority_groups: Dict[int, List[AgentRole]] = {}
        for assignment in self.strategy["assignments"]:
            if assignment.role in agent_functions:
                if assignment.priority not in priority_groups:
                    priority_groups[assignment.priority] = []
                priority_groups[assignment.priority].append(assignment.role)
        
        # 按优先级顺序执行
        results: Dict[AgentRole, Any] = {}
        for priority in sorted(priority_groups.keys()):
            agents_in_priority = priority_groups[priority]
            
            # 检查是否可以并行
            can_parallel = all(
                any(a.role == agent and a.can_parallel 
                    for a in self.strategy["assignments"])
                for agent in agents_in_priority
            )
            
            if can_parallel and len(agents_in_priority) > 1:
                # 并行执行
                tasks = []
                for agent_role in agents_in_priority:
                    func = agent_functions[agent_role]
                    # 为每个Agent创建独立的上下文副本
                    agent_context = context.copy()
                    agent_context['api_name'] = self.get_api_for_agent(agent_role)
                    tasks.append(func(agent_context))
                
                agent_results = await asyncio.gather(*tasks, return_exceptions=True)
                for agent_role, result in zip(agents_in_priority, agent_results):
                    if isinstance(result, Exception):
                        logger.error(f"Agent {agent_role.value} 执行失败: {result}")
                        results[agent_role] = {"error": str(result)}
                    else:
                        results[agent_role] = result
            else:
                # 串行执行
                for agent_role in agents_in_priority:
                    func = agent_functions[agent_role]
                    agent_context = context.copy()
                    agent_context['api_name'] = self.get_api_for_agent(agent_role)
                    try:
                        result = await func(agent_context)
                        results[agent_role] = result
                    except Exception as e:
                        logger.error(f"Agent {agent_role.value} 执行失败: {e}")
                        results[agent_role] = {"error": str(e)}
        
        return results
    
    def create_agent_llm_client(self, role: AgentRole) -> LLMClient:
        """
        为指定Agent创建专用的LLM客户端
        如果使用API池，返回指定API的客户端；否则返回共享客户端
        """
        if not self.has_api_pool:
            return self.llm_client
        
        # 获取分配给该Agent的API
        api_name = self.get_api_for_agent(role)
        if not api_name or api_name not in self.api_pool.apis:
            return self.llm_client
        
        # 创建使用指定API的客户端包装器
        from .enhanced_model_interface import EnhancedLLMClient
        api_config = self.api_pool.apis[api_name]
        provider = api_config.provider
        
        # 返回一个包装器，强制使用指定的API
        class AgentLLMClientWrapper(LLMClient):
            def __init__(self, base_client: EnhancedLLMClient, api_name: str, provider: APIProvider):
                self.base_client = base_client
                self.api_name = api_name
                self.provider = provider
            
            def send_prompt(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
                kwargs['provider'] = self.provider
                return self.base_client.send_prompt(prompt, system_prompt, **kwargs)
            
            async def send_prompt_async(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
                kwargs['provider'] = self.provider
                return await self.base_client.send_prompt_async(prompt, system_prompt, **kwargs)
            
            async def stream_prompt(self, prompt: str, system_prompt: Optional[str] = None, **kwargs):
                kwargs['provider'] = self.provider
                async for chunk in self.base_client.stream_prompt(prompt, system_prompt, **kwargs):
                    yield chunk
        
        return AgentLLMClientWrapper(self.llm_client, api_name, provider)
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """获取策略信息"""
        return {
            "strategy_name": self.strategy["name"],
            "description": self.strategy["description"],
            "available_apis": self.available_apis,
            "api_names": self.api_names,
            "assignments": [
                {
                    "role": a.role.value,
                    "api_index": a.api_index,
                    "api_name": self.api_names[a.api_index] if a.api_index < len(self.api_names) else None,
                    "priority": a.priority,
                    "can_parallel": a.can_parallel
                }
                for a in self.strategy["assignments"]
            ]
        }


