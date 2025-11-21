"""
Agent Skills 系统
模块化的 AI 知识系统，提供专业写作技能
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
from enum import Enum
import yaml
import logging
import re

logger = logging.getLogger(__name__)


class SkillLevel(str, Enum):
    """技能层级"""
    EXTENSION = "extension"  # 扩展技能（系统内置）
    PROJECT = "project"      # 项目技能
    PERSONAL = "personal"    # 个人技能


class AgentSkill:
    """Agent 技能"""
    
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        content: str,
        level: SkillLevel,
        tags: List[str] = None,
        activation_keywords: List[str] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.content = content
        self.level = level
        self.tags = tags or []
        self.activation_keywords = activation_keywords or []
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "content": self.content,
            "level": self.level.value,
            "tags": self.tags,
            "activation_keywords": self.activation_keywords
        }
    
    @classmethod
    def from_markdown(cls, file_path: Path, level: SkillLevel) -> 'AgentSkill':
        """从 Markdown 文件加载技能"""
        content = file_path.read_text(encoding='utf-8')
        
        # 解析 Markdown 元数据（YAML front matter）
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                metadata = yaml.safe_load(parts[1])
                content = parts[2].strip()
            except:
                metadata = {}
                content = content.strip()
        else:
            metadata = {}
            content = content.strip()
        
        # 从文件名获取 ID
        skill_id = file_path.stem
        
        return cls(
            id=skill_id,
            name=metadata.get('name', skill_id),
            description=metadata.get('description', ''),
            content=content,
            level=level,
            tags=metadata.get('tags', []),
            activation_keywords=metadata.get('activation_keywords', [])
        )


class AgentSkillsManager:
    """Agent Skills 管理器"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.skills: Dict[str, AgentSkill] = {}
        self._load_skills()
    
    def _load_skills(self):
        """加载所有技能"""
        # 加载扩展技能
        extension_skills_dir = Path(__file__).parent.parent / "agent_skills" / "extension"
        if extension_skills_dir.exists():
            self._load_skills_from_dir(extension_skills_dir, SkillLevel.EXTENSION)
        
        # 加载项目技能
        project_skills_dir = self.project_root / ".agent" / "skills"
        if project_skills_dir.exists():
            self._load_skills_from_dir(project_skills_dir, SkillLevel.PROJECT)
        
        # 加载个人技能
        personal_skills_dir = Path.home() / ".qcbigma" / "skills"
        if personal_skills_dir.exists():
            self._load_skills_from_dir(personal_skills_dir, SkillLevel.PERSONAL)
    
    def _load_skills_from_dir(self, skills_dir: Path, level: SkillLevel):
        """从目录加载技能"""
        for md_file in skills_dir.glob("*.md"):
            try:
                skill = AgentSkill.from_markdown(md_file, level)
                self.skills[skill.id] = skill
                logger.info(f"Loaded skill: {skill.name} ({level.value})")
            except Exception as e:
                logger.error(f"Failed to load skill from {md_file}: {e}")
    
    def get_skill(self, skill_id: str) -> Optional[AgentSkill]:
        """获取技能"""
        return self.skills.get(skill_id)
    
    def list_skills(self, level: Optional[SkillLevel] = None, tags: List[str] = None) -> List[AgentSkill]:
        """列出技能"""
        skills = list(self.skills.values())
        
        if level:
            skills = [s for s in skills if s.level == level]
        
        if tags:
            skills = [s for s in skills if any(tag in s.tags for tag in tags)]
        
        return skills
    
    def activate_skills(self, context: str, task_description: str) -> List[AgentSkill]:
        """根据上下文和任务描述激活相关技能"""
        activated = []
        
        # 计算每个技能的匹配度
        for skill in self.skills.values():
            score = self._calculate_relevance_score(skill, context, task_description)
            if score > 0.3:  # 阈值可配置
                activated.append((skill, score))
        
        # 按匹配度排序
        activated.sort(key=lambda x: x[1], reverse=True)
        
        # 返回前 5 个最相关的技能
        return [skill for skill, score in activated[:5]]
    
    def _calculate_relevance_score(
        self,
        skill: AgentSkill,
        context: str,
        task_description: str
    ) -> float:
        """计算技能相关性分数"""
        score = 0.0
        
        # 检查激活关键词
        text = (context + " " + task_description).lower()
        for keyword in skill.activation_keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in text:
                score += 0.2
        
        # 检查标签匹配
        # 这里可以添加更复杂的匹配逻辑
        
        return min(score, 1.0)
    
    def inject_skills_into_prompt(
        self,
        base_prompt: str,
        activated_skills: List[AgentSkill]
    ) -> str:
        """将激活的技能注入到提示词中"""
        if not activated_skills:
            return base_prompt
        
        skills_content = "\n\n## 相关专业知识\n\n"
        for skill in activated_skills:
            skills_content += f"### {skill.name}\n{skill.content}\n\n"
        
        return base_prompt + skills_content

