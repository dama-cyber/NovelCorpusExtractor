"""
项目管理系统
管理创作项目，包括项目创建、配置管理等
"""

import json
import uuid
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Project:
    """项目数据类"""
    id: str
    name: str
    description: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    def update(self, updates: Dict[str, Any]):
        """更新项目"""
        if 'name' in updates:
            self.name = updates['name']
        if 'description' in updates:
            self.description = updates['description']
        if 'config' in updates:
            self.config.update(updates['config'])
        if 'metadata' in updates:
            self.metadata.update(updates['metadata'])
        self.updated_at = datetime.now().isoformat()


class ProjectManager:
    """项目管理器"""
    
    def __init__(self, projects_dir: str = "projects"):
        self.projects_dir = Path(projects_dir)
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.projects: Dict[str, Project] = {}
        self._load_all_projects()
    
    def _get_project_dir(self, project_id: str) -> Path:
        """获取项目目录"""
        return self.projects_dir / project_id
    
    def _get_project_config_path(self, project_id: str) -> Path:
        """获取项目配置文件路径"""
        return self._get_project_dir(project_id) / "config.yaml"
    
    def _load_all_projects(self):
        """加载所有项目"""
        if not self.projects_dir.exists():
            return
        
        for project_dir in self.projects_dir.iterdir():
            if not project_dir.is_dir():
                continue
            
            project_id = project_dir.name
            config_path = project_dir / "config.yaml"
            
            if not config_path.exists():
                continue
            
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                
                project = Project(
                    id=project_id,
                    name=config.get('name', project_id),
                    description=config.get('description', ''),
                    config=config.get('config', {}),
                    metadata=config.get('metadata', {}),
                    created_at=config.get('created_at', datetime.now().isoformat()),
                    updated_at=config.get('updated_at', datetime.now().isoformat())
                )
                self.projects[project_id] = project
            except Exception as e:
                logger.error(f"加载项目失败 {project_dir}: {e}")
    
    def _save_project(self, project: Project):
        """保存项目配置"""
        project_dir = self._get_project_dir(project.id)
        project_dir.mkdir(parents=True, exist_ok=True)
        
        config_path = self._get_project_config_path(project.id)
        config = {
            'name': project.name,
            'description': project.description,
            'config': project.config,
            'metadata': project.metadata,
            'created_at': project.created_at,
            'updated_at': project.updated_at
        }
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        except Exception as e:
            logger.error(f"保存项目配置失败 {config_path}: {e}")
            raise
    
    def create_project(
        self,
        name: str,
        description: str = "",
        template_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """创建新项目"""
        project_id = str(uuid.uuid4())
        
        # 如果指定了模板，加载模板配置
        project_config = config or {}
        if template_id:
            template_config = self._load_template(template_id)
            project_config.update(template_config)
        
        project = Project(
            id=project_id,
            name=name,
            description=description,
            config=project_config
        )
        
        self.projects[project_id] = project
        self._save_project(project)
        
        # 创建项目目录结构
        project_dir = self._get_project_dir(project_id)
        (project_dir / "cards").mkdir(exist_ok=True)
        
        logger.info(f"创建项目: {project_id} ({name})")
        return project.to_dict()
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """获取项目"""
        project = self.projects.get(project_id)
        return project.to_dict() if project else None
    
    def update_project(self, project_id: str, updates: Dict[str, Any]):
        """更新项目"""
        project = self.projects.get(project_id)
        if not project:
            raise ValueError(f"项目不存在: {project_id}")
        
        project.update(updates)
        self._save_project(project)
        logger.info(f"更新项目: {project_id}")
    
    def delete_project(self, project_id: str):
        """删除项目"""
        project = self.projects.get(project_id)
        if not project:
            raise ValueError(f"项目不存在: {project_id}")
        
        # 删除项目目录
        project_dir = self._get_project_dir(project_id)
        if project_dir.exists():
            import shutil
            shutil.rmtree(project_dir)
        
        # 从内存中移除
        del self.projects[project_id]
        logger.info(f"删除项目: {project_id}")
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """列出所有项目"""
        return [p.to_dict() for p in self.projects.values()]
    
    def _load_template(self, template_id: str) -> Dict[str, Any]:
        """
        加载项目模板
        
        Args:
            template_id: 模板ID（文件名，不含扩展名）
        
        Returns:
            模板配置字典
        """
        # 查找模板文件（支持多个位置）
        template_paths = [
            Path("project_templates") / f"{template_id}.yaml",
            Path("project_templates") / f"{template_id}.json",
            self.projects_dir.parent / "project_templates" / f"{template_id}.yaml",
            self.projects_dir.parent / "project_templates" / f"{template_id}.json",
        ]
        
        for template_path in template_paths:
            if template_path.exists():
                try:
                    if template_path.suffix == ".yaml":
                        with open(template_path, 'r', encoding='utf-8') as f:
                            template_data = yaml.safe_load(f) or {}
                            logger.info(f"加载模板: {template_id} from {template_path}")
                            return template_data.get("config", {})
                    elif template_path.suffix == ".json":
                        with open(template_path, 'r', encoding='utf-8') as f:
                            template_data = json.load(f)
                            logger.info(f"加载模板: {template_id} from {template_path}")
                            return template_data.get("config", {})
                except Exception as e:
                    logger.warning(f"加载模板失败 {template_path}: {e}")
                    continue
        
        # 如果找不到模板，返回空配置并记录警告
        logger.warning(f"未找到模板: {template_id}，使用默认配置")
        return {}
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """
        列出所有可用的项目模板
        
        Returns:
            模板列表
        """
        templates = []
        template_dirs = [
            Path("project_templates"),
            self.projects_dir.parent / "project_templates"
        ]
        
        for template_dir in template_dirs:
            if not template_dir.exists():
                continue
            
            for template_file in template_dir.glob("*.yaml"):
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        template_data = yaml.safe_load(f) or {}
                        templates.append({
                            "id": template_file.stem,
                            "name": template_data.get("name", template_file.stem),
                            "description": template_data.get("description", ""),
                            "metadata": template_data.get("metadata", {})
                        })
                except Exception as e:
                    logger.warning(f"读取模板文件失败 {template_file}: {e}")
        
        return templates

