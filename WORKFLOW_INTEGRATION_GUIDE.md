# 创作流程融合指南

本文档详细说明如何将各种经典创作流程融合到 NovelForge 系统中。

## 一、支持的创作流程

### 1.1 雪花创作法（Snowflake Method）

#### 流程阶段
1. **一句话梗概** - 用一句话概括整个故事
2. **一段话扩展** - 将一句话扩展为一段话（约200-300字）
3. **角色表** - 为主要角色创建详细档案
4. **大纲** - 将段落扩展为多段落大纲
5. **世界观** - 构建完整的世界观设定
6. **蓝图** - 创建详细的故事蓝图
7. **分卷** - 将故事划分为多个卷
8. **章节** - 为每卷创建章节大纲
9. **正文** - 撰写具体章节内容

#### 实现方式
```python
# core/workflows/snowflake_workflow.py

class SnowflakeWorkflow(WorkflowBase):
    """雪花创作法工作流"""
    
    STAGES = [
        WorkflowStage("one_sentence", "一句话梗概", 1),
        WorkflowStage("paragraph", "一段话扩展", 2),
        WorkflowStage("character_sheet", "角色表", 3),
        WorkflowStage("synopsis", "大纲", 4),
        WorkflowStage("worldview", "世界观", 5),
        WorkflowStage("blueprint", "蓝图", 6),
        WorkflowStage("volume", "分卷", 7),
        WorkflowStage("chapter", "章节", 8),
        WorkflowStage("content", "正文", 9),
    ]
    
    async def expand_stage(self, stage_name: str, parent_card_id: str):
        """扩展当前阶段"""
        parent_card = self.card_manager.get_card(parent_card_id)
        
        if stage_name == "paragraph":
            return await self._expand_to_paragraph(parent_card)
        elif stage_name == "character_sheet":
            return await self._create_character_sheets(parent_card)
        # ... 其他阶段
```

### 1.2 英雄之旅（Hero's Journey）

#### 12个阶段
1. **平凡世界** - 英雄的日常生活
2. **冒险召唤** - 英雄收到冒险的邀请
3. **拒绝召唤** - 英雄犹豫或拒绝冒险
4. **遇见导师** - 英雄遇到指导者
5. **跨越第一道门槛** - 英雄正式进入冒险世界
6. **考验、伙伴、敌人** - 英雄面临挑战
7. **接近洞穴最深处** - 接近最大挑战
8. **磨难** - 英雄面临最大考验
9. **奖赏** - 英雄获得奖励
10. **回归之路** - 英雄开始返回
11. **复活** - 英雄经历最后的考验
12. **带着仙丹妙药回归** - 英雄带着收获回归

#### 实现方式
```python
# core/workflows/hero_journey_workflow.py

class HeroJourneyWorkflow(WorkflowBase):
    """英雄之旅工作流"""
    
    STAGES = [
        WorkflowStage("ordinary_world", "平凡世界", 1),
        WorkflowStage("call_to_adventure", "冒险召唤", 2),
        WorkflowStage("refusal", "拒绝召唤", 3),
        WorkflowStage("meeting_mentor", "遇见导师", 4),
        WorkflowStage("crossing_threshold", "跨越第一道门槛", 5),
        WorkflowStage("tests_allies_enemies", "考验、伙伴、敌人", 6),
        WorkflowStage("approach", "接近洞穴最深处", 7),
        WorkflowStage("ordeal", "磨难", 8),
        WorkflowStage("reward", "奖赏", 9),
        WorkflowStage("road_back", "回归之路", 10),
        WorkflowStage("resurrection", "复活", 11),
        WorkflowStage("return_with_elixir", "带着仙丹妙药回归", 12),
    ]
    
    async def generate_stage_content(self, stage: WorkflowStage, context: Dict):
        """生成阶段内容"""
        # 使用模板和上下文生成内容
        template = self._load_stage_template(stage.name)
        prompt = self.context_injector.inject_into_prompt(template, context)
        return await self.llm_client.generate(prompt)
```

### 1.3 三幕式结构（Three-Act Structure）

#### 三幕划分
- **第一幕：设定**（25%）- 建立情境，介绍人物和世界观
- **第二幕：冲突**（50%）- 发展情节，推进冲突
- **第三幕：解决**（25%）- 高潮和结局

#### 实现方式
```python
# core/workflows/three_act_workflow.py

class ThreeActWorkflow(WorkflowBase):
    """三幕式结构工作流"""
    
    ACTS = [
        Act("act1", "第一幕：设定", 0.25, [
            "开场钩子",
            "人物介绍",
            "世界观建立",
            "核心冲突引入",
            "激励事件"
        ]),
        Act("act2", "第二幕：冲突", 0.50, [
            "障碍和挑战",
            "角色成长",
            "冲突升级",
            "中点转折",
            "危机加深"
        ]),
        Act("act3", "第三幕：解决", 0.25, [
            "最终对决",
            "高潮爆发",
            "冲突解决",
            "角色弧线完成",
            "结局收束"
        ])
    ]
    
    def calculate_chapter_distribution(self, total_chapters: int) -> Dict[str, int]:
        """计算章节分布"""
        return {
            "act1": int(total_chapters * 0.25),
            "act2": int(total_chapters * 0.50),
            "act3": int(total_chapters * 0.25)
        }
```

### 1.4 救猫咪15节拍（Save the Cat! Beat Sheet）

#### 15个节拍
1. **开场画面** - 第一印象
2. **主题陈述** - 故事主题
3. **铺垫** - 建立角色和世界
4. **推动** - 引发事件
5. **争执** - 角色犹豫
6. **第二幕开始** - 进入新世界
7. **B故事** - 次要情节
8. **游戏时间** - 探索新世界
9. **中点** - 虚假胜利/失败
10. **坏家伙逼近** - 压力增加
11. **一无所有** - 最低点
12. **灵魂黑夜** - 内心挣扎
13. **第三幕开始** - 找到解决方案
14. **大结局** - 最终对决
15. **终场画面** - 对比开场

#### 实现方式
```python
# core/workflows/save_the_cat_workflow.py

class SaveTheCatWorkflow(WorkflowBase):
    """救猫咪15节拍工作流"""
    
    BEATS = [
        Beat("opening_image", "开场画面", 1),
        Beat("theme_stated", "主题陈述", 2),
        Beat("setup", "铺垫", 3),
        Beat("catalyst", "推动", 4),
        Beat("debate", "争执", 5),
        Beat("break_into_two", "第二幕开始", 6),
        Beat("b_story", "B故事", 7),
        Beat("fun_and_games", "游戏时间", 8),
        Beat("midpoint", "中点", 9),
        Beat("bad_guys_close_in", "坏家伙逼近", 10),
        Beat("all_is_lost", "一无所有", 11),
        Beat("dark_night", "灵魂黑夜", 12),
        Beat("break_into_three", "第三幕开始", 13),
        Beat("finale", "大结局", 14),
        Beat("final_image", "终场画面", 15),
    ]
```

### 1.5 起承转合式（Four-Part Structure）

#### 四段划分
- **起** - 开端，建立背景
- **承** - 承接，发展情节
- **转** - 转折，冲突升级
- **合** - 合拢，结局收束

#### 实现方式
```python
# core/workflows/four_part_workflow.py

class FourPartWorkflow(WorkflowBase):
    """起承转合式工作流"""
    
    PARTS = [
        Part("起", "开端", 0.25, "建立背景和人物"),
        Part("承", "承接", 0.25, "发展情节和关系"),
        Part("转", "转折", 0.25, "冲突升级和转折"),
        Part("合", "合拢", 0.25, "结局收束和升华")
    ]
```

### 1.6 草蛇灰线式（Foreshadowing Structure）

#### 特点
- 强调伏笔的布局和回收
- 非线性叙事
- 多线索交织

#### 实现方式
```python
# core/workflows/foreshadowing_workflow.py

class ForeshadowingWorkflow(WorkflowBase):
    """草蛇灰线式工作流"""
    
    def create_foreshadowing_plan(self, story_outline: Dict) -> Dict:
        """创建伏笔计划"""
        # 分析故事大纲，识别需要埋设伏笔的关键点
        key_points = self._identify_key_points(story_outline)
        
        # 为每个关键点创建伏笔卡片
        foreshadowing_cards = []
        for point in key_points:
            card = self._create_foreshadowing_card(point)
            foreshadowing_cards.append(card)
        
        return {
            "foreshadowing_cards": foreshadowing_cards,
            "timeline": self._create_foreshadowing_timeline(foreshadowing_cards)
        }
```

### 1.7 碎片拼贴式（Fragmented Structure）

#### 特点
- 非线性叙事
- 多视角切换
- 时间线交错

#### 实现方式
```python
# core/workflows/fragmented_workflow.py

class FragmentedWorkflow(WorkflowBase):
    """碎片拼贴式工作流"""
    
    def create_fragment_structure(self, story_elements: List[Dict]) -> Dict:
        """创建碎片结构"""
        # 将故事元素打散为碎片
        fragments = self._create_fragments(story_elements)
        
        # 创建时间线和视角映射
        timeline = self._create_timeline(fragments)
        perspectives = self._create_perspectives(fragments)
        
        return {
            "fragments": fragments,
            "timeline": timeline,
            "perspectives": perspectives,
            "assembly_plan": self._create_assembly_plan(fragments)
        }
```

## 二、工作流引擎设计

### 2.1 工作流基类

```python
# core/workflows/base.py

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from enum import Enum

class WorkflowStage:
    """工作流阶段"""
    def __init__(self, name: str, label: str, order: int, config: Dict = None):
        self.name = name
        self.label = label
        self.order = order
        self.config = config or {}
        self.completed = False
        self.card_id: Optional[str] = None

class WorkflowStatus(str, Enum):
    """工作流状态"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class WorkflowBase(ABC):
    """工作流基类"""
    
    def __init__(
        self,
        project_id: str,
        card_manager,
        llm_client,
        context_injector,
        knowledge_graph=None
    ):
        self.project_id = project_id
        self.card_manager = card_manager
        self.llm_client = llm_client
        self.context_injector = context_injector
        self.knowledge_graph = knowledge_graph
        self.stages: List[WorkflowStage] = []
        self.status = WorkflowStatus.NOT_STARTED
        self.current_stage_index = 0
    
    @abstractmethod
    def get_stages(self) -> List[WorkflowStage]:
        """获取工作流阶段列表"""
        pass
    
    @abstractmethod
    async def expand_stage(self, stage: WorkflowStage, parent_card_id: str) -> Dict[str, Any]:
        """扩展阶段"""
        pass
    
    async def start(self) -> Dict[str, Any]:
        """启动工作流"""
        self.status = WorkflowStatus.IN_PROGRESS
        self.stages = self.get_stages()
        
        # 创建根卡片
        root_card = self.card_manager.create_card(
            self.project_id,
            "workflow_root",
            {"workflow_type": self.__class__.__name__}
        )
        
        return {
            "workflow_id": str(uuid.uuid4()),
            "root_card_id": root_card['id'],
            "stages": [s.name for s in self.stages],
            "status": self.status.value
        }
    
    async def next_stage(self) -> Optional[Dict[str, Any]]:
        """进入下一阶段"""
        if self.current_stage_index >= len(self.stages):
            self.status = WorkflowStatus.COMPLETED
            return None
        
        current_stage = self.stages[self.current_stage_index]
        
        # 获取父卡片（通常是上一阶段的卡片）
        parent_card_id = self._get_parent_card_id()
        
        # 扩展当前阶段
        result = await self.expand_stage(current_stage, parent_card_id)
        
        # 更新阶段状态
        current_stage.completed = True
        current_stage.card_id = result.get('card_id')
        self.current_stage_index += 1
        
        return result
    
    def _get_parent_card_id(self) -> Optional[str]:
        """获取父卡片ID"""
        if self.current_stage_index > 0:
            prev_stage = self.stages[self.current_stage_index - 1]
            return prev_stage.card_id
        return None
    
    def get_progress(self) -> Dict[str, Any]:
        """获取工作流进度"""
        completed = sum(1 for s in self.stages if s.completed)
        total = len(self.stages)
        
        return {
            "status": self.status.value,
            "current_stage": self.stages[self.current_stage_index].name if self.current_stage_index < len(self.stages) else None,
            "progress": {
                "completed": completed,
                "total": total,
                "percentage": (completed / total * 100) if total > 0 else 0
            },
            "stages": [
                {
                    "name": s.name,
                    "label": s.label,
                    "completed": s.completed,
                    "order": s.order
                }
                for s in self.stages
            ]
        }
```

### 2.2 工作流工厂

```python
# core/workflows/factory.py

from typing import Dict, Type
from core.workflows.base import WorkflowBase
from core.workflows.snowflake_workflow import SnowflakeWorkflow
from core.workflows.hero_journey_workflow import HeroJourneyWorkflow
from core.workflows.three_act_workflow import ThreeActWorkflow
from core.workflows.save_the_cat_workflow import SaveTheCatWorkflow
from core.workflows.four_part_workflow import FourPartWorkflow
from core.workflows.foreshadowing_workflow import ForeshadowingWorkflow
from core.workflows.fragmented_workflow import FragmentedWorkflow

class WorkflowFactory:
    """工作流工厂"""
    
    WORKFLOW_REGISTRY: Dict[str, Type[WorkflowBase]] = {
        "snowflake": SnowflakeWorkflow,
        "hero_journey": HeroJourneyWorkflow,
        "three_act": ThreeActWorkflow,
        "save_the_cat": SaveTheCatWorkflow,
        "four_part": FourPartWorkflow,
        "foreshadowing": ForeshadowingWorkflow,
        "fragmented": FragmentedWorkflow,
    }
    
    @classmethod
    def create_workflow(
        cls,
        workflow_type: str,
        project_id: str,
        card_manager,
        llm_client,
        context_injector,
        knowledge_graph=None
    ) -> WorkflowBase:
        """创建工作流实例"""
        workflow_class = cls.WORKFLOW_REGISTRY.get(workflow_type)
        if not workflow_class:
            raise ValueError(f"Unknown workflow type: {workflow_type}")
        
        return workflow_class(
            project_id=project_id,
            card_manager=card_manager,
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
                "description": getattr(workflow_class, "__doc__", "")
            }
            for workflow_type, workflow_class in cls.WORKFLOW_REGISTRY.items()
        ]
```

## 三、工作流与卡片系统的集成

### 3.1 卡片类型映射

每个工作流阶段都会创建特定类型的卡片：

```python
# 雪花创作法
"one_sentence" -> Card(type="one_sentence")
"paragraph" -> Card(type="paragraph")
"character_sheet" -> Card(type="character", subtype="main")
"synopsis" -> Card(type="synopsis")
"worldview" -> Card(type="worldview")
"blueprint" -> Card(type="blueprint")
"volume" -> Card(type="volume")
"chapter" -> Card(type="chapter")
"content" -> Card(type="content")

# 英雄之旅
"ordinary_world" -> Card(type="scene", stage="ordinary_world")
"call_to_adventure" -> Card(type="event", stage="call_to_adventure")
# ... 其他阶段
```

### 3.2 工作流树形结构

工作流创建的卡片以树形结构组织：

```
工作流根卡片
├── 阶段1卡片
│   ├── 子卡片1
│   └── 子卡片2
├── 阶段2卡片
│   ├── 子卡片1
│   └── 子卡片2
└── ...
```

## 四、工作流配置

### 4.1 配置文件

```yaml
# config.yaml

workflows:
  enabled_workflows:
    - snowflake
    - hero_journey
    - three_act
    - save_the_cat
  
  default_workflow: "snowflake"
  
  workflow_configs:
    snowflake:
      auto_expand: false  # 是否自动扩展下一阶段
      require_validation: true  # 是否需要验证
      max_iterations: 10  # 最大迭代次数
    
    hero_journey:
      chapter_distribution: "auto"  # 章节分布方式
      character_focus: true  # 是否聚焦角色
    
    three_act:
      act1_percentage: 0.25
      act2_percentage: 0.50
      act3_percentage: 0.25
```

## 五、API接口

### 5.1 工作流API

```python
# api_server.py

@app.post("/api/workflows/start")
async def start_workflow(workflow_type: str, project_id: str):
    """启动工作流"""
    workflow = WorkflowFactory.create_workflow(...)
    result = await workflow.start()
    return result

@app.post("/api/workflows/{workflow_id}/next")
async def next_stage(workflow_id: str):
    """进入下一阶段"""
    workflow = get_workflow(workflow_id)
    result = await workflow.next_stage()
    return result

@app.get("/api/workflows/{workflow_id}/progress")
async def get_progress(workflow_id: str):
    """获取工作流进度"""
    workflow = get_workflow(workflow_id)
    return workflow.get_progress()

@app.get("/api/workflows/list")
async def list_workflows():
    """列出所有可用工作流"""
    return WorkflowFactory.list_workflows()
```

## 六、前端界面

### 6.1 工作流选择界面
- 显示所有可用工作流
- 工作流描述和特点
- 工作流预览

### 6.2 工作流执行界面
- 阶段进度条
- 当前阶段卡片编辑器
- 阶段导航
- 工作流树形视图

### 6.3 工作流配置界面
- 工作流参数配置
- 阶段自定义
- 验证规则设置

## 七、总结

通过工作流系统，用户可以：

1. ✅ 选择适合的创作流程（雪花法、英雄之旅、三幕式等）
2. ✅ 按照结构化流程逐步创作
3. ✅ 自动生成符合流程要求的卡片
4. ✅ 跟踪创作进度
5. ✅ 灵活切换和组合不同工作流
6. ✅ 自定义工作流参数和阶段

工作流系统与卡片系统、知识图谱、上下文注入等功能无缝集成，为创作者提供全方位的结构化创作支持。


