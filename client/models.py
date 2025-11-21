"""
API客户端数据模型
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class Project:
    """项目模型"""
    id: str
    name: str
    description: Optional[str] = None
    template_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        """从字典创建项目"""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description"),
            template_id=data.get("template_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            metadata=data.get("metadata", {})
        )


@dataclass
class Card:
    """卡片模型"""
    id: str
    name: str
    card_type: str
    content: Dict[str, Any]
    project_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Card":
        """从字典创建卡片"""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            card_type=data.get("card_type", ""),
            content=data.get("content", {}),
            project_id=data.get("project_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            metadata=data.get("metadata", {})
        )


@dataclass
class Workflow:
    """工作流模型"""
    id: str
    name: str
    description: Optional[str] = None
    stages: List[Dict[str, Any]] = field(default_factory=list)
    current_stage: Optional[str] = None
    status: str = "pending"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Workflow":
        """从字典创建工作流"""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description"),
            stages=data.get("stages", []),
            current_stage=data.get("current_stage"),
            status=data.get("status", "pending"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )


@dataclass
class WorkflowProgress:
    """工作流进度模型"""
    workflow_id: str
    current_stage: str
    completed_stages: List[str] = field(default_factory=list)
    total_stages: int = 0
    progress_percentage: float = 0.0
    status: str = "running"
    stage_results: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowProgress":
        """从字典创建工作流进度"""
        return cls(
            workflow_id=data.get("workflow_id", ""),
            current_stage=data.get("current_stage", ""),
            completed_stages=data.get("completed_stages", []),
            total_stages=data.get("total_stages", 0),
            progress_percentage=data.get("progress_percentage", 0.0),
            status=data.get("status", "running"),
            stage_results=data.get("stage_results", {})
        )


@dataclass
class ProcessResponse:
    """处理响应模型"""
    workflow_id: Optional[str] = None  # 工作流ID，用于查询进度
    chunk_results: List[Dict[str, Any]] = field(default_factory=list)
    workflow_stages: Optional[Dict[str, Dict]] = None
    workflow: Optional[Dict] = None
    outline: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProcessResponse":
        """从字典创建处理响应"""
        return cls(
            workflow_id=data.get("workflowId", data.get("workflow_id")),
            chunk_results=data.get("chunkResults", data.get("chunk_results", [])),
            workflow_stages=data.get("workflowStages", data.get("workflow_stages")),
            workflow=data.get("workflow"),
            outline=data.get("outline"),
            metadata=data.get("metadata", {})
        )


@dataclass
class HealthStatus:
    """健康状态模型"""
    status: str
    timestamp: Optional[str] = None
    components: Dict[str, Any] = field(default_factory=dict)
    performance: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HealthStatus":
        """从字典创建健康状态"""
        return cls(
            status=data.get("status", "unknown"),
            timestamp=data.get("timestamp"),
            components=data.get("components", {}),
            performance=data.get("performance"),
            error=data.get("error")
        )


@dataclass
class ConfigInfo:
    """配置信息模型"""
    api_mode: str
    api_providers: List[str] = field(default_factory=list)
    storage_path: Optional[str] = None
    features: Dict[str, bool] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConfigInfo":
        """从字典创建配置信息"""
        return cls(
            api_mode=data.get("api_mode", "single"),
            api_providers=data.get("api_providers", []),
            storage_path=data.get("storage_path"),
            features=data.get("features", {})
        )


