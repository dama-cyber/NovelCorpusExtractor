"""
整合工作流：拆书提炼语料 + 七步创作方法论
将拆书作为第一步，然后使用七步方法论进行创作
"""

from enum import Enum
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path

from .base import WorkflowBase, WorkflowStage
from .seven_step_workflow import SevenStepWorkflow, SevenStepStage

logger = logging.getLogger(__name__)


class IntegratedStage(str, Enum):
    """整合工作流阶段"""
    DISASSEMBLE = "disassemble"  # 拆书提炼语料
    CONSTITUTION = "constitution"  # 建立创作原则
    SPECIFY = "specify"            # 定义故事需求
    CLARIFY = "clarify"            # 关键澄清
    PLAN = "plan"                  # 创作计划
    TASKS = "tasks"                # 任务分解
    WRITE = "write"                # 执行写作（多个Agent协同）
    ANALYZE = "analyze"            # 全面验证


class IntegratedWorkflow(WorkflowBase):
    """
    整合工作流：拆书提炼语料 + 七步创作方法论
    
    流程：
    1. 拆书提炼语料（使用多个Agent提取语料和记忆体）
    2. 七步创作方法论（基于qcbigma方法论）
    """
    
    def __init__(self, project_id: str, card_manager, project_manager, llm_client, 
                 memory_manager=None, frankentexts_manager=None, agents=None):
        """
        初始化整合工作流
        
        Args:
            project_id: 项目ID
            card_manager: 卡片管理器
            project_manager: 项目管理器
            llm_client: LLM客户端
            memory_manager: 记忆体管理器
            frankentexts_manager: 语料库管理器
            agents: Agent字典，包含 reader, analyst, extractor, archivist, planner, stylist
        """
        super().__init__(project_id, card_manager, project_manager, llm_client)
        self.memory_manager = memory_manager
        self.frankentexts_manager = frankentexts_manager
        self.agents = agents or {}
        
        # 初始化七步工作流（用于后续阶段）
        self.seven_step_workflow = SevenStepWorkflow(
            project_id=project_id,
            card_manager=card_manager,
            project_manager=project_manager,
            llm_client=llm_client
        )
        # 传递记忆体和语料库管理器
        if memory_manager:
            self.seven_step_workflow.memory_manager = memory_manager
        if frankentexts_manager:
            self.seven_step_workflow.frankentexts_manager = frankentexts_manager
        if agents:
            self.seven_step_workflow.agents = agents
    
    def get_stages(self) -> List[WorkflowStage]:
        """获取整合工作流阶段"""
        return [
            WorkflowStage(
                name=IntegratedStage.DISASSEMBLE.value,
                label="拆书提炼语料",
                order=0,
                config={
                    "description": "从优秀小说中提取语料库片段和记忆体，为创作提供素材",
                    "output_type": "corpus_and_memory",
                    "required": True,
                    "agents": ["reader", "scanner", "analyst", "extractor", "archivist", "planner"]
                }
            ),
            WorkflowStage(
                name=IntegratedStage.CONSTITUTION.value,
                label="建立创作原则",
                order=1,
                config={
                    "description": "定义不可妥协的写作原则、风格指南和核心价值观",
                    "output_type": "constitution",
                    "required": True
                }
            ),
            WorkflowStage(
                name=IntegratedStage.SPECIFY.value,
                label="定义故事需求",
                order=2,
                config={
                    "description": "定义要创建的故事、目标受众和成功标准",
                    "output_type": "specification",
                    "required": True
                }
            ),
            WorkflowStage(
                name=IntegratedStage.CLARIFY.value,
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
                name=IntegratedStage.PLAN.value,
                label="创作计划",
                order=4,
                config={
                    "description": "将抽象需求转化为具体技术方案",
                    "output_type": "plan",
                    "required": True
                }
            ),
            WorkflowStage(
                name=IntegratedStage.TASKS.value,
                label="任务分解",
                order=5,
                config={
                    "description": "将计划分解为可执行的写作任务",
                    "output_type": "tasks",
                    "required": True
                }
            ),
            WorkflowStage(
                name=IntegratedStage.WRITE.value,
                label="执行写作",
                order=6,
                config={
                    "description": "基于任务列表进行实际写作，多个Agent协同工作",
                    "output_type": "content",
                    "iterative": True,
                    "required": True,
                    "agents": ["reader", "analyst", "extractor", "planner", "stylist"]
                }
            ),
            WorkflowStage(
                name=IntegratedStage.ANALYZE.value,
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
        if stage.name == IntegratedStage.DISASSEMBLE.value:
            return await self._disassemble_book(parent_card_id)
        elif stage.name == IntegratedStage.CONSTITUTION.value:
            return await self.seven_step_workflow._create_constitution(parent_card_id)
        elif stage.name == IntegratedStage.SPECIFY.value:
            return await self.seven_step_workflow._create_specification(parent_card_id)
        elif stage.name == IntegratedStage.CLARIFY.value:
            return await self.seven_step_workflow._create_clarifications(parent_card_id)
        elif stage.name == IntegratedStage.PLAN.value:
            return await self.seven_step_workflow._create_plan(parent_card_id)
        elif stage.name == IntegratedStage.TASKS.value:
            return await self.seven_step_workflow._create_tasks(parent_card_id)
        elif stage.name == IntegratedStage.WRITE.value:
            return await self._execute_writing_with_agents(parent_card_id)
        elif stage.name == IntegratedStage.ANALYZE.value:
            return await self.seven_step_workflow._analyze_quality(parent_card_id)
        else:
            raise ValueError(f"未知阶段: {stage.name}")
    
    async def _disassemble_book(self, parent_card_id: Optional[str] = None) -> Dict[str, Any]:
        """
        拆书提炼语料
        
        使用多个Agent协同工作：
        - Reader: 读取和分块
        - Scanner: 语义预检
        - Analyst: 深度分析
        - Extractor: 提取高价值片段
        - Archivist: 归档记忆体
        - Planner: 生成大纲
        """
        # 获取项目信息
        project = self.project_manager.get_project(self.project_id)
        if not project:
            raise ValueError(f"项目 {self.project_id} 不存在")
        
        # 获取输入文件路径
        input_file = project.get('config', {}).get('input_file')
        if not input_file:
            raise ValueError("未指定输入文件，无法进行拆书")
        
        input_path = Path(input_file)
        if not input_path.exists():
            raise ValueError(f"输入文件不存在: {input_file}")
        
        results = {
            "chunks_processed": 0,
            "fragments_extracted": 0,
            "memory_files_created": [],
            "corpus_files_updated": []
        }
        
        try:
            # 1. Reader: 读取和分块
            reader = self.agents.get('reader')
            if not reader:
                raise ValueError("Reader Agent 未初始化")
            
            logger.info(f"开始读取文件: {input_file}")
            chunks = reader.read_file(str(input_path))
            results["chunks_processed"] = len(chunks)
            logger.info(f"文件分块完成，共 {len(chunks)} 个块")
            
            # 2. Scanner: 语义预检（可选）
            scanner = self.agents.get('scanner')
            if scanner:
                logger.info("执行语义预检...")
                filtered_chunks = []
                for chunk in chunks:
                    if scanner.should_process(chunk):
                        filtered_chunks.append(chunk)
                chunks = filtered_chunks
                logger.info(f"预检完成，保留 {len(chunks)} 个有效块")
            
            # 3. Analyst: 深度分析
            analyst = self.agents.get('analyst')
            if not analyst:
                raise ValueError("Analyst Agent 未初始化")
            
            logger.info("开始深度分析...")
            analyzed_chunks = []
            for i, chunk in enumerate(chunks):
                try:
                    analysis = analyst.analyze(chunk)
                    analyzed_chunks.append({
                        "chunk": chunk,
                        "analysis": analysis
                    })
                    if (i + 1) % 10 == 0:
                        logger.info(f"已分析 {i + 1}/{len(chunks)} 个块")
                except Exception as e:
                    logger.warning(f"分析块 {i} 失败: {e}")
                    continue
            
            # 4. Extractor: 提取高价值片段
            extractor = self.agents.get('extractor')
            if extractor and self.frankentexts_manager:
                logger.info("开始提取高价值片段...")
                novel_type = project.get('config', {}).get('novel_type', '通用')
                
                for i, item in enumerate(analyzed_chunks):
                    try:
                        chunk_data = item['chunk']
                        extraction = extractor.extract(chunk_data, novel_type=novel_type)
                        
                        if extraction.get('extracted_data', {}).get('is_valuable', False):
                            results["fragments_extracted"] += 1
                        
                        if (i + 1) % 10 == 0:
                            logger.info(f"已提取 {i + 1}/{len(analyzed_chunks)} 个块")
                    except Exception as e:
                        logger.warning(f"提取块 {i} 失败: {e}")
                        continue
            
            # 5. Archivist: 归档记忆体
            archivist = self.agents.get('archivist')
            if archivist and self.memory_manager:
                logger.info("开始归档记忆体...")
                for item in analyzed_chunks:
                    try:
                        archivist.archive(item['analysis'])
                    except Exception as e:
                        logger.warning(f"归档失败: {e}")
                        continue
                
                # 检查生成的记忆体文件
                if self.memory_manager.output_dir.exists():
                    memory_files = list(self.memory_manager.output_dir.glob("*.yaml"))
                    results["memory_files_created"] = [f.name for f in memory_files]
                    logger.info(f"记忆体文件: {results['memory_files_created']}")
            
            # 6. Planner: 生成大纲
            planner = self.agents.get('planner')
            if planner and self.memory_manager:
                logger.info("生成剧情大纲...")
                try:
                    # 收集所有分析结果
                    all_analyses = [item['analysis'] for item in analyzed_chunks]
                    planner.generate_outline(all_analyses)
                    logger.info("剧情大纲生成完成")
                except Exception as e:
                    logger.warning(f"生成大纲失败: {e}")
            
            # 检查语料库文件
            if self.frankentexts_manager:
                corpus_dir = self.frankentexts_manager.corpus_dir
                if corpus_dir.exists():
                    corpus_files = list(corpus_dir.glob("*.txt"))
                    results["corpus_files_updated"] = [f.name for f in corpus_files]
            
            # 创建卡片记录拆书结果
            card = self.card_manager.create_card(
                self.project_id,
                "disassemble",
                {
                    "input_file": str(input_file),
                    "results": results,
                    "stage": "disassemble"
                },
                parent_id=parent_card_id
            )
            
            return {
                "card_id": card['id'],
                "results": results,
                "stage": "disassemble",
                "message": f"拆书完成：处理 {results['chunks_processed']} 个块，提取 {results['fragments_extracted']} 个高价值片段"
            }
            
        except Exception as e:
            logger.error(f"拆书过程失败: {e}", exc_info=True)
            raise ValueError(f"拆书失败: {str(e)}")
    
    async def _execute_writing_with_agents(self, parent_card_id: Optional[str] = None) -> Dict[str, Any]:
        """
        执行写作（多个Agent协同工作）
        
        使用以下Agent：
        - Reader: 分析任务上下文
        - Analyst: 分析任务需求
        - Extractor: 从语料库检索相关片段
        - Planner: 规划写作结构
        - Stylist: 优化文本风格
        """
        # 获取任务列表和所有上下文
        context = self.seven_step_workflow._get_all_previous_stages(parent_card_id)
        tasks = []
        
        if parent_card_id:
            tasks_card = self.card_manager.get_card(parent_card_id)
            if tasks_card:
                tasks = tasks_card.get('data', {}).get('tasks', [])
        
        # 选择下一个要执行的任务
        next_task = self.seven_step_workflow._get_next_task(tasks)
        
        if not next_task:
            return {
                "message": "所有任务已完成",
                "stage": "write",
                "completed": True
            }
        
        # 获取项目信息以确定小说类型
        novel_type = self.seven_step_workflow._get_novel_type_from_context(context)
        
        # 1. Analyst: 分析任务需求
        analyst = self.agents.get('analyst')
        task_analysis = None
        if analyst:
            try:
                task_text = f"{next_task.get('description', '')}"
                task_chunk = {"text": task_text, "metadata": next_task}
                task_analysis = analyst.analyze(task_chunk)
                logger.info("任务分析完成")
            except Exception as e:
                logger.warning(f"任务分析失败: {e}")
        
        # 2. Extractor: 从语料库检索相关片段
        corpus_fragments = []
        extractor = self.agents.get('extractor')
        if extractor and self.frankentexts_manager:
            try:
                task_description = next_task.get('description', '')
                corpus_fragments = self.frankentexts_manager.search_fragments(
                    query=task_description,
                    genre=novel_type,
                    top_k=3
                )
                logger.info(f"从语料库检索到 {len(corpus_fragments)} 个相关片段")
            except Exception as e:
                logger.warning(f"语料库检索失败: {e}")
        
        # 3. Planner: 规划写作结构（如果有）
        planner = self.agents.get('planner')
        structure_suggestion = None
        if planner and self.memory_manager:
            try:
                # 读取剧情大纲作为参考
                outline_file = self.memory_manager.output_dir / "04_剧情规划大纲.yaml"
                if outline_file.exists():
                    with open(outline_file, 'r', encoding='utf-8') as f:
                        outline_content = f.read()
                        structure_suggestion = f"\n参考剧情大纲：\n{outline_content[:500]}"
            except Exception as e:
                logger.warning(f"读取大纲失败: {e}")
        
        # 4. 构建提示词，包含所有Agent的分析结果
        corpus_context = ""
        if corpus_fragments:
            corpus_context = "\n\n## 参考语料库片段（可用于缝合）\n"
            for i, frag in enumerate(corpus_fragments, 1):
                template = frag.get('template') or frag.get('text', '')
                corpus_context += f"\n片段 {i}（类型: {frag.get('type', '未知')}）:\n{template[:500]}...\n"
            corpus_context += "\n注意：可以参考这些片段的写作风格和结构，但需要根据当前任务进行适配和改写。\n"
        
        analysis_context = ""
        if task_analysis:
            analysis_context = f"\n\n## 任务分析结果\n{str(task_analysis)[:500]}\n"
        
        # 读取记忆体作为上下文
        memory_context = ""
        if self.memory_manager:
            try:
                # 世界观记忆体
                worldview_file = self.memory_manager.output_dir / "02_世界观记忆体.yaml"
                if worldview_file.exists():
                    with open(worldview_file, 'r', encoding='utf-8') as f:
                        worldview_content = f.read()
                        memory_context += f"\n\n## 世界观记忆体\n{worldview_content[:1000]}\n"
                
                # 人物记忆体
                character_file = self.memory_manager.output_dir / "03_人物记忆体.yaml"
                if character_file.exists():
                    with open(character_file, 'r', encoding='utf-8') as f:
                        character_content = f.read()
                        memory_context += f"\n\n## 人物记忆体\n{character_content[:1000]}\n"
                
                # 伏笔追踪表
                foreshadowing_file = self.memory_manager.output_dir / "05_伏笔追踪表.yaml"
                if foreshadowing_file.exists():
                    with open(foreshadowing_file, 'r', encoding='utf-8') as f:
                        foreshadowing_content = f.read()
                        memory_context += f"\n\n## 伏笔追踪表\n{foreshadowing_content[:500]}\n"
            except Exception as e:
                logger.warning(f"读取记忆体失败: {e}")
        
        prompt = f"""基于以下上下文，执行写作任务。

项目上下文：
{context}
{memory_context}
{analysis_context}
{structure_suggestion}

当前任务：
{next_task}
{corpus_context}

请按照创作原则和规范，完成这个写作任务。
输出应该：
1. 符合创作原则
2. 符合故事规范
3. 符合创作计划
4. 达到任务的验收标准
5. 参考世界观和人物记忆体，保持设定一致
6. 如果提供了语料库片段，可以参考其风格和结构，但需要根据当前任务进行适配

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
        
        # 5. Stylist: 优化文本风格（可选）
        stylist = self.agents.get('stylist')
        if stylist:
            try:
                # 读取风格记忆体
                style_file = self.memory_manager.output_dir / "01_风格记忆体.yaml" if self.memory_manager else None
                style_guide = None
                if style_file and style_file.exists():
                    with open(style_file, 'r', encoding='utf-8') as f:
                        style_guide = f.read()
                
                # 使用Stylist优化文本
                optimized_result = stylist.enhance_style(result, style_guide=style_guide)
                if optimized_result:
                    result = optimized_result
                    logger.info("文本风格优化完成")
            except Exception as e:
                logger.warning(f"风格优化失败: {e}，使用原始文本")
        
        # 记录使用的语料库片段
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
                "corpus_fragment_count": len(corpus_fragments),
                "agents_used": ["analyst", "extractor", "planner", "stylist"]
            },
            parent_id=parent_card_id
        )
        
        # 更新任务状态
        self.seven_step_workflow._mark_task_completed(tasks, next_task.get('id'))
        
        return {
            "card_id": card['id'],
            "content": result,
            "task": next_task,
            "stage": "write",
            "has_more_tasks": len([t for t in tasks if not t.get('completed')]) > 0,
            "used_corpus_fragments": used_fragments,
            "corpus_fragment_count": len(corpus_fragments),
            "agents_used": ["analyst", "extractor", "planner", "stylist"]
        }
    
    def _get_project_context(self) -> str:
        """获取项目上下文"""
        project = self.project_manager.get_project(self.project_id)
        if not project:
            return ""
        
        context_parts = []
        if project.get('name'):
            context_parts.append(f"项目名称: {project['name']}")
        if project.get('description'):
            context_parts.append(f"项目描述: {project['description']}")
        if project.get('config'):
            config = project['config']
            if config.get('novel_type'):
                context_parts.append(f"小说类型: {config['novel_type']}")
        
        return "\n".join(context_parts)


