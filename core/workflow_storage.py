"""
工作流存储和检索模块
实现工作流状态的持久化
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class WorkflowStorage:
    """工作流存储管理器"""
    
    def __init__(self, storage_dir: str = "workflows"):
        """
        初始化工作流存储
        
        Args:
            storage_dir: 存储目录路径
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._workflows: Dict[str, Dict[str, Any]] = {}
        self._load_all()
    
    def _load_all(self):
        """加载所有已保存的工作流"""
        try:
            for workflow_file in self.storage_dir.glob("*.json"):
                try:
                    with open(workflow_file, 'r', encoding='utf-8') as f:
                        workflow_data = json.load(f)
                        workflow_id = workflow_data.get("id")
                        if workflow_id:
                            self._workflows[workflow_id] = workflow_data
                except Exception as e:
                    logger.warning(f"加载工作流文件失败 {workflow_file}: {e}")
        except Exception as e:
            logger.error(f"加载工作流失败: {e}")
    
    def save_workflow(self, workflow_id: str, workflow_data: Dict[str, Any]) -> bool:
        """
        保存工作流状态
        
        Args:
            workflow_id: 工作流ID
            workflow_data: 工作流数据
        
        Returns:
            是否保存成功
        """
        try:
            workflow_data["id"] = workflow_id
            workflow_data["updated_at"] = datetime.now().isoformat()
            
            # 保存到内存
            self._workflows[workflow_id] = workflow_data
            
            # 保存到文件
            workflow_file = self.storage_dir / f"{workflow_id}.json"
            with open(workflow_file, 'w', encoding='utf-8') as f:
                json.dump(workflow_data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"工作流已保存: {workflow_id}")
            return True
        except Exception as e:
            logger.error(f"保存工作流失败 {workflow_id}: {e}")
            return False
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        获取工作流状态
        
        Args:
            workflow_id: 工作流ID
        
        Returns:
            工作流数据，如果不存在则返回None
        """
        return self._workflows.get(workflow_id)
    
    def list_workflows(self, project_id: Optional[str] = None) -> list[Dict[str, Any]]:
        """
        列出所有工作流
        
        Args:
            project_id: 可选的项目ID过滤
        
        Returns:
            工作流列表
        """
        workflows = list(self._workflows.values())
        if project_id:
            workflows = [w for w in workflows if w.get("project_id") == project_id]
        return workflows
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """
        删除工作流
        
        Args:
            workflow_id: 工作流ID
        
        Returns:
            是否删除成功
        """
        try:
            # 从内存中删除
            if workflow_id in self._workflows:
                del self._workflows[workflow_id]
            
            # 删除文件
            workflow_file = self.storage_dir / f"{workflow_id}.json"
            if workflow_file.exists():
                workflow_file.unlink()
            
            logger.debug(f"工作流已删除: {workflow_id}")
            return True
        except Exception as e:
            logger.error(f"删除工作流失败 {workflow_id}: {e}")
            return False
    
    def update_workflow_progress(self, workflow_id: str, progress: Dict[str, Any]) -> bool:
        """
        更新工作流进度
        
        Args:
            workflow_id: 工作流ID
            progress: 进度数据
        
        Returns:
            是否更新成功
        """
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return False
        
        workflow["progress"] = progress
        workflow["updated_at"] = datetime.now().isoformat()
        return self.save_workflow(workflow_id, workflow)


# 全局工作流存储实例
_workflow_storage: Optional[WorkflowStorage] = None


def get_workflow_storage() -> WorkflowStorage:
    """获取工作流存储实例（单例模式）"""
    global _workflow_storage
    if _workflow_storage is None:
        storage_dir = Path("workflows")
        _workflow_storage = WorkflowStorage(str(storage_dir))
    return _workflow_storage


