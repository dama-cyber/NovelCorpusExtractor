"""
NovelCorpusExtractor API客户端
提供同步和异步客户端接口
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from io import BytesIO

import requests
import aiohttp

from .models import (
    Project, Card, Workflow, WorkflowProgress,
    ProcessResponse, HealthStatus, ConfigInfo
)
from core.exceptions import APIError, ValidationError

logger = logging.getLogger(__name__)


class NovelCorpusClient:
    """同步API客户端"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: int = 300,
        max_retries: int = 3
    ):
        """
        初始化客户端
        
        Args:
            base_url: API服务器地址
            api_key: API密钥（可选）
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法
            endpoint: API端点
            params: URL参数
            json_data: JSON数据
            files: 文件数据
            data: 表单数据
        
        Returns:
            Dict: 响应数据
        
        Raises:
            APIError: API调用失败
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    files=files,
                    data=data,
                    timeout=self.timeout
                )
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise APIError(f"API请求失败: {e}")
                logger.warning(f"请求失败，重试 {attempt + 1}/{self.max_retries}: {e}")
                time.sleep(2 ** attempt)  # 指数退避
    
    # 健康检查
    def health_check(self) -> HealthStatus:
        """检查API服务器健康状态"""
        data = self._request("GET", "/api/health")
        return HealthStatus.from_dict(data)
    
    def get_config(self) -> ConfigInfo:
        """获取配置信息"""
        data = self._request("GET", "/api/config")
        return ConfigInfo.from_dict(data)
    
    # 项目管理
    def list_projects(self) -> List[Project]:
        """列出所有项目"""
        data = self._request("GET", "/api/projects")
        return [Project.from_dict(item) for item in data]
    
    def get_project(self, project_id: str) -> Project:
        """获取项目详情"""
        data = self._request("GET", f"/api/projects/{project_id}")
        return Project.from_dict(data)
    
    def create_project(
        self,
        name: str,
        description: Optional[str] = None,
        template_id: Optional[str] = None
    ) -> Project:
        """创建项目"""
        json_data = {
            "name": name,
            "description": description,
            "template_id": template_id
        }
        data = self._request("POST", "/api/projects", json_data=json_data)
        return Project.from_dict(data)
    
    def update_project(
        self,
        project_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Project:
        """更新项目"""
        json_data = {}
        if name is not None:
            json_data["name"] = name
        if description is not None:
            json_data["description"] = description
        
        data = self._request("PUT", f"/api/projects/{project_id}", json_data=json_data)
        return Project.from_dict(data)
    
    def delete_project(self, project_id: str) -> bool:
        """删除项目"""
        self._request("DELETE", f"/api/projects/{project_id}")
        return True
    
    # 卡片管理
    def list_cards(self, project_id: Optional[str] = None) -> List[Card]:
        """列出卡片"""
        params = {}
        if project_id:
            params["project_id"] = project_id
        
        data = self._request("GET", "/api/cards", params=params)
        return [Card.from_dict(item) for item in data]
    
    def get_card(self, card_id: str) -> Card:
        """获取卡片详情"""
        data = self._request("GET", f"/api/cards/{card_id}")
        return Card.from_dict(data)
    
    def create_card(
        self,
        name: str,
        card_type: str,
        content: Dict[str, Any],
        project_id: Optional[str] = None
    ) -> Card:
        """创建卡片"""
        json_data = {
            "name": name,
            "card_type": card_type,
            "content": content,
            "project_id": project_id
        }
        data = self._request("POST", "/api/cards", json_data=json_data)
        return Card.from_dict(data)
    
    # 工作流管理
    def list_workflows(self) -> List[Workflow]:
        """列出可用工作流"""
        data = self._request("GET", "/api/workflows/list")
        return [Workflow.from_dict(item) for item in data]
    
    def start_workflow(
        self,
        workflow_name: str,
        project_id: Optional[str] = None,
        initial_data: Optional[Dict[str, Any]] = None
    ) -> Workflow:
        """启动工作流"""
        json_data = {
            "workflow_name": workflow_name,
            "project_id": project_id,
            "initial_data": initial_data or {}
        }
        data = self._request("POST", "/api/workflows/start", json_data=json_data)
        return Workflow.from_dict(data)
    
    def get_workflow_progress(self, workflow_id: str) -> WorkflowProgress:
        """获取工作流进度"""
        data = self._request("GET", f"/api/workflows/{workflow_id}/progress")
        return WorkflowProgress.from_dict(data)
    
    def next_workflow_stage(self, workflow_id: str) -> WorkflowProgress:
        """进入下一阶段"""
        data = self._request("POST", f"/api/workflows/{workflow_id}/next")
        return WorkflowProgress.from_dict(data)
    
    # 处理小说
    def process_novel(
        self,
        file_path: Optional[Union[str, Path]] = None,
        sample_text: Optional[str] = None,
        novel_type: str = "通用",
        topology_mode: str = "auto",
        api_pool_mode: str = "auto",
        workflow_targets: Optional[List[str]] = None,
        run_creative_flow: bool = False
    ) -> ProcessResponse:
        """
        处理小说文件或文本
        
        Args:
            file_path: 小说文件路径
            sample_text: 示例文本（当没有文件时使用）
            novel_type: 小说类型
            topology_mode: 拓扑模式
            api_pool_mode: API池模式
            workflow_targets: 工作流目标列表
            run_creative_flow: 是否运行创作流程
        
        Returns:
            ProcessResponse: 处理结果
        """
        if not file_path and not sample_text:
            raise ValidationError("必须提供 file_path 或 sample_text")
        
        data = {
            "novel_type": novel_type,
            "topology_mode": topology_mode,
            "api_pool_mode": api_pool_mode,
            "workflow_targets": json.dumps(workflow_targets or []),
            "run_creative_flow": str(run_creative_flow).lower()
        }
        
        files = None
        if file_path:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            with open(file_path, "rb") as f:
                files = {
                    "file": (file_path.name, f, "application/octet-stream")
                }
                response_data = self._request(
                    "POST",
                    "/api/process",
                    files=files,
                    data=data
                )
        else:
            data["sample_text"] = sample_text
            response_data = self._request(
                "POST",
                "/api/process",
                data=data
            )
        
        return ProcessResponse.from_dict(response_data)
    
    # 命令系统
    def list_commands(self) -> List[Dict[str, Any]]:
        """列出可用命令"""
        data = self._request("GET", "/api/commands/list")
        return data
    
    def execute_command(
        self,
        command: str,
        args: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """执行斜杠命令"""
        json_data = {
            "command": command,
            "args": args or {}
        }
        return self._request("POST", "/api/commands/execute", json_data=json_data)
    
    # 技能管理
    def list_skills(self) -> List[Dict[str, Any]]:
        """列出所有技能"""
        data = self._request("GET", "/api/skills")
        return data
    
    def close(self):
        """关闭客户端"""
        self.session.close()


class AsyncNovelCorpusClient:
    """异步API客户端"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: int = 300,
        max_retries: int = 3
    ):
        """
        初始化异步客户端
        
        Args:
            base_url: API服务器地址
            api_key: API密钥（可选）
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建会话"""
        if self.session is None or self.session.closed:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=self.timeout
            )
        return self.session
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """发送异步HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        session = await self._get_session()
        
        for attempt in range(self.max_retries):
            try:
                async with session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    data=data
                ) as response:
                    response.raise_for_status()
                    return await response.json()
                    
            except aiohttp.ClientError as e:
                if attempt == self.max_retries - 1:
                    raise APIError(f"API请求失败: {e}")
                logger.warning(f"请求失败，重试 {attempt + 1}/{self.max_retries}: {e}")
                await asyncio.sleep(2 ** attempt)
    
    # 健康检查
    async def health_check(self) -> HealthStatus:
        """检查API服务器健康状态"""
        data = await self._request("GET", "/api/health")
        return HealthStatus.from_dict(data)
    
    async def get_config(self) -> ConfigInfo:
        """获取配置信息"""
        data = await self._request("GET", "/api/config")
        return ConfigInfo.from_dict(data)
    
    # 项目管理（异步版本，方法类似同步版本）
    async def list_projects(self) -> List[Project]:
        """列出所有项目"""
        data = await self._request("GET", "/api/projects")
        return [Project.from_dict(item) for item in data]
    
    async def get_project(self, project_id: str) -> Project:
        """获取项目详情"""
        data = await self._request("GET", f"/api/projects/{project_id}")
        return Project.from_dict(data)
    
    async def create_project(
        self,
        name: str,
        description: Optional[str] = None,
        template_id: Optional[str] = None
    ) -> Project:
        """创建项目"""
        json_data = {
            "name": name,
            "description": description,
            "template_id": template_id
        }
        data = await self._request("POST", "/api/projects", json_data=json_data)
        return Project.from_dict(data)
    
    async def close(self):
        """关闭客户端"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()

