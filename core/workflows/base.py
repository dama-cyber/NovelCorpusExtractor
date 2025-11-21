"""
工作流基类
定义工作流系统的核心抽象和基础功能
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


class WorkflowStatus(str, Enum):
    """工作流状态"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStage:
    """工作流阶段"""
    name: str
    label: str
    order: int
    config: Dict[str, Any] = field(default_factory=dict)
    completed: bool = False
    card_id: Optional[str] = None
    output: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "label": self.label,
            "order": self.order,
            "config": self.config,
            "completed": self.completed,
            "card_id": self.card_id,
            "output": self.output
        }


class WorkflowBase(ABC):
    """工作流基类"""
    
    def __init__(
        self,
        project_id: str,
        card_manager=None,
        llm_client=None,
        context_injector=None,
        knowledge_graph=None
    ):
        self.project_id = project_id
        self.card_manager = card_manager
        self.llm_client = llm_client
        self.context_injector = context_injector
        self.knowledge_graph = knowledge_graph
        
        self.workflow_id = str(uuid.uuid4())
        self.stages: List[WorkflowStage] = []
        self.status = WorkflowStatus.NOT_STARTED
        self.current_stage_index = 0
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        
        # 初始化阶段列表
        self.stages = self.get_stages()
    
    @abstractmethod
    def get_stages(self) -> List[WorkflowStage]:
        """获取工作流阶段列表"""
        pass
    
    @abstractmethod
    async def expand_stage(self, stage: WorkflowStage, parent_card_id: Optional[str] = None) -> Dict[str, Any]:
        """扩展阶段"""
        pass
    
    async def start(self, initial_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """启动工作流"""
        if self.status != WorkflowStatus.NOT_STARTED:
            raise ValueError(f"工作流已启动，当前状态: {self.status}")
        
        self.status = WorkflowStatus.IN_PROGRESS
        self.current_stage_index = 0
        self.updated_at = datetime.now().isoformat()
        
        # 创建根卡片（如果需要）
        root_card_id = None
        if self.card_manager and initial_data:
            root_card = self.card_manager.create_card(
                self.project_id,
                "workflow_root",
                initial_data
            )
            root_card_id = root_card.get('id') if isinstance(root_card, dict) else root_card.id
        
        return {
            "workflow_id": self.workflow_id,
            "project_id": self.project_id,
            "status": self.status.value,
            "current_stage": self.stages[0].name if self.stages else None,
            "stages": [s.to_dict() for s in self.stages],
            "root_card_id": root_card_id
        }
    
    async def next_stage(self) -> Dict[str, Any]:
        """进入下一阶段"""
        if self.status != WorkflowStatus.IN_PROGRESS:
            raise ValueError(f"工作流未在进行中，当前状态: {self.status}")
        
        if self.current_stage_index >= len(self.stages):
            self.status = WorkflowStatus.COMPLETED
            return {
                "workflow_id": self.workflow_id,
                "status": self.status.value,
                "message": "所有阶段已完成"
            }
        
        current_stage = self.stages[self.current_stage_index]
        
        # 获取父卡片ID（前一个阶段的卡片）
        parent_card_id = None
        if self.current_stage_index > 0:
            prev_stage = self.stages[self.current_stage_index - 1]
            parent_card_id = prev_stage.card_id
        
        try:
            # 扩展当前阶段
            result = await self.expand_stage(current_stage, parent_card_id)
            
            # 更新阶段状态
            current_stage.completed = True
            current_stage.card_id = result.get("card_id")
            current_stage.output = result
            self.current_stage_index += 1
            self.updated_at = datetime.now().isoformat()
            
            # 检查是否完成所有阶段
            if self.current_stage_index >= len(self.stages):
                self.status = WorkflowStatus.COMPLETED
            
            return {
                "workflow_id": self.workflow_id,
                "status": self.status.value,
                "current_stage": current_stage.name,
                "stage_completed": True,
                "result": result,
                "next_stage": self.stages[self.current_stage_index].name if self.current_stage_index < len(self.stages) else None
            }
        except Exception as e:
            logger.error(f"扩展阶段失败: {e}", exc_info=True)
            raise
    
    async def jump_to_stage(self, stage_name: str) -> Dict[str, Any]:
        """跳转到指定阶段"""
        stage_index = next((i for i, s in enumerate(self.stages) if s.name == stage_name), None)
        if stage_index is None:
            raise ValueError(f"未知阶段: {stage_name}")
        
        self.current_stage_index = stage_index
        self.updated_at = datetime.now().isoformat()
        
        return await self.next_stage()
    
    def get_progress(self) -> Dict[str, Any]:
        """获取工作流进度"""
        completed_count = sum(1 for s in self.stages if s.completed)
        total_count = len(self.stages)
        
        return {
            "workflow_id": self.workflow_id,
            "project_id": self.project_id,
            "status": self.status.value,
            "current_stage_index": self.current_stage_index,
            "current_stage": self.stages[self.current_stage_index].name if self.current_stage_index < len(self.stages) else None,
            "progress": {
                "completed": completed_count,
                "total": total_count,
                "percentage": (completed_count / total_count * 100) if total_count > 0 else 0
            },
            "stages": [s.to_dict() for s in self.stages],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def pause(self):
        """暂停工作流"""
        if self.status == WorkflowStatus.IN_PROGRESS:
            self.status = WorkflowStatus.PAUSED
            self.updated_at = datetime.now().isoformat()
    
    def resume(self):
        """恢复工作流"""
        if self.status == WorkflowStatus.PAUSED:
            self.status = WorkflowStatus.IN_PROGRESS
            self.updated_at = datetime.now().isoformat()
    
    def cancel(self):
        """取消工作流"""
        self.status = WorkflowStatus.CANCELLED
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "workflow_id": self.workflow_id,
            "project_id": self.project_id,
            "status": self.status.value,
            "current_stage_index": self.current_stage_index,
            "stages": [s.to_dict() for s in self.stages],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


