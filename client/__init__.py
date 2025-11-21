"""
NovelCorpusExtractor API客户端库
提供便捷的Python客户端接口
"""

from .api_client import NovelCorpusClient, AsyncNovelCorpusClient
from .models import (
    Project, Card, Workflow, WorkflowProgress,
    ProcessResponse, HealthStatus, ConfigInfo
)

__all__ = [
    "NovelCorpusClient",
    "AsyncNovelCorpusClient",
    "Project",
    "Card",
    "Workflow",
    "WorkflowProgress",
    "ProcessResponse",
    "HealthStatus",
    "ConfigInfo"
]

__version__ = "1.0.0"


