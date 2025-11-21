# NovelForge 功能融合方案

## 概述

本文档详细说明如何将 NovelForge 的核心功能融合到现有的 NovelCorpusExtractor 系统中，实现从"语料提取系统"向"智能创作系统"的全面升级。

## 一、系统架构升级

### 1.1 核心概念扩展

#### 卡片系统（Card System）
- **定义**：所有创作元素（角色、场景、大纲、章节等）都以"卡片"形式存在
- **结构**：每个卡片包含唯一ID、类型、内容、元数据、关联关系
- **树形组织**：卡片以树形结构组织，支持父子关系和引用关系

#### 项目系统（Project System）
- **项目**：独立的创作单元，包含完整的卡片集合和配置
- **跨项目引用**：支持在不同项目间引用卡片内容
- **项目模板**：可保存和复用项目结构模板

### 1.2 新增目录结构

```
NovelCorpusExtractor/
├── core/
│   ├── card_manager.py          # 卡片管理系统（新增）
│   ├── project_manager.py       # 项目管理系统（新增）
│   ├── dynamic_schema.py        # 动态输出模型（新增）
│   ├── context_injector.py      # 自由上下文注入（新增）
│   ├── knowledge_graph.py       # 知识图谱驱动（新增）
│   ├── inspiration_assistant.py # 灵感助手（新增）
│   ├── inspiration_workspace.py # 灵感工作台（新增）
│   ├── snowflake_workflow.py    # 雪花式创作流程（新增）
│   └── config_manager.py        # 配置管理器（增强）
├── schemas/                      # 动态Schema定义（新增）
│   ├── character_schema.py
│   ├── scene_schema.py
│   ├── outline_schema.py
│   └── custom_schemas/          # 用户自定义Schema
├── projects/                     # 项目存储（新增）
│   ├── {project_id}/
│   │   ├── cards/               # 卡片数据
│   │   ├── config.yaml          # 项目配置
│   │   └── knowledge_graph.db   # 知识图谱数据库
├── inspiration/                  # 灵感工作台数据（新增）
│   ├── free_cards/              # 自由卡片
│   └── conversations/           # 对话记录
└── workflows/                    # 创作流程模板（新增）
    ├── snowflake/
    ├── hero_journey/
    └── custom/
```

## 二、核心功能详细设计

### 2.1 动态输出模型（Dynamic Output Schema）

#### 2.1.1 技术实现
- **基础库**：Pydantic v2
- **可视化界面**：前端Schema编辑器
- **验证机制**：AI生成内容自动校验

#### 2.1.2 架构设计

```python
# core/dynamic_schema.py

from pydantic import BaseModel, Field, create_model
from typing import Dict, Any, Optional, List
from enum import Enum

class SchemaFieldType(str, Enum):
    """字段类型枚举"""
    STRING = "string"
    TEXT = "text"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    ENUM = "enum"
    REFERENCE = "reference"  # 引用其他卡片

class SchemaField(BaseModel):
    """Schema字段定义"""
    name: str
    type: SchemaFieldType
    description: str
    required: bool = True
    default: Any = None
    constraints: Dict[str, Any] = {}  # 约束条件（如min_length, max_length等）
    enum_values: Optional[List[str]] = None  # 枚举值列表
    reference_type: Optional[str] = None  # 引用类型（如"character", "scene"）

class DynamicSchema(BaseModel):
    """动态Schema定义"""
    id: str
    name: str
    description: str
    card_type: str  # 卡片类型（character, scene, outline等）
    fields: List[SchemaField]
    version: str = "1.0.0"
    created_at: str
    updated_at: str

class SchemaManager:
    """Schema管理器"""
    
    def __init__(self, schema_dir: str = "schemas"):
        self.schema_dir = Path(schema_dir)
        self.schemas: Dict[str, DynamicSchema] = {}
        self._load_schemas()
    
    def create_schema(self, schema_def: DynamicSchema) -> DynamicSchema:
        """创建新的Schema"""
        # 验证Schema定义
        self._validate_schema(schema_def)
        # 生成Pydantic模型
        pydantic_model = self._generate_pydantic_model(schema_def)
        # 保存Schema
        self._save_schema(schema_def)
        return schema_def
    
    def _generate_pydantic_model(self, schema: DynamicSchema) -> type:
        """根据Schema定义生成Pydantic模型"""
        fields = {}
        for field in schema.fields:
            field_type = self._map_field_type(field.type)
            field_def = Field(
                default=field.default if not field.required else ...,
                description=field.description,
                **field.constraints
            )
            fields[field.name] = (field_type, field_def)
        
        return create_model(schema.name, **fields)
    
    def validate_output(self, schema_id: str, output: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """验证AI输出是否符合Schema"""
        schema = self.schemas.get(schema_id)
        if not schema:
            return False, f"Schema {schema_id} not found"
        
        try:
            pydantic_model = self._generate_pydantic_model(schema)
            instance = pydantic_model(**output)
            return True, None
        except Exception as e:
            return False, str(e)
```

#### 2.1.3 前端集成
- Schema可视化编辑器
- 实时预览和验证
- Schema模板库

### 2.2 自由上下文注入（Free Context Injection）

#### 2.2.1 表达式语言设计

```python
# core/context_injector.py

from typing import Dict, Any, List, Optional
import re
from pathlib import Path

class ContextExpression:
    """上下文表达式解析器"""
    
    # 表达式语法示例：
    # - @current.character.enemies  # 当前角色的所有仇人
    # - @volume(1).scenes  # 第一卷的所有场景
    # - @filter(cards, type="treasure", level>5)  # 所有等级大于5的宝物
    # - @project("project_id").characters  # 其他项目的角色
    
    EXPRESSION_PATTERNS = {
        'current': r'@current\.(\w+)(?:\.(\w+))?',
        'volume': r'@volume\((\d+)\)\.(\w+)',
        'filter': r'@filter\((\w+),\s*(.+)\)',
        'project': r'@project\(["\']?(\w+)["\']?\)\.(\w+)',
        'reference': r'@ref\(["\']?([\w-]+)["\']?\)',
    }
    
    def __init__(self, card_manager, project_manager):
        self.card_manager = card_manager
        self.project_manager = project_manager
    
    def parse_expression(self, expression: str, context: Dict[str, Any]) -> Any:
        """解析表达式并返回结果"""
        # 替换表达式为实际值
        result = expression
        
        # 处理 @current 表达式
        result = self._replace_current(result, context)
        
        # 处理 @volume 表达式
        result = self._replace_volume(result, context)
        
        # 处理 @filter 表达式
        result = self._replace_filter(result, context)
        
        # 处理 @project 表达式
        result = self._replace_project(result, context)
        
        # 处理 @ref 表达式
        result = self._replace_reference(result, context)
        
        return result
    
    def _replace_current(self, text: str, context: Dict[str, Any]) -> str:
        """替换 @current 表达式"""
        pattern = self.EXPRESSION_PATTERNS['current']
        
        def replacer(match):
            card_type = match.group(1)
            field = match.group(2) if match.group(2) else None
            
            current_card = context.get('current_card')
            if not current_card:
                return ""
            
            if card_type == 'character':
                card = self.card_manager.get_card(current_card['id'])
                if field:
                    return str(card.get('data', {}).get(field, ''))
                return self._format_card(card)
            
            # 处理其他类型...
            return ""
        
        return re.sub(pattern, replacer, text)
    
    def _replace_volume(self, text: str, context: Dict[str, Any]) -> str:
        """替换 @volume 表达式"""
        pattern = self.EXPRESSION_PATTERNS['volume']
        
        def replacer(match):
            volume_num = int(match.group(1))
            card_type = match.group(2)
            
            # 获取指定卷的卡片
            cards = self.card_manager.get_cards_by_volume(volume_num, card_type)
            return self._format_cards(cards)
        
        return re.sub(pattern, replacer, text)
    
    def _replace_filter(self, text: str, context: Dict[str, Any]) -> str:
        """替换 @filter 表达式"""
        pattern = self.EXPRESSION_PATTERNS['filter']
        
        def replacer(match):
            collection_name = match.group(1)
            filter_conditions = match.group(2)
            
            # 解析过滤条件
            conditions = self._parse_filter_conditions(filter_conditions)
            
            # 获取集合
            collection = context.get(collection_name, [])
            
            # 应用过滤
            filtered = self._apply_filter(collection, conditions)
            return self._format_cards(filtered)
        
        return re.sub(pattern, replacer, text)
    
    def inject_into_prompt(self, prompt_template: str, context: Dict[str, Any]) -> str:
        """将上下文注入到提示词模板中"""
        return self.parse_expression(prompt_template, context)
```

#### 2.2.2 使用示例

```python
# 提示词模板
prompt = """
请为角色 @current.character.name 生成一段对话。

角色背景：
@current.character

相关角色：
@filter(characters, relationship="enemy")

场景信息：
@current.scene
"""

# 自动注入后
injected_prompt = """
请为角色 张三 生成一段对话。

角色背景：
姓名：张三
性格：勇敢、正义
...

相关角色：
- 李四（仇人）
- 王五（仇人）

场景信息：
地点：古战场
时间：黄昏
...
"""
```

### 2.3 知识图谱驱动（Knowledge Graph）

#### 2.3.1 Neo4j 集成

```python
# core/knowledge_graph.py

from neo4j import GraphDatabase
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class KnowledgeGraph:
    """知识图谱管理器"""
    
    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database
    
    def close(self):
        """关闭数据库连接"""
        self.driver.close()
    
    def create_character_node(self, character_id: str, properties: Dict[str, Any]):
        """创建角色节点"""
        with self.driver.session(database=self.database) as session:
            session.write_transaction(self._create_character, character_id, properties)
    
    def create_relationship(self, from_id: str, to_id: str, rel_type: str, properties: Dict[str, Any] = None):
        """创建关系"""
        with self.driver.session(database=self.database) as session:
            session.write_transaction(self._create_rel, from_id, to_id, rel_type, properties or {})
    
    def extract_relationships_from_text(self, text: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从文本中提取关系（使用AI）"""
        # 调用AI提取人物关系
        # 返回关系列表：[{from, to, type, properties}]
        pass
    
    def get_character_context(self, character_id: str, depth: int = 2) -> Dict[str, Any]:
        """获取角色的上下文信息（关系网络）"""
        with self.driver.session(database=self.database) as session:
            result = session.read_transaction(
                self._get_character_context, character_id, depth
            )
            return result
    
    def inject_into_prompt(self, character_id: str, prompt: str) -> str:
        """将知识图谱信息注入到提示词中"""
        context = self.get_character_context(character_id)
        
        # 格式化关系信息
        relationships_text = self._format_relationships(context)
        
        # 注入到提示词
        enhanced_prompt = f"""
{relationships_text}

{prompt}
"""
        return enhanced_prompt
    
    @staticmethod
    def _create_character(tx, character_id: str, properties: Dict[str, Any]):
        query = """
        CREATE (c:Character {id: $character_id})
        SET c += $properties
        RETURN c
        """
        tx.run(query, character_id=character_id, properties=properties)
    
    @staticmethod
    def _create_rel(tx, from_id: str, to_id: str, rel_type: str, properties: Dict[str, Any]):
        query = f"""
        MATCH (a:Character {{id: $from_id}})
        MATCH (b:Character {{id: $to_id}})
        CREATE (a)-[r:{rel_type} $properties]->(b)
        RETURN r
        """
        tx.run(query, from_id=from_id, to_id=to_id, properties=properties)
    
    @staticmethod
    def _get_character_context(tx, character_id: str, depth: int):
        query = f"""
        MATCH path = (c:Character {{id: $character_id}})-[*1..{depth}]-(related)
        RETURN path
        """
        result = tx.run(query, character_id=character_id)
        return [record["path"] for record in result]
```

#### 2.3.2 关系提取Agent

```python
# agents/relationship_extractor.py

class RelationshipExtractorAgent:
    """关系提取Agent"""
    
    def __init__(self, llm_client, knowledge_graph):
        self.llm_client = llm_client
        self.kg = knowledge_graph
    
    async def extract_from_text(self, text: str, existing_characters: List[Dict]) -> List[Dict]:
        """从文本中提取人物关系"""
        prompt = f"""
请从以下文本中提取人物关系：

文本：
{text}

已知角色：
{self._format_characters(existing_characters)}

请提取以下信息：
1. 人物之间的关系（如：父子、师徒、仇敌、恋人等）
2. 关系的性质（如：友好、敌对、中立等）
3. 关系的变化（如：从友好变为敌对）

返回JSON格式：
[
  {{
    "from": "角色A",
    "to": "角色B",
    "relationship_type": "仇敌",
    "properties": {{
      "intensity": "强烈",
      "reason": "杀父之仇",
      "current_status": "敌对"
    }}
  }}
]
"""
        
        response = await self.llm_client.generate(prompt)
        relationships = self._parse_response(response)
        
        # 保存到知识图谱
        for rel in relationships:
            self.kg.create_relationship(
                rel['from'], rel['to'], 
                rel['relationship_type'],
                rel.get('properties', {})
            )
        
        return relationships
```

### 2.4 灵感助手（Inspiration Assistant）

#### 2.4.1 对话式创作助手

```python
# core/inspiration_assistant.py

from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

class ConversationMessage:
    """对话消息"""
    def __init__(self, role: str, content: str, metadata: Dict[str, Any] = None):
        self.id = str(uuid.uuid4())
        self.role = role  # "user" or "assistant"
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()

class InspirationAssistant:
    """灵感助手"""
    
    def __init__(self, llm_client, card_manager, project_manager):
        self.llm_client = llm_client
        self.card_manager = card_manager
        self.project_manager = project_manager
        self.conversations: Dict[str, List[ConversationMessage]] = {}
    
    async def chat(
        self, 
        user_message: str, 
        context_card_id: Optional[str] = None,
        project_id: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """与助手对话"""
        
        # 获取或创建对话
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            self.conversations[conversation_id] = []
        
        conversation = self.conversations[conversation_id]
        
        # 添加上下文信息
        context = self._build_context(context_card_id, project_id)
        
        # 构建提示词
        prompt = self._build_prompt(user_message, context, conversation)
        
        # 调用AI
        response = await self.llm_client.generate(prompt)
        
        # 保存对话
        conversation.append(ConversationMessage("user", user_message))
        conversation.append(ConversationMessage("assistant", response))
        
        return {
            "conversation_id": conversation_id,
            "response": response,
            "suggestions": self._extract_suggestions(response)
        }
    
    def apply_to_card(self, conversation_id: str, card_id: str, message_indices: List[int]):
        """将对话成果应用到卡片"""
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # 提取选中的消息
        selected_messages = [conversation[i] for i in message_indices]
        
        # 合并内容
        merged_content = self._merge_messages(selected_messages)
        
        # 更新卡片
        card = self.card_manager.get_card(card_id)
        card['data'] = self._merge_card_data(card['data'], merged_content)
        self.card_manager.update_card(card_id, card)
    
    def _build_context(self, card_id: Optional[str], project_id: Optional[str]) -> Dict[str, Any]:
        """构建对话上下文"""
        context = {}
        
        if card_id:
            card = self.card_manager.get_card(card_id)
            context['current_card'] = card
            
            # 获取相关卡片
            related_cards = self.card_manager.get_related_cards(card_id)
            context['related_cards'] = related_cards
        
        if project_id:
            project = self.project_manager.get_project(project_id)
            context['project'] = project
        
        return context
```

### 2.5 灵感工作台（Inspiration Workspace）

#### 2.5.1 自由卡片系统

```python
# core/inspiration_workspace.py

from typing import Dict, List, Optional, Any
from pathlib import Path
import json

class FreeCard:
    """自由卡片（不受项目限制）"""
    def __init__(self, card_id: str, card_type: str, content: Dict[str, Any]):
        self.id = card_id
        self.type = card_type
        self.content = content
        self.tags: List[str] = []
        self.references: List[str] = []  # 引用的项目卡片ID
        self.created_at: str = ""
        self.updated_at: str = ""

class InspirationWorkspace:
    """灵感工作台"""
    
    def __init__(self, workspace_dir: str = "inspiration"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.free_cards: Dict[str, FreeCard] = {}
        self._load_free_cards()
    
    def create_free_card(self, card_type: str, content: Dict[str, Any]) -> FreeCard:
        """创建自由卡片"""
        card_id = str(uuid.uuid4())
        card = FreeCard(card_id, card_type, content)
        self.free_cards[card_id] = card
        self._save_free_card(card)
        return card
    
    def reference_project_card(self, free_card_id: str, project_id: str, card_id: str):
        """引用项目中的卡片"""
        card = self.free_cards.get(free_card_id)
        if not card:
            raise ValueError(f"Free card {free_card_id} not found")
        
        reference = f"{project_id}:{card_id}"
        if reference not in card.references:
            card.references.append(reference)
            self._save_free_card(card)
    
    def move_to_project(self, free_card_id: str, project_id: str) -> str:
        """将自由卡片移动到项目"""
        card = self.free_cards.get(free_card_id)
        if not card:
            raise ValueError(f"Free card {free_card_id} not found")
        
        # 在项目中创建新卡片
        project_manager = ProjectManager()
        new_card_id = project_manager.create_card(
            project_id, card.type, card.content
        )
        
        # 删除自由卡片
        del self.free_cards[free_card_id]
        self._delete_free_card(free_card_id)
        
        return new_card_id
    
    def copy_to_project(self, free_card_id: str, project_id: str) -> str:
        """将自由卡片复制到项目"""
        card = self.free_cards.get(free_card_id)
        if not card:
            raise ValueError(f"Free card {free_card_id} not found")
        
        # 在项目中创建新卡片（复制）
        project_manager = ProjectManager()
        new_card_id = project_manager.create_card(
            project_id, card.type, card.content.copy()
        )
        
        return new_card_id
```

### 2.6 雪花式创作流程（Snowflake Workflow）

#### 2.6.1 流程定义

```python
# core/snowflake_workflow.py

from typing import Dict, List, Optional, Any
from enum import Enum

class SnowflakeStage(str, Enum):
    """雪花创作法阶段"""
    ONE_SENTENCE = "one_sentence"  # 一句话梗概
    PARAGRAPH = "paragraph"  # 一段话扩展
    CHARACTER_SHEET = "character_sheet"  # 角色表
    SYNOPSIS = "synopsis"  # 大纲
    WORLDVIEW = "worldview"  # 世界观
    BLUEPRINT = "blueprint"  # 蓝图
    VOLUME = "volume"  # 分卷
    CHAPTER = "chapter"  # 章节
    CONTENT = "content"  # 正文

class SnowflakeWorkflow:
    """雪花式创作流程"""
    
    STAGE_ORDER = [
        SnowflakeStage.ONE_SENTENCE,
        SnowflakeStage.PARAGRAPH,
        SnowflakeStage.CHARACTER_SHEET,
        SnowflakeStage.SYNOPSIS,
        SnowflakeStage.WORLDVIEW,
        SnowflakeStage.BLUEPRINT,
        SnowflakeStage.VOLUME,
        SnowflakeStage.CHAPTER,
        SnowflakeStage.CONTENT,
    ]
    
    def __init__(self, project_id: str, card_manager, llm_client):
        self.project_id = project_id
        self.card_manager = card_manager
        self.llm_client = llm_client
    
    async def start_workflow(self) -> Dict[str, Any]:
        """启动雪花创作流程"""
        # 创建根卡片（一句话梗概）
        root_card = self.card_manager.create_card(
            self.project_id,
            "one_sentence",
            {"sentence": ""}
        )
        
        return {
            "workflow_id": str(uuid.uuid4()),
            "root_card_id": root_card['id'],
            "current_stage": SnowflakeStage.ONE_SENTENCE.value,
            "stages": [s.value for s in self.STAGE_ORDER]
        }
    
    async def expand_stage(self, stage: SnowflakeStage, parent_card_id: str) -> Dict[str, Any]:
        """扩展当前阶段"""
        parent_card = self.card_manager.get_card(parent_card_id)
        
        # 根据阶段生成内容
        if stage == SnowflakeStage.PARAGRAPH:
            content = await self._expand_to_paragraph(parent_card)
        elif stage == SnowflakeStage.CHARACTER_SHEET:
            content = await self._create_character_sheet(parent_card)
        elif stage == SnowflakeStage.SYNOPSIS:
            content = await self._create_synopsis(parent_card)
        # ... 其他阶段
        
        # 创建新卡片
        new_card = self.card_manager.create_card(
            self.project_id,
            stage.value,
            content,
            parent_id=parent_card_id
        )
        
        return new_card
    
    async def _expand_to_paragraph(self, parent_card: Dict[str, Any]) -> Dict[str, Any]:
        """扩展为一段话"""
        prompt = f"""
请将以下一句话梗概扩展为一段话（约200-300字）：

{parent_card['data']['sentence']}

要求：
1. 包含主要角色
2. 包含核心冲突
3. 包含故事背景
"""
        response = await self.llm_client.generate(prompt)
        return {"paragraph": response}
    
    async def _create_character_sheet(self, parent_card: Dict[str, Any]) -> Dict[str, Any]:
        """创建角色表"""
        # 从段落中提取角色信息
        # 生成角色卡片
        pass
    
    def get_workflow_tree(self) -> Dict[str, Any]:
        """获取工作流树形结构"""
        cards = self.card_manager.get_project_cards(self.project_id)
        return self._build_tree(cards)
    
    def _build_tree(self, cards: List[Dict[str, Any]]) -> Dict[str, Any]:
        """构建树形结构"""
        # 构建父子关系的树形结构
        pass
```

### 2.7 高度可配置系统

#### 2.7.1 配置管理器增强

```python
# core/config_manager.py

from typing import Dict, Any, Optional
from pathlib import Path
import yaml

class ConfigManager:
    """配置管理器（增强版）"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self._load_config()
    
    def get_model_config(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """获取模型配置"""
        if model_name:
            # 获取特定模型的配置
            return self.config.get("models", {}).get(model_name, {})
        return self.config.get("model", {})
    
    def get_prompt_template(self, template_name: str) -> str:
        """获取提示词模板"""
        templates = self.config.get("prompt_templates", {})
        return templates.get(template_name, "")
    
    def get_card_type_config(self, card_type: str) -> Dict[str, Any]:
        """获取卡片类型配置"""
        card_types = self.config.get("card_types", {})
        return card_types.get(card_type, {})
    
    def update_config(self, section: str, key: str, value: Any):
        """更新配置"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self._save_config()
```

#### 2.7.2 配置文件结构

```yaml
# config.yaml (增强版)

# 模型配置（支持多模型）
models:
  default:
    provider: "openai"
    model_name: "gpt-4"
    api_key: ""
    temperature: 0.7
    max_tokens: 2000
  
  creative:
    provider: "openai"
    model_name: "gpt-4"
    temperature: 0.9
    max_tokens: 3000
  
  analysis:
    provider: "deepseek"
    model_name: "deepseek-chat"
    temperature: 0.3
    max_tokens: 1000

# 提示词模板
prompt_templates:
  character_generation: |
    请生成一个角色：
    {context}
  
  scene_generation: |
    请生成一个场景：
    {context}

# 卡片类型配置
card_types:
  character:
    schema_id: "character_v1"
    default_fields:
      - name
      - age
      - personality
    required_fields:
      - name
  
  scene:
    schema_id: "scene_v1"
    default_fields:
      - location
      - time
      - participants

# 工作流配置
workflows:
  snowflake:
    enabled: true
    stages:
      - one_sentence
      - paragraph
      - character_sheet
      - synopsis
      - worldview
      - blueprint
      - volume
      - chapter
      - content
  
  hero_journey:
    enabled: false
    stages: [...]

# 知识图谱配置
knowledge_graph:
  enabled: true
  provider: "neo4j"
  uri: "bolt://localhost:7687"
  user: "neo4j"
  password: ""
  database: "novelforge"

# 灵感助手配置
inspiration_assistant:
  enabled: true
  model: "default"
  max_context_cards: 10
  enable_cross_project: true

# 灵感工作台配置
inspiration_workspace:
  enabled: true
  max_free_cards: 1000
```

## 三、数据模型设计

### 3.1 卡片数据模型

```python
# core/card_manager.py

from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
from pathlib import Path
import json

class Card:
    """卡片数据模型"""
    def __init__(
        self,
        card_id: str,
        project_id: str,
        card_type: str,
        data: Dict[str, Any],
        parent_id: Optional[str] = None,
        children_ids: List[str] = None,
        metadata: Dict[str, Any] = None
    ):
        self.id = card_id
        self.project_id = project_id
        self.type = card_type
        self.data = data
        self.parent_id = parent_id
        self.children_ids = children_ids or []
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "type": self.type,
            "data": self.data,
            "parent_id": self.parent_id,
            "children_ids": self.children_ids,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class CardManager:
    """卡片管理器"""
    
    def __init__(self, projects_dir: str = "projects"):
        self.projects_dir = Path(projects_dir)
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.cards: Dict[str, Card] = {}
        self._load_all_cards()
    
    def create_card(
        self,
        project_id: str,
        card_type: str,
        data: Dict[str, Any],
        parent_id: Optional[str] = None
    ) -> Card:
        """创建新卡片"""
        card_id = str(uuid.uuid4())
        card = Card(card_id, project_id, card_type, data, parent_id)
        
        # 如果有父卡片，更新父卡片的children_ids
        if parent_id:
            parent_card = self.cards.get(parent_id)
            if parent_card:
                parent_card.children_ids.append(card_id)
                self._save_card(parent_card)
        
        self.cards[card_id] = card
        self._save_card(card)
        return card
    
    def get_card(self, card_id: str) -> Optional[Card]:
        """获取卡片"""
        return self.cards.get(card_id)
    
    def get_project_cards(self, project_id: str, card_type: Optional[str] = None) -> List[Card]:
        """获取项目的所有卡片"""
        cards = [c for c in self.cards.values() if c.project_id == project_id]
        if card_type:
            cards = [c for c in cards if c.type == card_type]
        return cards
    
    def get_cards_by_volume(self, volume_num: int, card_type: str) -> List[Card]:
        """获取指定卷的卡片"""
        # 根据卷号过滤卡片
        pass
    
    def update_card(self, card_id: str, updates: Dict[str, Any]):
        """更新卡片"""
        card = self.cards.get(card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found")
        
        # 更新数据
        if "data" in updates:
            card.data.update(updates["data"])
        if "metadata" in updates:
            card.metadata.update(updates["metadata"])
        
        card.updated_at = datetime.now().isoformat()
        self._save_card(card)
    
    def _save_card(self, card: Card):
        """保存卡片到文件"""
        project_dir = self.projects_dir / card.project_id / "cards"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        card_file = project_dir / f"{card.id}.json"
        with open(card_file, 'w', encoding='utf-8') as f:
            json.dump(card.to_dict(), f, ensure_ascii=False, indent=2)
```

### 3.2 项目数据模型

```python
# core/project_manager.py

from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml
import uuid

class Project:
    """项目数据模型"""
    def __init__(
        self,
        project_id: str,
        name: str,
        description: str = "",
        config: Dict[str, Any] = None
    ):
        self.id = project_id
        self.name = name
        self.description = description
        self.config = config or {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

class ProjectManager:
    """项目管理器"""
    
    def __init__(self, projects_dir: str = "projects"):
        self.projects_dir = Path(projects_dir)
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.projects: Dict[str, Project] = {}
        self._load_all_projects()
    
    def create_project(self, name: str, description: str = "", template_id: Optional[str] = None) -> Project:
        """创建新项目"""
        project_id = str(uuid.uuid4())
        
        # 如果指定了模板，加载模板配置
        config = {}
        if template_id:
            config = self._load_template(template_id)
        
        project = Project(project_id, name, description, config)
        self.projects[project_id] = project
        self._save_project(project)
        
        # 创建项目目录
        project_dir = self.projects_dir / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "cards").mkdir(exist_ok=True)
        
        return project
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """获取项目"""
        return self.projects.get(project_id)
    
    def list_projects(self) -> List[Project]:
        """列出所有项目"""
        return list(self.projects.values())
```

## 四、API接口设计

### 4.1 新增API端点

```python
# api_server.py (扩展)

# 卡片管理API
@app.post("/api/cards")
async def create_card(project_id: str, card_type: str, data: Dict):
    """创建卡片"""
    pass

@app.get("/api/cards/{card_id}")
async def get_card(card_id: str):
    """获取卡片"""
    pass

@app.put("/api/cards/{card_id}")
async def update_card(card_id: str, updates: Dict):
    """更新卡片"""
    pass

# 项目管理API
@app.post("/api/projects")
async def create_project(name: str, description: str = ""):
    """创建项目"""
    pass

@app.get("/api/projects")
async def list_projects():
    """列出所有项目"""
    pass

# 动态Schema API
@app.post("/api/schemas")
async def create_schema(schema_def: Dict):
    """创建Schema"""
    pass

@app.get("/api/schemas/{schema_id}")
async def get_schema(schema_id: str):
    """获取Schema"""
    pass

# 上下文注入API
@app.post("/api/context/inject")
async def inject_context(prompt: str, context: Dict):
    """注入上下文"""
    pass

# 知识图谱API
@app.post("/api/kg/extract")
async def extract_relationships(text: str, project_id: str):
    """提取关系"""
    pass

@app.get("/api/kg/character/{character_id}")
async def get_character_context(character_id: str, depth: int = 2):
    """获取角色上下文"""
    pass

# 灵感助手API
@app.post("/api/inspiration/chat")
async def chat_with_assistant(message: str, context_card_id: str = None):
    """与灵感助手对话"""
    pass

@app.post("/api/inspiration/apply")
async def apply_to_card(conversation_id: str, card_id: str, message_indices: List[int]):
    """应用对话成果到卡片"""
    pass

# 灵感工作台API
@app.post("/api/workspace/free-cards")
async def create_free_card(card_type: str, content: Dict):
    """创建自由卡片"""
    pass

@app.post("/api/workspace/move-to-project")
async def move_to_project(free_card_id: str, project_id: str):
    """移动到项目"""
    pass

# 雪花工作流API
@app.post("/api/workflows/snowflake/start")
async def start_snowflake_workflow(project_id: str):
    """启动雪花工作流"""
    pass

@app.post("/api/workflows/snowflake/expand")
async def expand_stage(workflow_id: str, stage: str, parent_card_id: str):
    """扩展阶段"""
    pass
```

## 五、前端界面设计

### 5.1 主要界面模块

1. **项目工作区**
   - 项目列表
   - 项目详情
   - 卡片树形视图

2. **卡片编辑器**
   - 卡片内容编辑
   - Schema验证
   - 关联关系管理

3. **Schema编辑器**
   - 可视化Schema设计
   - 字段配置
   - 预览和测试

4. **上下文注入编辑器**
   - 表达式编辑器
   - 实时预览
   - 上下文选择器

5. **知识图谱可视化**
   - 关系图谱
   - 节点详情
   - 关系编辑

6. **灵感助手界面**
   - 对话界面
   - 上下文卡片显示
   - 应用建议

7. **灵感工作台**
   - 自由卡片列表
   - 跨项目引用
   - 移动/复制操作

8. **雪花工作流界面**
   - 工作流进度
   - 阶段扩展
   - 树形结构展示

## 六、实施计划

### 阶段一：基础架构（2-3周）
1. 实现卡片管理系统
2. 实现项目管理系统
3. 实现基础API接口
4. 前端基础框架搭建

### 阶段二：核心功能（3-4周）
1. 实现动态输出模型（Pydantic）
2. 实现自由上下文注入
3. 集成Neo4j知识图谱
4. 实现灵感助手基础功能

### 阶段三：高级功能（2-3周）
1. 完善灵感工作台
2. 实现雪花式创作流程
3. 实现配置管理系统
4. 前端界面完善

### 阶段四：优化和测试（1-2周）
1. 性能优化
2. 功能测试
3. 用户体验优化
4. 文档完善

## 七、依赖更新

需要在 `requirements.txt` 中添加：

```txt
# 动态输出模型
pydantic>=2.0.0

# 知识图谱
neo4j>=5.0.0

# 其他工具
python-dateutil>=2.8.0
```

## 八、注意事项

1. **向后兼容**：确保现有功能不受影响
2. **数据迁移**：现有记忆体数据需要迁移到卡片系统
3. **性能考虑**：知识图谱查询需要优化
4. **安全性**：跨项目引用需要权限控制
5. **可扩展性**：保持模块化设计，便于后续扩展

## 九、总结

本融合方案将 NovelForge 的核心功能完整整合到现有系统中，实现了：

1. ✅ 动态输出模型 - 基于Pydantic的可视化Schema系统
2. ✅ 自由上下文注入 - 表达式语言驱动的上下文系统
3. ✅ 知识图谱驱动 - Neo4j集成的关系管理
4. ✅ 灵感助手 - 对话式创作助手
5. ✅ 灵感工作台 - 自由卡片和跨项目引用
6. ✅ 雪花式创作流程 - 完整的创作工作流
7. ✅ 高度可配置 - 深度自定义配置系统

系统将从"语料提取工具"升级为"智能创作平台"，为创作者提供全方位的创作支持。


