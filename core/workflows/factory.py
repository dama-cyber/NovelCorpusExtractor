"""
工作流工厂
用于创建和管理不同类型的工作流
"""

import logging
from typing import Dict, Type, List
from .base import WorkflowBase
from .seven_step_workflow import SevenStepWorkflow
from .integrated_workflow import IntegratedWorkflow

logger = logging.getLogger(__name__)


class WorkflowFactory:
    """工作流工厂"""
    
    WORKFLOW_REGISTRY: Dict[str, Type[WorkflowBase]] = {
        "seven_step": SevenStepWorkflow,
        "integrated": IntegratedWorkflow,  # 拆书+七步创作整合工作流
        # 可以添加更多工作流类型
        # "snowflake": SnowflakeWorkflow,
        # "hero_journey": HeroJourneyWorkflow,
    }
    
    @classmethod
    def create_workflow(
        cls,
        workflow_type: str,
        project_id: str,
        card_manager=None,
        project_manager=None,
        llm_client=None,
        context_injector=None,
        knowledge_graph=None,
        memory_manager=None,
        frankentexts_manager=None,
        agents=None
    ) -> WorkflowBase:
        """创建工作流实例"""
        workflow_class = cls.WORKFLOW_REGISTRY.get(workflow_type)
        if not workflow_class:
            raise ValueError(f"未知工作流类型: {workflow_type}")
        
        # 整合工作流需要额外的参数
        if workflow_type == "integrated":
            return workflow_class(
                project_id=project_id,
                card_manager=card_manager,
                project_manager=project_manager,
                llm_client=llm_client,
                memory_manager=memory_manager,
                frankentexts_manager=frankentexts_manager,
                agents=agents
            )
        
        # 其他工作流使用标准参数
        return workflow_class(
            project_id=project_id,
            card_manager=card_manager,
            project_manager=project_manager,
            llm_client=llm_client,
            context_injector=context_injector,
            knowledge_graph=knowledge_graph
        )
    
    @classmethod
    def list_workflows(cls) -> List[Dict[str, str]]:
        """列出所有可用的工作流"""
        return [
            {
                "type": workflow_type,
                "name": workflow_class.__name__,
                "description": getattr(workflow_class, "__doc__", "") or ""
            }
            for workflow_type, workflow_class in cls.WORKFLOW_REGISTRY.items()
        ]
    
    @classmethod
    def register_workflow(cls, workflow_type: str, workflow_class: Type[WorkflowBase]):
        """注册新的工作流类型"""
        cls.WORKFLOW_REGISTRY[workflow_type] = workflow_class
        logger.info(f"注册工作流类型: {workflow_type} -> {workflow_class.__name__}")

