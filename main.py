"""
主程序入口
命令行界面，协调各模块执行小说语料提取
"""

import argparse
import asyncio
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

import yaml
from tqdm import tqdm

from agents.analyst import AnalystAgent
from agents.archivist import ArchivistAgent
from agents.extractor import ExtractorAgent
from agents.planner import PlannerAgent
from agents.reader import ReaderAgent
from agents.scanner import ScannerAgent
from agents.stylist import StylistAgent
from core.api_optimizer import APIOptimizer
from core.creative_workflow import CreativeWorkflowPipeline
from core.enhanced_model_interface import EnhancedLLMClient, create_enhanced_client_from_config
from core.frankentexts import FrankentextsManager
from core.memory_manager import MemoryManager
from core.model_interface import ModelFactory
from core.topology_manager import DynamicTopologyResolver, TopologyManager, TopologyMode

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('novel_extractor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NovelCorpusExtractor:
    """小说语料提取系统主类"""
    
    def __init__(self, config_path: str):
        """初始化系统"""
        # 检查配置文件是否存在
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        # 加载配置
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f) or {}
        
        # 初始化模型客户端（支持单API或多API池模式）
        api_pool_config = self.config.get("api_pool", {})
        available_apis = 0
        if api_pool_config.get("enabled", False):
            # 使用多API池模式
            raw_api_configs = api_pool_config.get("apis", [])
            api_configs: List[Dict[str, Any]] = []
            for cfg in raw_api_configs:
                cfg = cfg.copy()
                if not cfg.get("enabled", True):
                    continue
                if not cfg.get("api_key"):
                    provider = cfg.get("provider", "").upper()
                    env_key = f"{provider}_API_KEY" if provider else ""
                    if env_key:
                        cfg["api_key"] = os.getenv(env_key, "")
                if not cfg.get("api_key"):
                    logger.warning("API配置 %s 缺少密钥，已跳过", cfg.get("name", cfg.get("provider", "unknown")))
                    continue
                api_configs.append(cfg)
            
            self.llm_client = create_enhanced_client_from_config(api_configs)
            self.api_optimizer = APIOptimizer(self.llm_client.api_pool)
            available_apis = DynamicTopologyResolver.detect_available_apis(api_configs)
            logger.info("已启用多API池模式，共 %d 个有效API", available_apis)
        else:
            # 使用单API模式（兼容旧配置）
            model_config = self.config.get("model", {})
            self.llm_client = ModelFactory.create_client(model_config)
            self.api_optimizer = None
            available_apis = DynamicTopologyResolver.detect_available_apis([model_config])
            logger.info("使用单API模式")
        
        # 初始化管理器
        output_dir = self.config.get("output_dir", "output")
        self.memory_manager = MemoryManager(output_dir=output_dir)
        self.frankentexts_manager = FrankentextsManager(
            corpus_dir=self.config.get("corpus_dir", "corpus_samples")
        )
        
        # 初始化Agent
        self.reader = ReaderAgent(
            chunk_size=self.config.get("chunk_size", 1024),
            overlap=self.config.get("chunk_overlap", 100)
        )
        self.analyst = AnalystAgent(self.llm_client)
        self.archivist = ArchivistAgent(self.memory_manager)
        self.scanner = ScannerAgent()
        self.extractor = ExtractorAgent(self.llm_client, self.frankentexts_manager)
        self.planner = PlannerAgent(self.llm_client, self.memory_manager)
        self.stylist = StylistAgent(self.llm_client)
        
        # 初始化类型增强器
        from core.genre_enhancer import GenreEnhancer
        self.genre_enhancer = GenreEnhancer()

        # 初始化创作工作流
        workflow_config = self.config.get("workflow", {})
        self.workflow_pipeline = CreativeWorkflowPipeline(
            memory_manager=self.memory_manager,
            workflow_config=workflow_config
        )
        
        # 初始化拓扑管理器
        topology_config = self.config.get("topology", {})
        topology_mode_str = topology_config.get("mode", "auto")
        try:
            topology_mode = TopologyMode(topology_mode_str)
        except ValueError:
            logger.warning(f"无效的拓扑模式: {topology_mode_str}，使用auto模式")
            topology_mode = TopologyMode.AUTO
        
        # 确保至少有一个API可用
        if available_apis == 0:
            logger.warning("未检测到可用的API密钥，系统可能无法正常工作")
        
        self.topology_manager = TopologyManager(topology_mode, available_apis)
        
        logger.info("系统初始化完成")
    
    async def process_novel(self, input_file: str, novel_type: str = "通用"):
        """处理小说文件"""
        logger.info(f"开始处理小说: {input_file}")
        
        # 解析类型标签（支持多个类型，用逗号分隔）
        type_tags = [t.strip() for t in novel_type.split(",")] if novel_type != "通用" else []
        if type_tags:
            logger.info(f"类型标签: {', '.join(type_tags)}")
        
        # 读取并分块
        logger.info("步骤1: 读取和分块...")
        chunks = list(self.reader.process(input_file))
        logger.info(f"共生成 {len(chunks)} 个文本块")
        
        # 根据拓扑模式执行
        mode = self.topology_manager.mode
        
        if mode == TopologyMode.LINEAR:
            results = await self._process_linear(chunks, novel_type)
        elif mode == TopologyMode.TRIANGULAR:
            results = await self._process_triangular(chunks, novel_type)
        elif mode == TopologyMode.SWARM:
            results = await self._process_swarm(chunks, novel_type)
        else:
            results = await self._process_linear(chunks, novel_type)
        
        # 生成大纲
        logger.info("步骤2: 生成剧情大纲...")
        structure = self.planner.analyze_structure(chunks, novel_type)
        outline = self.planner.generate_outline(structure, novel_type)
        logger.info("大纲生成完成")

        # 执行创作与优化工作流
        logger.info("步骤3: 运行创作工作流...")
        workflow_summary = self.workflow_pipeline.run(
            chunks=chunks,
            novel_type=novel_type,
            agent_results=results,
            outline=outline
        )
        logger.info("创作工作流完成")
        
        logger.info("处理完成！")
        return {
            "chunk_results": results,
            "outline": outline,
            "workflow": workflow_summary
        }
    
    async def _process_linear(self, chunks: List[Dict], novel_type: str) -> List[Dict]:
        """线性串行处理"""
        results = []
        
        def pipeline(chunk):
            # 分析
            analysis_result = self.analyst.analyze_chunk(chunk, novel_type)
            # 归档
            archive_result = self.archivist.archive_extracted_info(
                analysis_result.get("extracted_info", {}),
                chunk.get("chunk_id", "")
            )
            return {**analysis_result, **archive_result}
        
        for chunk in tqdm(chunks, desc="处理中"):
            # 在线性模式下，使用线程池执行以避免阻塞
            result = await asyncio.to_thread(pipeline, chunk)
            results.append(result)
        
        return results
    
    async def _process_triangular(self, chunks: List[Dict], novel_type: str) -> List[Dict]:
        """三角协同处理"""
        async def scanner_func(chunk):
            return await asyncio.to_thread(self.scanner.scan_chunk, chunk)
        
        async def extractor_func(scanned_chunk):
            return await asyncio.to_thread(self.extractor.extract, scanned_chunk, novel_type)
        
        async def memory_keeper_func(extracted):
            # 校验一致性
            chunk_id = extracted.get("chunk_id", "")
            extracted_data = extracted.get("extracted_data", {})
            archive_result = await asyncio.to_thread(
                self.archivist.archive_extracted_info, extracted_data, chunk_id
            )
            return {**extracted, **archive_result}
        
        return await self.topology_manager.execute_triangular(
            scanner_func, extractor_func, memory_keeper_func, chunks
        )
    
    async def _process_swarm(self, chunks: List[Dict], novel_type: str) -> List[Dict]:
        """专家蜂群处理"""
        # 简化实现：先扫描，再并行分析和提取
        scanned_chunks = await asyncio.gather(*[
            asyncio.to_thread(self.scanner.scan_chunk, chunk) for chunk in chunks
        ])
        
        results = []
        for scanned_chunk in tqdm(scanned_chunks, desc="处理中"):
            # 并行执行分析和提取
            analysis_task = asyncio.create_task(
                asyncio.to_thread(self.analyst.analyze_chunk, scanned_chunk, novel_type)
            )
            extract_task = asyncio.create_task(
                asyncio.to_thread(self.extractor.extract, scanned_chunk, novel_type)
            )
            
            analysis_result, extract_result = await asyncio.gather(analysis_task, extract_task)
            
            # 归档
            archive_result = await asyncio.to_thread(
                self.archivist.archive_extracted_info,
                analysis_result.get("extracted_info", {}),
                scanned_chunk.get("chunk_id", "")
            )
            
            results.append({
                **analysis_result,
                **extract_result,
                **archive_result
            })
        
        return results


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="小说语料提取系统")
    parser.add_argument("--config", type=str, default="config.yaml",
                       help="配置文件路径")
    parser.add_argument("--input", type=str, required=True,
                       help="输入小说文件路径")
    parser.add_argument("--output", type=str, default=None,
                       help="输出目录（覆盖配置文件设置）")
    parser.add_argument("--type", type=str, default="通用",
                       help="小说类型（支持36+种类型，如：言情、玄幻、仙侠、重生文、系统文、爽文等）")
    
    args = parser.parse_args()
    
    # 检查配置文件
    if not Path(args.config).exists():
        logger.error(f"配置文件不存在: {args.config}")
        logger.info("请先创建config.yaml配置文件，或使用--config指定配置文件路径")
        return
    
    # 检查输入文件
    if not Path(args.input).exists():
        logger.error(f"输入文件不存在: {args.input}")
        return
    
    # 创建提取器
    try:
        extractor = NovelCorpusExtractor(args.config)
        
        # 如果指定了输出目录，覆盖配置
        if args.output:
            extractor.memory_manager.output_dir = Path(args.output)
            extractor.memory_manager.output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"初始化失败: {e}", exc_info=True)
        return
    
    # 处理小说
    try:
        results = asyncio.run(extractor.process_novel(args.input, args.type))
        chunk_results = results.get("chunk_results", []) if isinstance(results, dict) else results
        logger.info(f"处理完成，共处理 {len(chunk_results)} 个文本块")
        if isinstance(results, dict) and results.get("workflow"):
            flows = ", ".join(results["workflow"].keys())
            logger.info(f"已执行的工作流阶段: {flows}")
        logger.info(f"输出目录: {extractor.memory_manager.output_dir}")
    except KeyboardInterrupt:
        logger.warning("用户中断处理")
    except Exception as e:
        logger.error(f"处理失败: {e}", exc_info=True)


if __name__ == "__main__":
    main()

