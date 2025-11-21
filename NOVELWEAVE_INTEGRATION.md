# NovelWeave 优点融合方案

基于 [NovelWeave 项目](https://github.com/wordflowlab/novelweave) 的优秀设计，本文档说明如何将其核心优点融入到 NovelCorpusExtractor 系统中。

## 📋 NovelWeave 核心优点分析

### 1. 七步方法论（Seven-Step Methodology）

NovelWeave 实现了结构化的创作流程，从原则定义到质量验证的完整闭环：

1. **`/constitution`** - 建立核心创作原则（不可妥协的写作原则）
2. **`/specify`** - 定义故事需求（类似产品需求文档 PRD）
3. **`/clarify`** - 关键澄清（AI 识别歧义，生成最多 5 个关键问题）
4. **`/plan`** - 创作计划（将抽象需求转化为具体技术方案）
5. **`/tasks`** - 任务分解（将计划分解为可执行的写作任务）
6. **`/write`** - 执行写作（基于任务列表进行实际写作）
7. **`/analyze`** - 全面验证（验证情节一致性、时间线准确性等）

**优点**：
- ✅ 结构化流程，避免遗漏关键步骤
- ✅ 早期发现和解决歧义
- ✅ 从抽象到具体的渐进式创作
- ✅ 质量保证内置在流程中

### 2. Agent Skills 系统

模块化的 AI 知识系统，提供专业写作技能：

- **内置技能**：14 个专业写作技能（类型知识、写作技巧、质量保证等）
- **三层系统**：
  - **扩展技能**：系统内置的专业技能
  - **项目技能**：项目特定的指导原则（`.agent/skills/`）
  - **个人技能**：个人可复用的知识库
- **智能激活**：AI 根据任务上下文自动选择相关技能
- **自定义技能**：使用简单的 Markdown 创建自己的专业知识模块

**优点**：
- ✅ 模块化知识管理
- ✅ 可扩展和可复用
- ✅ 上下文感知的技能选择
- ✅ 团队协作友好

### 3. 斜杠命令系统（Slash Commands）

类似 novel-writer CLI 的命令系统，提供快速操作：

- `/constitution` - 创建或编辑创作原则
- `/specify` - 定义故事需求
- `/clarify` - 澄清歧义
- `/plan` - 生成创作计划
- `/tasks` - 管理任务列表
- `/write` - 开始写作
- `/analyze` - 验证质量

**优点**：
- ✅ 快速访问常用功能
- ✅ 统一的命令接口
- ✅ 支持自动补全和提示

### 4. 质量保证系统

内置的质量验证机制：

- **一致性检查**：验证角色特征、时间线、事实
- **情节跟踪**：确保所有情节线索都得到解决
- **时间线管理**：时间顺序准确性验证
- **风格一致性**：保持独特的写作声音

**优点**：
- ✅ 自动化质量检查
- ✅ 早期发现问题
- ✅ 减少返工

## 🔄 融合方案

### 方案一：七步方法论集成

#### 1.1 创建七步方法论工作流

```python
# core/workflows/seven_step_workflow.py

from enum import Enum
from typing import Dict, List, Optional, Any
from .base import WorkflowBase, WorkflowStage

class SevenStepStage(str, Enum):
    """七步方法论阶段"""
    CONSTITUTION = "constitution"  # 建立创作原则
    SPECIFY = "specify"            # 定义故事需求
    CLARIFY = "clarify"            # 关键澄清
    PLAN = "plan"                  # 创作计划
    TASKS = "tasks"                # 任务分解
    WRITE = "write"                # 执行写作
    ANALYZE = "analyze"            # 全面验证

class SevenStepWorkflow(WorkflowBase):
    """七步方法论工作流"""
    
    def get_stages(self) -> List[WorkflowStage]:
        """获取七步方法论阶段"""
        return [
            WorkflowStage(
                name=SevenStepStage.CONSTITUTION.value,
                label="建立创作原则",
                order=1,
                config={
                    "description": "定义不可妥协的写作原则、风格指南和核心价值观",
                    "output_type": "constitution",
                    "required": True
                }
            ),
            WorkflowStage(
                name=SevenStepStage.SPECIFY.value,
                label="定义故事需求",
                order=2,
                config={
                    "description": "定义要创建的故事、目标受众和成功标准",
                    "output_type": "specification",
                    "required": True
                }
            ),
            WorkflowStage(
                name=SevenStepStage.CLARIFY.value,
                label="关键澄清",
                order=3,
                config={
                    "description": "AI 识别规范中的歧义并生成最多 5 个关键问题",
                    "output_type": "clarifications",
                    "max_questions": 5,
                    "required": True
                }
            ),
            WorkflowStage(
                name=SevenStepStage.PLAN.value,
                label="创作计划",
                order=4,
                config={
                    "description": "将抽象需求转化为具体技术方案",
                    "output_type": "plan",
                    "required": True
                }
            ),
            WorkflowStage(
                name=SevenStepStage.TASKS.value,
                label="任务分解",
                order=5,
                config={
                    "description": "将计划分解为可执行的写作任务",
                    "output_type": "tasks",
                    "required": True
                }
            ),
            WorkflowStage(
                name=SevenStepStage.WRITE.value,
                label="执行写作",
                order=6,
                config={
                    "description": "基于任务列表进行实际写作",
                    "output_type": "content",
                    "iterative": True,
                    "required": True
                }
            ),
            WorkflowStage(
                name=SevenStepStage.ANALYZE.value,
                label="全面验证",
                order=7,
                config={
                    "description": "验证情节一致性、时间线准确性等",
                    "output_type": "analysis",
                    "required": True
                }
            ),
        ]
    
    async def expand_stage(self, stage: WorkflowStage, parent_card_id: str) -> Dict[str, Any]:
        """扩展阶段"""
        if stage.name == SevenStepStage.CONSTITUTION.value:
            return await self._create_constitution(parent_card_id)
        elif stage.name == SevenStepStage.SPECIFY.value:
            return await self._create_specification(parent_card_id)
        elif stage.name == SevenStepStage.CLARIFY.value:
            return await self._create_clarifications(parent_card_id)
        elif stage.name == SevenStepStage.PLAN.value:
            return await self._create_plan(parent_card_id)
        elif stage.name == SevenStepStage.TASKS.value:
            return await self._create_tasks(parent_card_id)
        elif stage.name == SevenStepStage.WRITE.value:
            return await self._execute_writing(parent_card_id)
        elif stage.name == SevenStepStage.ANALYZE.value:
            return await self._analyze_quality(parent_card_id)
    
    async def _create_constitution(self, parent_card_id: str) -> Dict[str, Any]:
        """创建创作原则"""
        # 获取项目上下文
        context = self._get_project_context()
        
        prompt = f"""请为这个小说项目建立创作原则（Constitution）。

创作原则是不可妥协的写作原则、风格指南和核心价值观，将指导整个创作过程。

项目上下文：
{context}

请生成以下内容：
1. 核心创作原则（3-5 条）
2. 风格指南（语言风格、叙事视角等）
3. 核心价值观（故事要传达的主题和价值观）
4. 不可妥协的规则（必须遵守的规则）

以结构化的格式输出。"""
        
        result = await self.llm_client.generate(prompt)
        
        # 创建卡片
        card = self.card_manager.create_card(
            self.project_id,
            "constitution",
            {
                "content": result,
                "stage": "constitution",
                "parent_id": parent_card_id
            }
        )
        
        return {
            "card_id": card['id'],
            "content": result,
            "stage": "constitution"
        }
    
    async def _create_specification(self, parent_card_id: str) -> Dict[str, Any]:
        """创建故事需求规范"""
        # 获取创作原则
        constitution_card = self.card_manager.get_card(parent_card_id)
        constitution = constitution_card.get('content', {})
        
        prompt = f"""基于以下创作原则，定义详细的故事需求规范（Specification）。

创作原则：
{constitution}

请生成类似产品需求文档（PRD）的故事规范，包括：
1. 故事概述（一句话梗概）
2. 目标受众
3. 故事类型和风格
4. 核心冲突和主题
5. 主要角色（简要描述）
6. 故事结构（三幕式/英雄之旅等）
7. 成功标准（如何判断故事成功）

以结构化的格式输出。"""
        
        result = await self.llm_client.generate(prompt)
        
        card = self.card_manager.create_card(
            self.project_id,
            "specification",
            {
                "content": result,
                "stage": "specify",
                "parent_id": parent_card_id
            }
        )
        
        return {
            "card_id": card['id'],
            "content": result,
            "stage": "specify"
        }
    
    async def _create_clarifications(self, parent_card_id: str) -> Dict[str, Any]:
        """创建关键澄清问题"""
        # 获取规范
        spec_card = self.card_manager.get_card(parent_card_id)
        specification = spec_card.get('content', {})
        
        prompt = f"""分析以下故事规范，识别可能存在的歧义和模糊之处。

故事规范：
{specification}

请生成最多 5 个关键问题，这些问题需要澄清以确保后续创作顺利进行。
每个问题应该：
1. 针对规范中的具体模糊点
2. 对后续创作有重要影响
3. 需要明确的答案

格式：
问题1：[问题描述]
问题2：[问题描述]
...

然后，请为每个问题提供建议的答案选项（如果有）。"""
        
        result = await self.llm_client.generate(prompt)
        
        card = self.card_manager.create_card(
            self.project_id,
            "clarifications",
            {
                "content": result,
                "stage": "clarify",
                "parent_id": parent_card_id,
                "questions": self._extract_questions(result)
            }
        )
        
        return {
            "card_id": card['id'],
            "content": result,
            "questions": self._extract_questions(result),
            "stage": "clarify"
        }
    
    async def _create_plan(self, parent_card_id: str) -> Dict[str, Any]:
        """创建创作计划"""
        # 获取前面的所有阶段内容
        context = self._get_all_previous_stages(parent_card_id)
        
        prompt = f"""基于以下信息，创建详细的创作计划（Plan）。

项目上下文：
{context}

请将抽象的需求转化为具体的技术方案，包括：
1. 章节结构（章节数量和大致内容）
2. 角色弧线（主要角色的成长轨迹）
3. 世界观构建（如果需要）
4. 情节时间线（主要事件的时间顺序）
5. 伏笔布局（关键伏笔的埋设和回收）
6. 写作策略（如何实现创作原则和规范）

以结构化的格式输出。"""
        
        result = await self.llm_client.generate(prompt)
        
        card = self.card_manager.create_card(
            self.project_id,
            "plan",
            {
                "content": result,
                "stage": "plan",
                "parent_id": parent_card_id
            }
        )
        
        return {
            "card_id": card['id'],
            "content": result,
            "stage": "plan"
        }
    
    async def _create_tasks(self, parent_card_id: str) -> Dict[str, Any]:
        """创建任务分解"""
        # 获取计划
        plan_card = self.card_manager.get_card(parent_card_id)
        plan = plan_card.get('content', {})
        
        prompt = f"""将以下创作计划分解为可执行的写作任务（Tasks）。

创作计划：
{plan}

请创建任务列表，每个任务应该：
1. 有明确的描述
2. 有优先级（高/中/低）
3. 有依赖关系（如果有）
4. 有估算的工作量
5. 有验收标准

任务应该按照执行顺序排列，并考虑依赖关系。"""
        
        result = await self.llm_client.generate(prompt)
        
        card = self.card_manager.create_card(
            self.project_id,
            "tasks",
            {
                "content": result,
                "stage": "tasks",
                "parent_id": parent_card_id,
                "tasks": self._extract_tasks(result)
            }
        )
        
        return {
            "card_id": card['id'],
            "content": result,
            "tasks": self._extract_tasks(result),
            "stage": "tasks"
        }
    
    async def _execute_writing(self, parent_card_id: str) -> Dict[str, Any]:
        """执行写作"""
        # 获取任务列表和所有上下文
        context = self._get_all_previous_stages(parent_card_id)
        tasks_card = self.card_manager.get_card(parent_card_id)
        tasks = tasks_card.get('tasks', [])
        
        # 选择下一个要执行的任务
        next_task = self._get_next_task(tasks)
        
        if not next_task:
            return {
                "message": "所有任务已完成",
                "stage": "write",
                "completed": True
            }
        
        prompt = f"""基于以下上下文，执行写作任务。

项目上下文：
{context}

当前任务：
{next_task}

请按照创作原则和规范，完成这个写作任务。
输出应该：
1. 符合创作原则
2. 符合故事规范
3. 符合创作计划
4. 达到任务的验收标准"""
        
        result = await self.llm_client.generate(prompt)
        
        # 创建内容卡片
        card = self.card_manager.create_card(
            self.project_id,
            "content",
            {
                "content": result,
                "stage": "write",
                "parent_id": parent_card_id,
                "task_id": next_task.get('id'),
                "task_description": next_task.get('description')
            }
        )
        
        # 更新任务状态
        self._mark_task_completed(next_task['id'])
        
        return {
            "card_id": card['id'],
            "content": result,
            "task": next_task,
            "stage": "write",
            "has_more_tasks": len([t for t in tasks if not t.get('completed')]) > 0
        }
    
    async def _analyze_quality(self, parent_card_id: str) -> Dict[str, Any]:
        """全面验证质量"""
        # 获取所有已写内容
        all_content = self._get_all_written_content(parent_card_id)
        context = self._get_all_previous_stages(parent_card_id)
        
        prompt = f"""对以下创作内容进行全面质量验证（Analysis）。

项目上下文：
{context}

已写内容：
{all_content}

请验证以下方面：
1. **情节一致性**：检查情节逻辑是否一致，是否有矛盾
2. **时间线准确性**：验证事件的时间顺序是否正确
3. **角色发展**：检查角色行为是否符合设定，角色弧线是否完整
4. **创作原则遵循**：验证是否遵循了创作原则
5. **规范符合度**：检查是否符合故事规范
6. **伏笔处理**：检查伏笔是否合理埋设和回收
7. **风格一致性**：验证写作风格是否一致

对于发现的问题，请提供：
- 问题描述
- 问题位置（章节/段落）
- 严重程度（高/中/低）
- 修复建议"""
        
        result = await self.llm_client.generate(prompt)
        
        card = self.card_manager.create_card(
            self.project_id,
            "analysis",
            {
                "content": result,
                "stage": "analyze",
                "parent_id": parent_card_id,
                "issues": self._extract_issues(result)
            }
        )
        
        return {
            "card_id": card['id'],
            "content": result,
            "issues": self._extract_issues(result),
            "stage": "analyze"
        }
    
    def _get_project_context(self) -> str:
        """获取项目上下文"""
        # 实现获取项目上下文逻辑
        pass
    
    def _get_all_previous_stages(self, current_card_id: str) -> str:
        """获取所有前面阶段的内容"""
        # 实现获取前面阶段内容的逻辑
        pass
    
    def _extract_questions(self, text: str) -> List[Dict]:
        """从文本中提取问题"""
        # 实现问题提取逻辑
        pass
    
    def _extract_tasks(self, text: str) -> List[Dict]:
        """从文本中提取任务"""
        # 实现任务提取逻辑
        pass
    
    def _get_next_task(self, tasks: List[Dict]) -> Optional[Dict]:
        """获取下一个要执行的任务"""
        # 实现任务选择逻辑
        pass
    
    def _mark_task_completed(self, task_id: str):
        """标记任务为已完成"""
        # 实现任务状态更新逻辑
        pass
    
    def _get_all_written_content(self, parent_card_id: str) -> str:
        """获取所有已写内容"""
        # 实现获取已写内容的逻辑
        pass
    
    def _extract_issues(self, text: str) -> List[Dict]:
        """从分析文本中提取问题"""
        # 实现问题提取逻辑
        pass
```

### 方案二：Agent Skills 系统集成

#### 2.1 创建 Agent Skills 系统

```python
# core/agent_skills.py

from typing import Dict, List, Optional, Any
from pathlib import Path
from enum import Enum
import yaml
import logging

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
            metadata = yaml.safe_load(parts[1])
            content = parts[2].strip()
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
        personal_skills_dir = Path.home() / ".novelweave" / "skills"
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
            if keyword.lower() in text:
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
```

#### 2.2 创建内置技能示例

```markdown
# agent_skills/extension/romance_writing.md

---
name: 言情小说写作技巧
description: 专业言情小说写作知识和技巧
tags: [genre, romance, writing]
activation_keywords: [言情, 爱情, 恋爱, 感情线, 情感]
---

## 言情小说核心要素

### 情感发展
- 情感线应该循序渐进，有起承转合
- 避免一见钟情（除非是特定设定）
- 通过事件和互动推进感情发展

### 角色塑造
- 主角要有明确的性格特征和成长弧线
- 配角要有自己的故事线，不能只是工具人
- 反派要有合理的动机

### 冲突设计
- 外部冲突：家庭、社会、环境等
- 内部冲突：性格、价值观、过去经历等
- 情感冲突：误会、嫉妒、不安全感等

### 节奏控制
- 情感高潮要合理分布
- 甜宠和虐心要平衡
- 避免过度拖沓或过快发展

## 常见问题

1. **感情线单薄**：增加情感细节和内心描写
2. **角色脸谱化**：给角色更多维度的性格特征
3. **冲突不够**：增加内外冲突的层次
```

### 方案三：斜杠命令系统集成

#### 3.1 创建斜杠命令处理器

```python
# core/slash_commands.py

from typing import Dict, List, Optional, Callable, Any
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)

class SlashCommand:
    """斜杠命令"""
    
    def __init__(
        self,
        name: str,
        description: str,
        handler: Callable,
        aliases: List[str] = None,
        parameters: List[Dict] = None
    ):
        self.name = name
        self.description = description
        self.handler = handler
        self.aliases = aliases or []
        self.parameters = parameters or []
    
    def matches(self, command_text: str) -> bool:
        """检查命令是否匹配"""
        command_text = command_text.strip().lower()
        if command_text.startswith(f"/{self.name}"):
            return True
        for alias in self.aliases:
            if command_text.startswith(f"/{alias}"):
                return True
        return False
    
    async def execute(self, command_text: str, context: Dict) -> Any:
        """执行命令"""
        # 解析参数
        args = self._parse_args(command_text)
        return await self.handler(args, context)
    
    def _parse_args(self, command_text: str) -> Dict:
        """解析命令参数"""
        # 简单的参数解析实现
        parts = command_text.split()
        args = {}
        for i, param in enumerate(self.parameters):
            if i + 1 < len(parts):
                args[param['name']] = parts[i + 1]
        return args

class SlashCommandProcessor:
    """斜杠命令处理器"""
    
    def __init__(self, workflow_manager=None, card_manager=None):
        self.workflow_manager = workflow_manager
        self.card_manager = card_manager
        self.commands: Dict[str, SlashCommand] = {}
        self._register_default_commands()
    
    def _register_default_commands(self):
        """注册默认命令"""
        # /constitution
        self.register_command(SlashCommand(
            name="constitution",
            description="建立或编辑创作原则",
            handler=self._handle_constitution,
            aliases=["const", "原则"]
        ))
        
        # /specify
        self.register_command(SlashCommand(
            name="specify",
            description="定义故事需求规范",
            handler=self._handle_specify,
            aliases=["spec", "规范", "需求"]
        ))
        
        # /clarify
        self.register_command(SlashCommand(
            name="clarify",
            description="澄清歧义，生成关键问题",
            handler=self._handle_clarify,
            aliases=["clar", "澄清", "问题"]
        ))
        
        # /plan
        self.register_command(SlashCommand(
            name="plan",
            description="生成创作计划",
            handler=self._handle_plan,
            aliases=["计划", "规划"]
        ))
        
        # /tasks
        self.register_command(SlashCommand(
            name="tasks",
            description="管理任务列表",
            handler=self._handle_tasks,
            aliases=["task", "任务"]
        ))
        
        # /write
        self.register_command(SlashCommand(
            name="write",
            description="开始写作",
            handler=self._handle_write,
            aliases=["写作", "写"]
        ))
        
        # /analyze
        self.register_command(SlashCommand(
            name="analyze",
            description="验证质量和一致性",
            handler=self._handle_analyze,
            aliases=["analysis", "验证", "分析"]
        ))
    
    def register_command(self, command: SlashCommand):
        """注册命令"""
        self.commands[command.name] = command
        for alias in command.aliases:
            self.commands[alias] = command
    
    async def process(self, command_text: str, context: Dict) -> Dict:
        """处理命令"""
        command_text = command_text.strip()
        
        if not command_text.startswith("/"):
            return {"error": "命令必须以 / 开头"}
        
        # 查找匹配的命令
        for command in self.commands.values():
            if command.matches(command_text):
                try:
                    result = await command.execute(command_text, context)
                    return {
                        "success": True,
                        "command": command.name,
                        "result": result
                    }
                except Exception as e:
                    logger.error(f"执行命令失败: {e}")
                    return {
                        "success": False,
                        "error": str(e)
                    }
        
        return {"error": f"未知命令: {command_text.split()[0]}"}
    
    async def _handle_constitution(self, args: Dict, context: Dict) -> Dict:
        """处理 /constitution 命令"""
        # 实现创建或编辑创作原则的逻辑
        pass
    
    async def _handle_specify(self, args: Dict, context: Dict) -> Dict:
        """处理 /specify 命令"""
        # 实现定义故事需求的逻辑
        pass
    
    async def _handle_clarify(self, args: Dict, context: Dict) -> Dict:
        """处理 /clarify 命令"""
        # 实现澄清歧义的逻辑
        pass
    
    async def _handle_plan(self, args: Dict, context: Dict) -> Dict:
        """处理 /plan 命令"""
        # 实现生成创作计划的逻辑
        pass
    
    async def _handle_tasks(self, args: Dict, context: Dict) -> Dict:
        """处理 /tasks 命令"""
        # 实现任务管理的逻辑
        pass
    
    async def _handle_write(self, args: Dict, context: Dict) -> Dict:
        """处理 /write 命令"""
        # 实现写作的逻辑
        pass
    
    async def _handle_analyze(self, args: Dict, context: Dict) -> Dict:
        """处理 /analyze 命令"""
        # 实现质量验证的逻辑
        pass
    
    def list_commands(self) -> List[Dict]:
        """列出所有可用命令"""
        unique_commands = {}
        for name, command in self.commands.items():
            if command.name not in unique_commands:
                unique_commands[command.name] = command
        
        return [
            {
                "name": cmd.name,
                "description": cmd.description,
                "aliases": cmd.aliases
            }
            for cmd in unique_commands.values()
        ]
```

## 📊 集成优先级

### 高优先级（立即实施）

1. ✅ **七步方法论工作流** - 提供结构化创作流程
2. ✅ **Agent Skills 系统** - 模块化知识管理
3. ✅ **斜杠命令系统** - 快速访问常用功能

### 中优先级（后续实施）

4. ⏳ **质量保证增强** - 集成到七步方法论的 analyze 阶段
5. ⏳ **技能自动激活优化** - 改进技能选择算法
6. ⏳ **命令自动补全** - 前端支持命令提示

### 低优先级（可选）

7. ⏸️ **技能市场** - 分享和下载技能
8. ⏸️ **命令插件系统** - 支持自定义命令

## 🔗 与现有功能集成

### 与 NovelForge 功能集成

- **七步方法论** ↔ **雪花式创作流程**：可以结合使用
- **Agent Skills** ↔ **自由上下文注入**：技能可以作为上下文注入
- **斜杠命令** ↔ **灵感助手**：命令可以在对话中使用

### 与现有 Agent 集成

- **PlannerAgent** ↔ **七步方法论**：plan 阶段可以使用 PlannerAgent
- **AnalystAgent** ↔ **analyze 阶段**：analyze 阶段可以使用 AnalystAgent
- **StylistAgent** ↔ **Agent Skills**：风格技能可以作为 Agent Skill

## 📝 实施步骤

1. **阶段一**：实现七步方法论工作流基础框架
2. **阶段二**：实现 Agent Skills 系统核心功能
3. **阶段三**：实现斜杠命令系统
4. **阶段四**：集成到现有工作流和 API
5. **阶段五**：前端界面支持
6. **阶段六**：测试和优化

## 📚 参考资源

- [NovelWeave GitHub](https://github.com/wordflowlab/novelweave)
- [novel-writer 方法论](https://github.com/wordflowlab/novel-writer)
- [Agent Skills 用户指南](https://github.com/wordflowlab/novelweave/docs/agent-skills)

---

**最后更新**：2025-01-XX


