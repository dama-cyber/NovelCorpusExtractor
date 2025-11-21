"""
七步方法论工作流
基于 qcbigma 的七步创作方法论
整合创作工具和语料库缝合功能
支持多Agent协同机制（1-5个API）
"""

from enum import Enum
from typing import Dict, List, Optional, Any
import logging
import yaml

from .base import WorkflowBase, WorkflowStage
from ..multi_agent_coordinator import MultiAgentCoordinator, AgentRole

logger = logging.getLogger(__name__)


def _safe_llm_call(llm_client, prompt: str, operation_name: str) -> str:
    """安全的 LLM 调用，包含错误处理"""
    if not llm_client:
        raise ValueError("LLM 客户端未初始化，请检查 API 配置")
    
    try:
        import asyncio
        # 如果是异步客户端，使用异步调用
        if hasattr(llm_client, 'send_prompt_async'):
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # 如果事件循环正在运行，需要特殊处理
                    raise RuntimeError("请在异步上下文中调用")
                return loop.run_until_complete(llm_client.send_prompt_async(prompt))
            except RuntimeError:
                # 如果没有事件循环，创建一个新的
                return asyncio.run(llm_client.send_prompt_async(prompt))
        else:
            return llm_client.send_prompt(prompt)
    except Exception as e:
        logger.error(f"{operation_name} - 调用 LLM API 失败: {e}", exc_info=True)
        raise ValueError(f"{operation_name}失败: {str(e)}。请检查 API 配置和网络连接。")


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
    
    def __init__(
        self,
        project_id: str,
        card_manager=None,
        project_manager=None,
        llm_client=None,
        context_injector=None,
        knowledge_graph=None,
        memory_manager=None,
        frankentexts_manager=None,
        agents=None
    ):
        """初始化工作流"""
        super().__init__(project_id, card_manager, llm_client, context_injector, knowledge_graph)
        self.project_manager = project_manager
        self.memory_manager = memory_manager
        self.frankentexts_manager = frankentexts_manager
        self.agents = agents or {}
        
        # 初始化多Agent协同管理器
        # 检测可用API数量
        available_apis = 1
        if hasattr(llm_client, 'api_pool') and llm_client.api_pool:
            available_apis = len(llm_client.api_pool.apis)
        elif hasattr(llm_client, 'api_names'):
            available_apis = len(llm_client.api_names)
        
        self.agent_coordinator = MultiAgentCoordinator(llm_client, available_apis)
        logger.info(f"多Agent协同管理器已初始化: {self.agent_coordinator.get_strategy_info()['strategy_name']}")
    
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
    
    async def expand_stage(self, stage: WorkflowStage, parent_card_id: Optional[str] = None) -> Dict[str, Any]:
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
        else:
            raise ValueError(f"未知阶段: {stage.name}")
    
    async def _create_constitution(self, parent_card_id: Optional[str] = None) -> Dict[str, Any]:
        """创建创作原则（整合世界观冲突检测和角色一致性检查）"""
        context = self._get_project_context()
        
        # 如果已有世界观记忆体，可以用于验证
        worldview_context = ""
        if hasattr(self, 'memory_manager') and self.memory_manager:
            try:
                worldview_file = self.memory_manager.output_dir / "02_世界观记忆体.yaml"
                if worldview_file.exists():
                    with open(worldview_file, 'r', encoding='utf-8') as f:
                        worldview_content = f.read()
                        worldview_context = f"\n\n现有世界观记忆体（用于参考）：\n{worldview_content[:1000]}"
            except Exception as e:
                logger.warning(f"读取世界观记忆体失败: {e}")
        
        prompt = f"""请为这个小说项目建立创作原则（Constitution）。

创作原则是不可妥协的写作原则、风格指南和核心价值观，将指导整个创作过程。

项目上下文：
{context}
{worldview_context}

请生成以下内容：
1. 核心创作原则（3-5 条）
2. 风格指南（语言风格、叙事视角等）
3. 核心价值观（故事要传达的主题和价值观）
4. 不可妥协的规则（必须遵守的规则）
5. 世界观一致性规则（确保世界观设定不冲突）
6. 角色一致性规则（确保角色行为符合设定）

以结构化的格式输出。"""
        
        if not self.llm_client:
            raise ValueError("LLM 客户端未初始化，请检查 API 配置")
        
        try:
            result = await self.llm_client.send_prompt_async(prompt)
        except Exception as e:
            logger.error(f"调用 LLM API 失败: {e}", exc_info=True)
            raise ValueError(f"API 调用失败: {str(e)}。请检查 API 配置和网络连接。")
        
        # 创建卡片
        if not self.card_manager:
            raise ValueError("卡片管理器未初始化")
        
        try:
            card = self.card_manager.create_card(
                self.project_id,
                "constitution",
                {
                    "content": result,
                    "stage": "constitution"
                },
                parent_id=parent_card_id
            )
        except Exception as e:
            logger.error(f"创建卡片失败: {e}", exc_info=True)
            raise ValueError(f"保存创作原则失败: {str(e)}")
        
        return {
            "card_id": card['id'] if isinstance(card, dict) else card.id,
            "content": result,
            "stage": "constitution"
        }
    
    async def _create_specification(self, parent_card_id: Optional[str] = None) -> Dict[str, Any]:
        """创建故事需求规范（整合商业化优化和平台适配），并创建世界观和人物记忆体"""
        # 获取创作原则
        constitution_content = ""
        if parent_card_id:
            constitution_card = self.card_manager.get_card(parent_card_id)
            if constitution_card:
                constitution_content = constitution_card.get('data', {}).get('content', '')
        
        prompt = f"""基于以下创作原则，定义详细的故事需求规范（Specification）。

创作原则：
{constitution_content}

请生成类似产品需求文档（PRD）的故事规范，包括：
1. 故事概述（一句话梗概）
2. 目标受众（包括目标平台，如番茄小说、起点中文网等）
3. 故事类型和风格
4. 核心冲突和主题
5. 主要角色（简要描述，包括姓名、性格、背景、能力等）
6. 世界观设定（包括世界背景、力量体系、规则设定等）
7. 故事结构（三幕式/英雄之旅等）
8. 成功标准（如何判断故事成功）
9. 商业化考虑（标题吸引力、开篇钩子、付费点规划）
10. 平台适配要求（根据目标平台调整内容策略）

以结构化的格式输出。"""
        
        if not self.llm_client:
            raise ValueError("LLM 客户端未初始化，请检查 API 配置")
        
        try:
            result = await self.llm_client.send_prompt_async(prompt)
        except Exception as e:
            logger.error(f"调用 LLM API 失败: {e}", exc_info=True)
            raise ValueError(f"API 调用失败: {str(e)}。请检查 API 配置和网络连接。")
        
        # 从规范中提取世界观和人物信息，创建记忆体
        memory_files_created = []
        if hasattr(self, 'memory_manager') and self.memory_manager:
            try:
                # 提取世界观信息
                worldview_prompt = f"""从以下故事规范中提取世界观设定信息，以YAML格式输出：

故事规范：
{result}

请提取以下世界观信息：
1. 世界背景（时代、地点、环境等）
2. 力量体系（如果有，包括等级划分、修炼方式等）
3. 规则设定（世界运行的规则、限制等）
4. 重要地点（主要场景、城市、国家等）
5. 组织势力（门派、国家、组织等）
6. 历史背景（重要历史事件等）

如果规范中没有明确的世界观设定，请根据故事类型和主题推断并创建基础世界观。

以YAML格式输出，结构清晰。"""
                
                worldview_result = await self.llm_client.send_prompt_async(worldview_prompt)
                # 尝试解析YAML
                try:
                    worldview_data = yaml.safe_load(worldview_result) or {}
                    if isinstance(worldview_data, dict):
                        self.memory_manager.save_worldview(worldview_data)
                        memory_files_created.append("02_世界观记忆体.yaml")
                        logger.info("世界观记忆体已创建")
                except Exception as e:
                    logger.warning(f"解析世界观YAML失败，保存为文本: {e}")
                    # 如果解析失败，保存为结构化文本
                    self.memory_manager.save_worldview({"世界观设定": worldview_result})
                    memory_files_created.append("02_世界观记忆体.yaml")
                
                # 提取人物信息
                character_prompt = f"""从以下故事规范中提取主要角色信息，以YAML格式输出：

故事规范：
{result}

请提取所有主要角色的详细信息，每个角色包括：
1. 姓名
2. 性格特点（MBTI类型、性格描述等）
3. 背景故事
4. 能力/技能
5. 外貌描述
6. 角色定位（主角/配角/反派等）
7. 角色关系（与其他角色的关系）
8. 成长目标（角色的成长弧线）

以YAML格式输出，每个角色作为一个条目。"""
                
                character_result = await self.llm_client.send_prompt_async(character_prompt)
                # 尝试解析YAML
                try:
                    character_data = yaml.safe_load(character_result) or {}
                    if isinstance(character_data, dict):
                        self.memory_manager.save_characters(character_data)
                        memory_files_created.append("03_人物记忆体.yaml")
                        logger.info("人物记忆体已创建")
                except Exception as e:
                    logger.warning(f"解析人物YAML失败，保存为文本: {e}")
                    # 如果解析失败，保存为结构化文本
                    self.memory_manager.save_characters({"主要角色": character_result})
                    memory_files_created.append("03_人物记忆体.yaml")
                    
            except Exception as e:
                logger.warning(f"创建记忆体失败: {e}，继续执行")
        
        card = self.card_manager.create_card(
            self.project_id,
            "specification",
            {
                "content": result,
                "stage": "specify",
                "memory_files_created": memory_files_created
            },
            parent_id=parent_card_id
        )
        
        return {
            "card_id": card['id'],
            "content": result,
            "stage": "specify",
            "memory_files_created": memory_files_created
        }
    
    async def _create_clarifications(self, parent_card_id: Optional[str] = None) -> Dict[str, Any]:
        """创建关键澄清问题"""
        # 获取规范
        specification_content = ""
        if parent_card_id:
            spec_card = self.card_manager.get_card(parent_card_id)
            if spec_card:
                specification_content = spec_card.get('data', {}).get('content', '')
        
        prompt = f"""分析以下故事规范，识别可能存在的歧义和模糊之处。

故事规范：
{specification_content}

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
        
        if not self.llm_client:
            raise ValueError("LLM 客户端未初始化，请检查 API 配置")
        
        try:
            result = await self.llm_client.send_prompt_async(prompt)
        except Exception as e:
            logger.error(f"调用 LLM API 失败: {e}", exc_info=True)
            raise ValueError(f"API 调用失败: {str(e)}。请检查 API 配置和网络连接。")
        questions = self._extract_questions(result)
        
        card = self.card_manager.create_card(
            self.project_id,
            "clarifications",
            {
                "content": result,
                "questions": questions,
                "stage": "clarify"
            },
            parent_id=parent_card_id
        )
        
        return {
            "card_id": card['id'],
            "content": result,
            "questions": questions,
            "stage": "clarify"
        }
    
    async def _create_plan(self, parent_card_id: Optional[str] = None) -> Dict[str, Any]:
        """创建创作计划（整合情绪曲线优化和伏笔提醒），并创建剧情大纲和伏笔追踪表"""
        # 获取前面的所有阶段内容
        context = self._get_all_previous_stages(parent_card_id)
        
        # 获取世界观和人物记忆体作为参考
        memory_context = ""
        if hasattr(self, 'memory_manager') and self.memory_manager:
            try:
                worldview = self.memory_manager.load_worldview()
                characters = self.memory_manager.load_characters()
                if worldview:
                    memory_context += f"\n\n世界观记忆体：\n{str(worldview)[:1000]}\n"
                if characters:
                    memory_context += f"\n\n人物记忆体：\n{str(characters)[:1000]}\n"
                
                # 获取伏笔追踪表（如果存在）
                foreshadowing_file = self.memory_manager.output_dir / "05_伏笔追踪表.yaml"
                if foreshadowing_file.exists():
                    with open(foreshadowing_file, 'r', encoding='utf-8') as f:
                        foreshadowing_content = f.read()
                        memory_context += f"\n\n现有伏笔追踪表（用于参考）：\n{foreshadowing_content[:1000]}"
            except Exception as e:
                logger.warning(f"读取记忆体失败: {e}")
        
        prompt = f"""基于以下信息，创建详细的创作计划（Plan）。

项目上下文：
{context}
{memory_context}

请将抽象的需求转化为具体的技术方案，包括：
1. 章节结构（章节数量和大致内容，每章的核心事件）
2. 角色弧线（主要角色的成长轨迹，在哪些章节发生关键转变）
3. 世界观构建（如果需要补充世界观细节）
4. 情节时间线（主要事件的时间顺序，关键情节点）
5. 伏笔布局（关键伏笔的埋设章节和回收章节）
6. 情绪曲线规划（各章节的情绪节奏，高潮和低谷的分布）
7. Hook 点规划（每章的钩子和转折点）
8. 写作策略（如何实现创作原则和规范）
9. 语料库使用策略（哪些场景可以使用语料库片段进行缝合）

以结构化的格式输出。"""
        
        if not self.llm_client:
            raise ValueError("LLM 客户端未初始化，请检查 API 配置")
        
        try:
            result = await self.llm_client.send_prompt_async(prompt)
        except Exception as e:
            logger.error(f"调用 LLM API 失败: {e}", exc_info=True)
            raise ValueError(f"API 调用失败: {str(e)}。请检查 API 配置和网络连接。")
        
        # 从计划中提取剧情大纲和伏笔信息，创建记忆体
        memory_files_created = []
        if hasattr(self, 'memory_manager') and self.memory_manager:
            try:
                # 提取剧情大纲
                plot_prompt = f"""从以下创作计划中提取详细的剧情大纲，以YAML格式输出：

创作计划：
{result}

请提取以下剧情信息：
1. 总体结构（卷/幕的划分）
2. 每章的核心事件（章节编号、标题、核心事件、关键情节点）
3. 主要冲突和高潮（冲突类型、高潮位置）
4. 人物成长弧线（每个主要角色在哪些章节发生关键转变）
5. 时间线（主要事件的时间顺序）
6. 关键情节点（转折点、高潮点、低谷点）

以YAML格式输出，结构清晰，便于后续写作参考。"""
                
                plot_result = await self.llm_client.send_prompt_async(plot_prompt)
                # 尝试解析YAML
                try:
                    plot_data = yaml.safe_load(plot_result) or {}
                    if isinstance(plot_data, dict):
                        self.memory_manager.save_plot(plot_data)
                        memory_files_created.append("04_剧情规划大纲.yaml")
                        logger.info("剧情规划大纲已创建")
                except Exception as e:
                    logger.warning(f"解析剧情大纲YAML失败，保存为文本: {e}")
                    # 如果解析失败，保存为结构化文本
                    self.memory_manager.save_plot({"剧情大纲": plot_result})
                    memory_files_created.append("04_剧情规划大纲.yaml")
                
                # 提取伏笔信息
                foreshadowing_prompt = f"""从以下创作计划中提取所有伏笔信息，以YAML列表格式输出：

创作计划：
{result}

请提取所有伏笔，每个伏笔包括：
1. 伏笔内容（伏笔的描述）
2. 埋设章节（在哪个章节埋设）
3. 回收章节（计划在哪个章节回收）
4. 伏笔类型（线索型/暗示型/悬念型等）
5. 关联角色（与哪些角色相关）
6. 重要性（关键/次要）

以YAML列表格式输出，每个伏笔作为一个列表项。"""
                
                foreshadowing_result = await self.llm_client.send_prompt_async(foreshadowing_prompt)
                # 尝试解析YAML
                try:
                    foreshadowing_data = yaml.safe_load(foreshadowing_result) or []
                    if isinstance(foreshadowing_data, list):
                        # 为每个伏笔添加ID和状态
                        for i, f in enumerate(foreshadowing_data):
                            if isinstance(f, dict):
                                f['id'] = f"{i+1:03d}"
                                f['status'] = "未回收"
                        self.memory_manager.save_foreshadowing(foreshadowing_data)
                        memory_files_created.append("05_伏笔追踪表.yaml")
                        logger.info(f"伏笔追踪表已创建，共 {len(foreshadowing_data)} 个伏笔")
                except Exception as e:
                    logger.warning(f"解析伏笔YAML失败，保存为文本: {e}")
                    # 如果解析失败，尝试手动提取
                    foreshadowing_list = [{"伏笔内容": foreshadowing_result, "id": "001", "status": "未回收"}]
                    self.memory_manager.save_foreshadowing(foreshadowing_list)
                    memory_files_created.append("05_伏笔追踪表.yaml")
                    
            except Exception as e:
                logger.warning(f"创建记忆体失败: {e}，继续执行")
        
        card = self.card_manager.create_card(
            self.project_id,
            "plan",
            {
                "content": result,
                "stage": "plan",
                "memory_files_created": memory_files_created
            },
            parent_id=parent_card_id
        )
        
        return {
            "card_id": card['id'],
            "content": result,
            "stage": "plan",
            "memory_files_created": memory_files_created
        }
    
    async def _create_tasks(self, parent_card_id: Optional[str] = None) -> Dict[str, Any]:
        """创建任务分解（整合章节标题生成）"""
        # 获取计划
        plan_content = ""
        if parent_card_id:
            plan_card = self.card_manager.get_card(parent_card_id)
            if plan_card:
                plan_content = plan_card.get('data', {}).get('content', '')
        
        prompt = f"""将以下创作计划分解为可执行的写作任务（Tasks）。

创作计划：
{plan_content}

请创建任务列表，每个任务应该：
1. 有明确的描述（包括章节标题建议）
2. 有优先级（高/中/低）
3. 有依赖关系（如果有）
4. 有估算的工作量
5. 有验收标准
6. 有建议的语料库片段类型（如果需要使用语料库缝合）

任务应该按照执行顺序排列，并考虑依赖关系。
对于每个章节任务，建议生成2-3个候选标题。
以 JSON 格式输出任务列表。"""
        
        if not self.llm_client:
            raise ValueError("LLM 客户端未初始化，请检查 API 配置")
        
        try:
            result = await self.llm_client.send_prompt_async(prompt)
        except Exception as e:
            logger.error(f"调用 LLM API 失败: {e}", exc_info=True)
            raise ValueError(f"API 调用失败: {str(e)}。请检查 API 配置和网络连接。")
        tasks = self._extract_tasks(result)
        
        card = self.card_manager.create_card(
            self.project_id,
            "tasks",
            {
                "content": result,
                "tasks": tasks,
                "stage": "tasks"
            },
            parent_id=parent_card_id
        )
        
        return {
            "card_id": card['id'],
            "content": result,
            "tasks": tasks,
            "stage": "tasks"
        }
    
    async def _execute_writing(self, parent_card_id: Optional[str] = None) -> Dict[str, Any]:
        """执行写作（整合语料库缝合功能和多Agent协同）"""
        # 获取任务列表和所有上下文
        context = self._get_all_previous_stages(parent_card_id)
        tasks = []
        
        if parent_card_id:
            tasks_card = self.card_manager.get_card(parent_card_id)
            if tasks_card:
                tasks = tasks_card.get('data', {}).get('tasks', [])
        
        # 选择下一个要执行的任务
        next_task = self._get_next_task(tasks)
        
        if not next_task:
            return {
                "message": "所有任务已完成",
                "stage": "write",
                "completed": True
            }
        
        # 获取项目信息以确定小说类型
        novel_type = self._get_novel_type_from_context(context)
        
        # 使用多Agent协同执行写作
        # 根据可用API数量，使用不同的Agent组合
        available_apis = self.agent_coordinator.available_apis
        
        if available_apis >= 2:
            # 多Agent协同模式
            return await self._execute_writing_with_agents(context, next_task, parent_card_id, novel_type, tasks)
        else:
            # 单API串行模式（原有逻辑）
            return await self._execute_writing_single(context, next_task, parent_card_id, novel_type, tasks)
    
    async def _execute_writing_with_agents(
        self, 
        context: str, 
        next_task: Dict, 
        parent_card_id: Optional[str],
        novel_type: str,
        tasks: List[Dict]
    ) -> Dict[str, Any]:
        """使用多Agent协同执行写作"""
        try:
            import sys
            from pathlib import Path
            # 添加项目根目录到路径
            project_root = Path(__file__).parent.parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            
            from agents.reader import ReaderAgent
            from agents.analyst import AnalystAgent
            from agents.extractor import ExtractorAgent
            from agents.planner import PlannerAgent
            from agents.stylist import StylistAgent
            from agents.critic import CriticAgent
        except ImportError as e:
            logger.warning(f"导入Agent失败: {e}，将使用单API模式")
            return await self._execute_writing_single(context, next_task, parent_card_id, novel_type, tasks)
        
        # 创建Agent函数映射
        agent_functions = {}
        
        # 1. Reader: 分析任务上下文
        async def reader_task(ctx):
            reader_llm = self.agent_coordinator.create_agent_llm_client(AgentRole.READER)
            reader = ReaderAgent()
            task_text = f"{next_task.get('description', '')}\n\n上下文:\n{context[:2000]}"
            # ReaderAgent通常不需要LLM，但这里我们用它来分析
            return {"reader_analysis": task_text}
        
        # 2. Analyst: 分析任务需求
        async def analyst_task(ctx):
            analyst_llm = self.agent_coordinator.create_agent_llm_client(AgentRole.ANALYST)
            analyst = AnalystAgent(analyst_llm)
            task_chunk = {"text": next_task.get('description', ''), "metadata": next_task}
            analysis = analyst.analyze_chunk(task_chunk, novel_type)
            return {"task_analysis": analysis}
        
        # 3. Extractor: 从语料库检索相关片段
        async def extractor_task(ctx):
            if not self.frankentexts_manager:
                return {"corpus_fragments": []}
            extractor_llm = self.agent_coordinator.create_agent_llm_client(AgentRole.EXTRACTOR)
            extractor = ExtractorAgent(extractor_llm, self.frankentexts_manager)
            task_description = next_task.get('description', '')
            try:
                fragments = self.frankentexts_manager.search_fragments(
                    query=task_description,
                    genre=novel_type,
                    top_k=3
                )
                return {"corpus_fragments": fragments}
            except Exception as e:
                logger.warning(f"语料库检索失败: {e}")
                return {"corpus_fragments": []}
        
        # 4. Planner: 规划写作结构
        async def planner_task(ctx):
            planner_llm = self.agent_coordinator.create_agent_llm_client(AgentRole.PLANNER)
            planner = PlannerAgent(planner_llm, self.memory_manager) if self.memory_manager else None
            if planner:
                # 简化的规划
                return {"writing_plan": "按照任务要求进行写作"}
            return {"writing_plan": None}
        
        # 5. Writer: 执行写作
        async def writer_task(ctx):
            writer_llm = self.agent_coordinator.create_agent_llm_client(AgentRole.WRITER)
            
            # 收集前面Agent的结果
            reader_result = ctx.get('reader_analysis', {})
            analyst_result = ctx.get('task_analysis', {})
            extractor_result = ctx.get('corpus_fragments', [])
            planner_result = ctx.get('writing_plan', {})
            
            # 构建语料库上下文
            corpus_context = ""
            if extractor_result:
                corpus_context = "\n\n## 参考语料库片段（可用于缝合）\n"
                for i, frag in enumerate(extractor_result[:3], 1):
                    template = frag.get('template') or frag.get('text', '')
                    corpus_context += f"\n片段 {i}（类型: {frag.get('type', '未知')}）:\n{template[:500]}...\n"
                corpus_context += "\n注意：可以参考这些片段的写作风格和结构，但需要根据当前任务进行适配和改写。\n"
            
            prompt = f"""基于以下上下文，执行写作任务。

项目上下文：
{context}

当前任务：
{next_task}

任务分析：
{analyst_result.get('extracted_info', {})}

写作计划：
{planner_result}
{corpus_context}

请按照创作原则和规范，完成这个写作任务。
输出应该：
1. 符合创作原则
2. 符合故事规范
3. 符合创作计划
4. 达到任务的验收标准
5. 如果提供了语料库片段，可以参考其风格和结构，但需要根据当前任务进行适配

如果使用了语料库片段，请确保：
- 替换专有名词为当前故事中的角色和地点
- 保持情节逻辑连贯
- 风格与整体作品一致"""
            
            result = await writer_llm.send_prompt_async(prompt)
            return {"content": result}
        
        # 6. Stylist: 优化文本风格（如果可用）
        async def stylist_task(ctx):
            if self.agent_coordinator.available_apis >= 3:
                stylist_llm = self.agent_coordinator.create_agent_llm_client(AgentRole.STYLIST)
                stylist = StylistAgent(stylist_llm)
                content = ctx.get('content', '')
                if content:
                    try:
                        optimized = stylist.optimize_style(content, context[:1000])
                        return {"optimized_content": optimized}
                    except Exception as e:
                        logger.warning(f"风格优化失败: {e}")
            return {"optimized_content": None}
        
        # 7. Critic: 质量审查（如果可用）
        async def critic_task(ctx):
            if self.agent_coordinator.available_apis >= 4:
                critic_llm = self.agent_coordinator.create_agent_llm_client(AgentRole.CRITIC)
                critic = CriticAgent(critic_llm)
                content = ctx.get('optimized_content') or ctx.get('content', '')
                if content:
                    try:
                        review_context = {
                            "constitution": context,
                            "specification": context,
                            "plan": context
                        }
                        review = await critic.review_content(content, review_context)
                        return {"review": review}
                    except Exception as e:
                        logger.warning(f"质量审查失败: {e}")
            return {"review": None}
        
        # 根据可用API数量选择执行的Agent
        agent_functions = {}
        if self.agent_coordinator.available_apis >= 1:
            agent_functions[AgentRole.READER] = reader_task
        if self.agent_coordinator.available_apis >= 1:
            agent_functions[AgentRole.ANALYST] = analyst_task
        if self.agent_coordinator.available_apis >= 2:
            agent_functions[AgentRole.EXTRACTOR] = extractor_task
        if self.agent_coordinator.available_apis >= 3:
            agent_functions[AgentRole.PLANNER] = planner_task
        if self.agent_coordinator.available_apis >= 1:
            agent_functions[AgentRole.WRITER] = writer_task
        if self.agent_coordinator.available_apis >= 3:
            agent_functions[AgentRole.STYLIST] = stylist_task
        if self.agent_coordinator.available_apis >= 4:
            agent_functions[AgentRole.CRITIC] = critic_task
        
        # 执行Agent协同（按优先级顺序执行，但同优先级可以并行）
        # 需要按顺序执行，因为后面的Agent依赖前面的结果
        results = {}
        shared_context = {
            "context": context,
            "next_task": next_task,
            "novel_type": novel_type
        }
        
        # 第一轮：Reader, Analyst, Extractor (可以并行)
        round1_agents = {}
        if AgentRole.READER in agent_functions:
            round1_agents[AgentRole.READER] = agent_functions[AgentRole.READER]
        if AgentRole.ANALYST in agent_functions:
            round1_agents[AgentRole.ANALYST] = agent_functions[AgentRole.ANALYST]
        if AgentRole.EXTRACTOR in agent_functions:
            round1_agents[AgentRole.EXTRACTOR] = agent_functions[AgentRole.EXTRACTOR]
        
        if round1_agents:
            round1_results = await self.agent_coordinator.execute_agents_parallel(round1_agents, shared_context)
            results.update(round1_results)
            shared_context.update(round1_results)
        
        # 第二轮：Planner (依赖第一轮结果)
        if AgentRole.PLANNER in agent_functions:
            planner_result = await agent_functions[AgentRole.PLANNER](shared_context)
            results[AgentRole.PLANNER] = planner_result
            shared_context.update(planner_result)
        
        # 第三轮：Writer (依赖前面所有结果)
        if AgentRole.WRITER in agent_functions:
            writer_result = await agent_functions[AgentRole.WRITER](shared_context)
            results[AgentRole.WRITER] = writer_result
            shared_context.update(writer_result)
        
        # 第四轮：Stylist (依赖Writer结果)
        if AgentRole.STYLIST in agent_functions:
            stylist_result = await agent_functions[AgentRole.STYLIST](shared_context)
            results[AgentRole.STYLIST] = stylist_result
            shared_context.update(stylist_result)
        
        # 第五轮：Critic (依赖Stylist或Writer结果)
        if AgentRole.CRITIC in agent_functions:
            critic_result = await agent_functions[AgentRole.CRITIC](shared_context)
            results[AgentRole.CRITIC] = critic_result
        
        # 提取最终内容
        final_content = (
            results.get(AgentRole.STYLIST, {}).get('optimized_content') or
            results.get(AgentRole.WRITER, {}).get('content') or
            ""
        )
        
        # 如果Critic有建议，应用建议
        if results.get(AgentRole.CRITIC, {}).get('review'):
            review = results[AgentRole.CRITIC]['review']
            if review.get('issues'):
                logger.info(f"Critic发现 {len(review['issues'])} 个问题")
        
        # 获取语料库片段
        corpus_fragments = results.get(AgentRole.EXTRACTOR, {}).get('corpus_fragments', [])
        used_fragments = [f.get('id') for f in corpus_fragments if f.get('id')]
        
        # 创建内容卡片
        card = self.card_manager.create_card(
            self.project_id,
            "content",
            {
                "content": final_content,
                "task_id": next_task.get('id'),
                "task_description": next_task.get('description'),
                "stage": "write",
                "used_corpus_fragments": used_fragments,
                "corpus_fragment_count": len(corpus_fragments),
                "agent_results": {
                    role.value: result for role, result in results.items()
                }
            },
            parent_id=parent_card_id
        )
        
        # 更新任务状态
        self._mark_task_completed(tasks, next_task.get('id'))
        
        return {
            "card_id": card['id'],
            "content": final_content,
            "task": next_task,
            "stage": "write",
            "has_more_tasks": len([t for t in tasks if not t.get('completed')]) > 0,
            "used_corpus_fragments": used_fragments,
            "corpus_fragment_count": len(corpus_fragments),
            "agent_coordination": self.agent_coordinator.get_strategy_info()
        }
    
    async def _execute_writing_single(
        self, 
        context: str, 
        next_task: Dict, 
        parent_card_id: Optional[str],
        novel_type: str,
        tasks: List[Dict]
    ) -> Dict[str, Any]:
        """单API串行模式执行写作（原有逻辑）"""
        # 尝试从语料库中检索相关片段用于缝合
        corpus_fragments = []
        if hasattr(self, 'frankentexts_manager') and self.frankentexts_manager:
            try:
                task_description = next_task.get('description', '')
                corpus_fragments = self.frankentexts_manager.search_fragments(
                    query=task_description,
                    genre=novel_type,
                    top_k=3
                )
                logger.info(f"从语料库检索到 {len(corpus_fragments)} 个相关片段")
            except Exception as e:
                logger.warning(f"语料库检索失败: {e}，将使用纯生成模式")
        
        # 构建提示词，包含语料库片段作为参考
        corpus_context = ""
        if corpus_fragments:
            corpus_context = "\n\n## 参考语料库片段（可用于缝合）\n"
            for i, frag in enumerate(corpus_fragments, 1):
                template = frag.get('template') or frag.get('text', '')
                corpus_context += f"\n片段 {i}（类型: {frag.get('type', '未知')}）:\n{template[:500]}...\n"
            corpus_context += "\n注意：可以参考这些片段的写作风格和结构，但需要根据当前任务进行适配和改写。\n"
        
        prompt = f"""基于以下上下文，执行写作任务。

项目上下文：
{context}

当前任务：
{next_task}
{corpus_context}

请按照创作原则和规范，完成这个写作任务。
输出应该：
1. 符合创作原则
2. 符合故事规范
3. 符合创作计划
4. 达到任务的验收标准
5. 如果提供了语料库片段，可以参考其风格和结构，但需要根据当前任务进行适配

如果使用了语料库片段，请确保：
- 替换专有名词为当前故事中的角色和地点
- 保持情节逻辑连贯
- 风格与整体作品一致"""
        
        if not self.llm_client:
            raise ValueError("LLM 客户端未初始化，请检查 API 配置")
        
        try:
            result = await self.llm_client.send_prompt_async(prompt)
        except Exception as e:
            logger.error(f"调用 LLM API 失败: {e}", exc_info=True)
            raise ValueError(f"API 调用失败: {str(e)}。请检查 API 配置和网络连接。")
        
        # 如果使用了语料库片段，记录使用情况
        used_fragments = []
        if corpus_fragments:
            used_fragments = [f.get('id') for f in corpus_fragments]
        
        # 创建内容卡片
        card = self.card_manager.create_card(
            self.project_id,
            "content",
            {
                "content": result,
                "task_id": next_task.get('id'),
                "task_description": next_task.get('description'),
                "stage": "write",
                "used_corpus_fragments": used_fragments,
                "corpus_fragment_count": len(corpus_fragments)
            },
            parent_id=parent_card_id
        )
        
        # 更新任务状态
        self._mark_task_completed(tasks, next_task.get('id'))
        
        return {
            "card_id": card['id'],
            "content": result,
            "task": next_task,
            "stage": "write",
            "has_more_tasks": len([t for t in tasks if not t.get('completed')]) > 0,
            "used_corpus_fragments": used_fragments,
            "corpus_fragment_count": len(corpus_fragments)
        }
    
    def _get_novel_type_from_context(self, context: str) -> str:
        """从上下文中提取小说类型"""
        # 尝试从规范中提取类型
        if "类型" in context or "genre" in context.lower():
            import re
            # 简单提取，实际可以更复杂
            type_match = re.search(r'(?:类型|genre)[:：]\s*([^\n]+)', context, re.IGNORECASE)
            if type_match:
                return type_match.group(1).strip()
        return "通用"
    
    async def _analyze_quality(self, parent_card_id: Optional[str] = None) -> Dict[str, Any]:
        """全面验证质量（整合所有检测工具和多Agent协同）"""
        # 获取所有已写内容
        all_content = self._get_all_written_content(parent_card_id)
        context = self._get_all_previous_stages(parent_card_id)
        
        # 使用创作工具进行质量检测
        quality_checks = {}
        
        # 角色一致性检查
        if hasattr(self, 'character_checker') and self.character_checker:
            try:
                character_issues = self.character_checker.check_all_characters()
                quality_checks['character_consistency'] = character_issues
            except Exception as e:
                logger.warning(f"角色一致性检查失败: {e}")
        
        # 世界观冲突检测
        if hasattr(self, 'worldview_detector') and self.worldview_detector:
            try:
                worldview_conflicts = self.worldview_detector.generate_conflict_report()
                quality_checks['worldview_conflicts'] = worldview_conflicts
            except Exception as e:
                logger.warning(f"世界观冲突检测失败: {e}")
        
        # AI 检测
        if hasattr(self, 'ai_evader') and self.ai_evader:
            try:
                ai_likelihood = self.ai_evader.analyze_ai_likelihood(all_content[:3000])
                quality_checks['ai_detection'] = ai_likelihood
            except Exception as e:
                logger.warning(f"AI 检测失败: {e}")
        
        # 伏笔检查
        if hasattr(self, 'foreshadowing_reminder') and self.foreshadowing_reminder:
            try:
                # 估算当前章节数
                content_chapters = all_content.count('第') + all_content.count('章')
                foreshadow_report = self.foreshadowing_reminder.get_reminder_report(content_chapters)
                quality_checks['foreshadowing'] = foreshadow_report
            except Exception as e:
                logger.warning(f"伏笔检查失败: {e}")
        
        quality_checks_str = "\n".join([
            f"### {key}\n{str(value)[:500]}\n"
            for key, value in quality_checks.items()
        ])
        
        # 如果有多API，使用Critic Agent进行多角度审查
        if self.agent_coordinator.available_apis >= 2:
            return await self._analyze_quality_with_agents(
                all_content, context, quality_checks_str, parent_card_id
            )
        else:
            # 单API模式
            return await self._analyze_quality_single(
                all_content, context, quality_checks_str, parent_card_id
            )
    
    async def _analyze_quality_with_agents(
        self,
        all_content: str,
        context: str,
        quality_checks_str: str,
        parent_card_id: Optional[str]
    ) -> Dict[str, Any]:
        """使用多Agent协同进行质量分析"""
        try:
            import sys
            from pathlib import Path
            # 添加项目根目录到路径
            project_root = Path(__file__).parent.parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            
            from agents.critic import CriticAgent
            from agents.analyst import AnalystAgent
        except ImportError as e:
            logger.warning(f"导入Agent失败: {e}，将使用单API模式")
            return await self._analyze_quality_single(all_content, context, quality_checks_str, parent_card_id)
        
        # 创建Agent函数
        agent_functions = {}
        
        # Critic: 全面质量审查
        async def critic_task(ctx):
            critic_llm = self.agent_coordinator.create_agent_llm_client(AgentRole.CRITIC)
            critic = CriticAgent(critic_llm)
            review_context = {
                "constitution": context,
                "specification": context,
                "plan": context
            }
            review = await critic.review_content(
                all_content[:5000],
                review_context,
                ["情节一致性", "角色行为", "风格统一", "逻辑合理性", "可读性"]
            )
            return {"critic_review": review}
        
        # Analyst: 深度分析（如果可用）
        async def analyst_task(ctx):
            if self.agent_coordinator.available_apis >= 3:
                analyst_llm = self.agent_coordinator.create_agent_llm_client(AgentRole.ANALYST)
                analyst = AnalystAgent(analyst_llm)
                # 分析内容结构
                chunk = {"text": all_content[:3000], "chunk_id": "quality_analysis"}
                analysis = analyst.analyze_chunk(chunk)
                return {"deep_analysis": analysis}
            return {"deep_analysis": None}
        
        agent_functions[AgentRole.CRITIC] = critic_task
        if self.agent_coordinator.available_apis >= 3:
            agent_functions[AgentRole.ANALYST] = analyst_task
        
        # 执行Agent协同
        shared_context = {
            "all_content": all_content,
            "context": context,
            "quality_checks": quality_checks_str
        }
        
        results = await self.agent_coordinator.execute_agents_parallel(agent_functions, shared_context)
        
        # 整合结果
        critic_review = results.get(AgentRole.CRITIC, {}).get('critic_review', {})
        deep_analysis = results.get(AgentRole.ANALYST, {}).get('deep_analysis', {})
        
        # 构建最终分析报告
        analysis_parts = []
        if critic_review:
            analysis_parts.append(f"## 质量审查报告\n{critic_review.get('summary', '')}")
            if critic_review.get('issues'):
                analysis_parts.append("\n### 发现的问题\n")
                for issue in critic_review['issues']:
                    analysis_parts.append(f"- {issue.get('description', '')}")
            if critic_review.get('suggestions'):
                analysis_parts.append("\n### 改进建议\n")
                for suggestion in critic_review['suggestions']:
                    analysis_parts.append(f"- {suggestion.get('text', '')}")
        
        if deep_analysis:
            analysis_parts.append(f"\n## 深度分析\n{str(deep_analysis)[:1000]}")
        
        analysis_parts.append(f"\n## 工具检测结果\n{quality_checks_str}")
        
        final_result = "\n\n".join(analysis_parts)
        issues = critic_review.get('issues', []) if critic_review else []
        
        card = self.card_manager.create_card(
            self.project_id,
            "analysis",
            {
                "content": final_result,
                "issues": issues,
                "quality_checks": quality_checks_str,
                "critic_review": critic_review,
                "deep_analysis": deep_analysis,
                "stage": "analyze",
                "agent_coordination": self.agent_coordinator.get_strategy_info()
            },
            parent_id=parent_card_id
        )
        
        return {
            "card_id": card['id'],
            "content": final_result,
            "issues": issues,
            "quality_checks": quality_checks_str,
            "critic_review": critic_review,
            "deep_analysis": deep_analysis,
            "stage": "analyze"
        }
    
    async def _analyze_quality_single(
        self,
        all_content: str,
        context: str,
        quality_checks_str: str,
        parent_card_id: Optional[str]
    ) -> Dict[str, Any]:
        """单API模式质量分析"""
        prompt = f"""对以下创作内容进行全面质量验证（Analysis）。

项目上下文：
{context}

已写内容：
{all_content[:5000]}

创作工具检测结果：
{quality_checks_str}

请验证以下方面：
1. **情节一致性**：检查情节逻辑是否一致，是否有矛盾
2. **时间线准确性**：验证事件的时间顺序是否正确
3. **角色发展**：检查角色行为是否符合设定，角色弧线是否完整（参考角色一致性检查结果）
4. **创作原则遵循**：验证是否遵循了创作原则
5. **规范符合度**：检查是否符合故事规范
6. **伏笔处理**：检查伏笔是否合理埋设和回收（参考伏笔检查结果）
7. **风格一致性**：验证写作风格是否一致
8. **世界观一致性**：检查世界观设定是否冲突（参考世界观冲突检测结果）
9. **AI 检测风险**：评估文本的 AI 检测风险（参考 AI 检测结果）

对于发现的问题，请提供：
- 问题描述
- 问题位置（章节/段落）
- 严重程度（高/中/低）
- 修复建议"""
        
        if not self.llm_client:
            raise ValueError("LLM 客户端未初始化，请检查 API 配置")
        
        try:
            result = await self.llm_client.send_prompt_async(prompt)
        except Exception as e:
            logger.error(f"调用 LLM API 失败: {e}", exc_info=True)
            raise ValueError(f"API 调用失败: {str(e)}。请检查 API 配置和网络连接。")
        issues = self._extract_issues(result)
        
        card = self.card_manager.create_card(
            self.project_id,
            "analysis",
            {
                "content": result,
                "issues": issues,
                "quality_checks": quality_checks_str,
                "stage": "analyze"
            },
            parent_id=parent_card_id
        )
        
        return {
            "card_id": card['id'],
            "content": result,
            "issues": issues,
            "quality_checks": quality_checks_str,
            "stage": "analyze"
        }
    
    def _get_project_context(self) -> str:
        """获取项目上下文"""
        # 获取项目信息
        if hasattr(self, 'project_manager') and self.project_manager:
            project = self.project_manager.get_project(self.project_id)
            if project:
                return f"项目名称: {project.get('name', '')}\n项目描述: {project.get('description', '')}"
        return f"项目ID: {self.project_id}"
    
    def _get_all_previous_stages(self, current_card_id: Optional[str] = None) -> str:
        """获取所有前面阶段的内容"""
        if not current_card_id:
            return ""
        
        # 获取当前卡片的所有祖先卡片
        context_parts = []
        card = self.card_manager.get_card(current_card_id)
        
        while card:
            stage = card.get('data', {}).get('stage', '')
            content = card.get('data', {}).get('content', '')
            if content:
                context_parts.append(f"## {stage}\n{content}")
            
            parent_id = card.get('parent_id')
            if not parent_id:
                break
            card = self.card_manager.get_card(parent_id)
        
        return "\n\n".join(reversed(context_parts))
    
    def _extract_questions(self, text: str) -> List[Dict]:
        """从文本中提取问题"""
        questions = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('问题') or line.startswith('Q') or '?' in line:
                questions.append({
                    "question": line,
                    "answered": False
                })
        
        return questions[:5]  # 最多5个问题
    
    def _extract_tasks(self, text: str) -> List[Dict]:
        """从文本中提取任务"""
        import json
        import re
        
        # 尝试解析 JSON
        try:
            # 查找 JSON 部分
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                tasks_data = json.loads(json_match.group())
                if isinstance(tasks_data, list):
                    return tasks_data
                elif isinstance(tasks_data, dict) and 'tasks' in tasks_data:
                    return tasks_data['tasks']
        except:
            pass
        
        # 如果 JSON 解析失败，尝试从文本中提取
        tasks = []
        lines = text.split('\n')
        current_task = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测任务开始
            if re.match(r'^\d+[\.\)]', line) or '任务' in line:
                if current_task:
                    tasks.append(current_task)
                current_task = {
                    "id": str(len(tasks) + 1),
                    "description": line,
                    "priority": "中",
                    "completed": False
                }
            elif current_task:
                if '优先级' in line or 'priority' in line.lower():
                    if '高' in line:
                        current_task["priority"] = "高"
                    elif '低' in line:
                        current_task["priority"] = "低"
                else:
                    current_task["description"] += "\n" + line
        
        if current_task:
            tasks.append(current_task)
        
        return tasks
    
    def _get_next_task(self, tasks: List[Dict]) -> Optional[Dict]:
        """获取下一个要执行的任务"""
        for task in tasks:
            if not task.get('completed', False):
                return task
        return None
    
    def _mark_task_completed(self, tasks: List[Dict], task_id: str):
        """标记任务为已完成"""
        for task in tasks:
            if task.get('id') == task_id:
                task['completed'] = True
                break
    
    def _get_all_written_content(self, parent_card_id: Optional[str] = None) -> str:
        """获取所有已写内容"""
        # 获取所有类型为 content 的卡片
        content_cards = self.card_manager.get_project_cards(
            self.project_id,
            card_type="content"
        )
        
        contents = []
        for card in content_cards:
            content = card.get('data', {}).get('content', '')
            task_desc = card.get('data', {}).get('task_description', '')
            if content:
                contents.append(f"## {task_desc}\n{content}")
        
        return "\n\n".join(contents)
    
    def _extract_issues(self, text: str) -> List[Dict]:
        """从分析文本中提取问题"""
        issues = []
        lines = text.split('\n')
        current_issue = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测问题开始
            if '问题' in line or 'Issue' in line or '严重程度' in line:
                if current_issue:
                    issues.append(current_issue)
                current_issue = {
                    "description": line,
                    "severity": "中",
                    "location": "",
                    "suggestion": ""
                }
            elif current_issue:
                if '严重程度' in line or 'Severity' in line.lower():
                    if '高' in line or 'High' in line:
                        current_issue["severity"] = "高"
                    elif '低' in line or 'Low' in line:
                        current_issue["severity"] = "低"
                elif '位置' in line or 'Location' in line.lower():
                    current_issue["location"] = line
                elif '建议' in line or 'Suggestion' in line.lower():
                    current_issue["suggestion"] = line
                else:
                    current_issue["description"] += "\n" + line
        
        if current_issue:
            issues.append(current_issue)
        
        return issues

