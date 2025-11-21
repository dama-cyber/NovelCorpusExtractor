"""
命令行界面工具
提供完整的CLI功能，包括单文件处理、批量处理、配置管理等
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

from main import NovelCorpusExtractor
from core.batch_processor import BatchProcessor, create_batch_processor
from core.data_exporter import DataExporter, create_exporter
from core.utils import ensure_dir

logger = logging.getLogger(__name__)


class CLIFormatter:
    """CLI输出格式化器"""
    
    @staticmethod
    def success(message: str):
        """成功消息"""
        print(f"✅ {message}")
    
    @staticmethod
    def error(message: str):
        """错误消息"""
        print(f"❌ {message}", file=sys.stderr)
    
    @staticmethod
    def info(message: str):
        """信息消息"""
        print(f"ℹ️  {message}")
    
    @staticmethod
    def warning(message: str):
        """警告消息"""
        print(f"⚠️  {message}")
    
    @staticmethod
    def progress(message: str):
        """进度消息"""
        print(f"🔄 {message}")


def setup_logging_for_cli(verbose: bool = False):
    """为CLI设置日志"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )


async def process_single_file(
    extractor: NovelCorpusExtractor,
    input_file: str,
    novel_type: str = "通用",
    output_dir: Optional[str] = None,
    export: Optional[str] = None,
    export_dir: Optional[str] = None
):
    """处理单个文件"""
    CLIFormatter.progress(f"开始处理文件: {input_file}")
    
    try:
        if output_dir:
            extractor.memory_manager.output_dir = Path(output_dir)
            extractor.memory_manager.output_dir.mkdir(parents=True, exist_ok=True)
        
        results = await extractor.process_novel(input_file, novel_type)
        
        chunk_results = results.get("chunk_results", []) if isinstance(results, dict) else results
        CLIFormatter.success(f"处理完成！共处理 {len(chunk_results)} 个文本块")
        
        if isinstance(results, dict) and results.get("workflow"):
            flows = ", ".join(results["workflow"].keys())
            CLIFormatter.info(f"已执行的工作流阶段: {flows}")
        
        CLIFormatter.info(f"输出目录: {extractor.memory_manager.output_dir}")
        
        # 导出数据
        if export:
            await export_data(
                extractor,
                results,
                export_format=export,
                export_dir=export_dir or str(extractor.memory_manager.output_dir / "exports")
            )
        
        return results
        
    except KeyboardInterrupt:
        CLIFormatter.warning("用户中断处理")
        raise
    except Exception as e:
        CLIFormatter.error(f"处理失败: {e}")
        raise


async def process_batch(
    extractor: NovelCorpusExtractor,
    file_paths: List[str],
    novel_type: str = "通用",
    max_concurrent: int = 3,
    output_dir: Optional[str] = None
):
    """批量处理文件"""
    CLIFormatter.progress(f"创建批量任务，共 {len(file_paths)} 个文件")
    
    try:
        batch_processor = create_batch_processor(
            extractor,
            max_concurrent=max_concurrent,
            output_dir=Path(output_dir) if output_dir else None
        )
        
        batch_result = batch_processor.create_batch(
            file_paths=file_paths,
            novel_type=novel_type
        )
        
        CLIFormatter.info(f"批量任务ID: {batch_result.batch_id}")
        CLIFormatter.progress("开始批量处理...")
        
        def progress_callback(batch):
            """进度回调"""
            from core.batch_processor import BatchResult
            progress = batch.progress_percentage
            CLIFormatter.progress(
                f"进度: {progress:.1f}% "
                f"({batch.completed_jobs}/{batch.total_jobs} 完成, "
                f"{batch.failed_jobs} 失败)"
            )
        
        final_result = await batch_processor.process_batch(
            batch_result.batch_id,
            progress_callback=progress_callback
        )
        
        CLIFormatter.success(
            f"批量处理完成！成功: {final_result.completed_jobs}, "
            f"失败: {final_result.failed_jobs}"
        )
        CLIFormatter.info(f"成功率: {final_result.success_rate:.1f}%")
        
        if output_dir:
            summary_file = Path(output_dir) / f"{final_result.batch_id}_summary.json"
            CLIFormatter.info(f"批量结果摘要: {summary_file}")
        
        return final_result
        
    except Exception as e:
        CLIFormatter.error(f"批量处理失败: {e}")
        raise


def list_batch_status(batch_id: Optional[str] = None):
    """列出批量任务状态"""
    # 注意：这需要从存储中读取，简化实现
    CLIFormatter.info("批量任务状态查询功能需要API服务器支持")
    CLIFormatter.info("请使用API端点 /api/batch 查询任务状态")


def show_config_info(config_path: str):
    """显示配置信息"""
    import yaml
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
        
        CLIFormatter.info("配置信息:")
        print(f"  配置文件: {config_path}")
        
        # 显示模型配置
        model_config = config.get("model", {})
        api_pool_config = config.get("api_pool", {})
        
        if api_pool_config.get("enabled", False):
            apis = api_pool_config.get("apis", [])
            enabled_apis = [api for api in apis if api.get("enabled", True)]
            print(f"  API池模式: 启用 ({len(enabled_apis)} 个API)")
            for api in enabled_apis:
                provider = api.get("provider", "unknown")
                name = api.get("name", provider)
                print(f"    - {name} ({provider})")
        else:
            provider = model_config.get("model", "unknown")
            print(f"  模型: {provider}")
        
        # 显示其他配置
        output_dir = config.get("output_dir", "output")
        print(f"  输出目录: {output_dir}")
        
        chunk_size = config.get("chunk_size", 1024)
        chunk_overlap = config.get("chunk_overlap", 100)
        print(f"  分块大小: {chunk_size}, 重叠: {chunk_overlap}")
        
        topology_mode = config.get("topology", {}).get("mode", "auto")
        print(f"  拓扑模式: {topology_mode}")
        
    except Exception as e:
        CLIFormatter.error(f"读取配置失败: {e}")


def validate_config(config_path: str) -> bool:
    """验证配置文件"""
    CLIFormatter.progress(f"验证配置文件: {config_path}")
    
    try:
        extractor = NovelCorpusExtractor(config_path)
        CLIFormatter.success("配置文件有效")
        return True
    except Exception as e:
        CLIFormatter.error(f"配置文件无效: {e}")
        return False


async def export_data(
    extractor: NovelCorpusExtractor,
    results: Dict[str, Any],
    export_format: str = "all",
    export_dir: Optional[str] = None
):
    """导出处理结果"""
    CLIFormatter.progress(f"开始导出数据，格式: {export_format}")
    
    try:
        # 确定导出目录
        if export_dir:
            export_path = Path(export_dir)
        else:
            export_path = extractor.memory_manager.output_dir / "exports"
        
        export_path.mkdir(parents=True, exist_ok=True)
        
        # 创建导出器
        exporter = create_exporter(export_path)
        
        # 准备数据
        export_data_dict = {}
        
        # 文本块结果
        if isinstance(results, dict):
            if 'chunk_results' in results:
                export_data_dict['chunkResults'] = results['chunk_results']
            if 'outline' in results:
                export_data_dict['outline'] = results['outline']
            if 'workflow' in results:
                export_data_dict['workflow'] = results['workflow']
        else:
            export_data_dict['chunkResults'] = results if isinstance(results, list) else []
        
        # 生成基础文件名
        base_filename = f"export_{Path(extractor.memory_manager.output_dir).name}"
        
        # 根据格式导出
        if export_format.lower() == "all":
            exported_files = exporter.export_from_memory_manager(
                extractor.memory_manager,
                chunk_results=export_data_dict.get('chunkResults'),
                outline=export_data_dict.get('outline'),
                workflow_summary=export_data_dict.get('workflow'),
                base_filename=base_filename
            )
            CLIFormatter.success(f"已导出所有格式到: {export_path}")
            for fmt, path in exported_files.items():
                CLIFormatter.info(f"  {fmt.upper()}: {path}")
        elif export_format.lower() == "json":
            path = exporter.export_json(export_data_dict, base_filename)
            CLIFormatter.success(f"JSON导出完成: {path}")
        elif export_format.lower() == "csv":
            if export_data_dict.get('chunkResults'):
                path = exporter.export_csv(export_data_dict['chunkResults'], base_filename)
                CLIFormatter.success(f"CSV导出完成: {path}")
            else:
                CLIFormatter.warning("没有文本块结果可导出为CSV")
        elif export_format.lower() == "excel":
            if export_data_dict.get('chunkResults'):
                excel_data = {'文本块结果': export_data_dict['chunkResults']}
                path = exporter.export_excel(excel_data, base_filename)
                CLIFormatter.success(f"Excel导出完成: {path}")
            else:
                CLIFormatter.warning("没有数据可导出为Excel")
        elif export_format.lower() == "markdown":
            path = exporter.export_markdown(export_data_dict, base_filename)
            CLIFormatter.success(f"Markdown导出完成: {path}")
        elif export_format.lower() == "html":
            path = exporter.export_html(export_data_dict, base_filename)
            CLIFormatter.success(f"HTML导出完成: {path}")
        else:
            CLIFormatter.error(f"不支持的导出格式: {export_format}")
            CLIFormatter.info("支持的格式: json, csv, excel, markdown, html, all")
    
    except Exception as e:
        CLIFormatter.error(f"导出失败: {e}")
        if logger.isEnabledFor(logging.DEBUG):
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="小说语料提取系统 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 处理单个文件
  python cli.py process --input novel.txt --type 玄幻
  
  # 批量处理
  python cli.py batch --files novel1.txt novel2.txt --type 言情
  
  # 显示配置信息
  python cli.py config --show
  
  # 验证配置
  python cli.py config --validate
        """
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="配置文件路径 (默认: config.yaml)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细日志"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # process 命令：处理单个文件
    process_parser = subparsers.add_parser("process", help="处理单个文件")
    process_parser.add_argument("--input", "-i", type=str, required=True, help="输入文件路径")
    process_parser.add_argument("--output", "-o", type=str, help="输出目录")
    process_parser.add_argument("--type", "-t", type=str, default="通用", help="小说类型")
    process_parser.add_argument("--export", "-e", type=str, choices=["json", "csv", "excel", "markdown", "html", "all"], help="导出格式")
    process_parser.add_argument("--export-dir", type=str, help="导出目录（默认：输出目录/exports）")
    
    # batch 命令：批量处理
    batch_parser = subparsers.add_parser("batch", help="批量处理文件")
    batch_parser.add_argument("--files", "-f", nargs="+", required=True, help="文件路径列表")
    batch_parser.add_argument("--output", "-o", type=str, help="输出目录")
    batch_parser.add_argument("--type", "-t", type=str, default="通用", help="小说类型")
    batch_parser.add_argument("--concurrent", "-c", type=int, default=3, help="最大并发数")
    
    # config 命令：配置管理
    config_parser = subparsers.add_parser("config", help="配置管理")
    config_group = config_parser.add_mutually_exclusive_group(required=True)
    config_group.add_argument("--show", action="store_true", help="显示配置信息")
    config_group.add_argument("--validate", action="store_true", help="验证配置文件")
    
    # status 命令：状态查询
    status_parser = subparsers.add_parser("status", help="查询批量任务状态")
    status_parser.add_argument("--batch-id", type=str, help="批量任务ID")
    
    # export 命令：导出已有结果
    export_parser = subparsers.add_parser("export", help="导出处理结果")
    export_parser.add_argument("--output-dir", "-o", type=str, required=True, help="输出目录（包含处理结果）")
    export_parser.add_argument("--format", "-f", type=str, choices=["json", "csv", "excel", "markdown", "html", "all"], default="all", help="导出格式")
    export_parser.add_argument("--export-dir", type=str, help="导出目录（默认：输出目录/exports）")
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging_for_cli(verbose=args.verbose)
    
    # 如果没有指定命令，显示帮助
    if not args.command:
        parser.print_help()
        return
    
    # 执行命令
    try:
        if args.command == "process":
            # 检查配置文件
            if not Path(args.config).exists():
                CLIFormatter.error(f"配置文件不存在: {args.config}")
                return
            
            # 检查输入文件
            if not Path(args.input).exists():
                CLIFormatter.error(f"输入文件不存在: {args.input}")
                return
            
            # 创建提取器并处理
            extractor = NovelCorpusExtractor(args.config)
            asyncio.run(process_single_file(
                extractor,
                args.input,
                args.type,
                args.output,
                args.export,
                args.export_dir
            ))
        
        elif args.command == "batch":
            # 检查配置文件
            if not Path(args.config).exists():
                CLIFormatter.error(f"配置文件不存在: {args.config}")
                return
            
            # 检查文件
            valid_files = []
            for file_path in args.files:
                if Path(file_path).exists():
                    valid_files.append(file_path)
                else:
                    CLIFormatter.warning(f"文件不存在，跳过: {file_path}")
            
            if not valid_files:
                CLIFormatter.error("没有有效的文件可以处理")
                return
            
            # 创建提取器并批量处理
            extractor = NovelCorpusExtractor(args.config)
            asyncio.run(process_batch(
                extractor,
                valid_files,
                args.type,
                args.concurrent,
                args.output
            ))
        
        elif args.command == "config":
            if not Path(args.config).exists():
                CLIFormatter.error(f"配置文件不存在: {args.config}")
                return
            
            if args.show:
                show_config_info(args.config)
            elif args.validate:
                validate_config(args.config)
        
        elif args.command == "status":
            list_batch_status(args.batch_id)
        
        elif args.command == "export":
            # 导出已有结果
            output_dir = Path(args.output_dir)
            if not output_dir.exists():
                CLIFormatter.error(f"输出目录不存在: {output_dir}")
                return
            
            # 创建临时提取器以访问memory_manager
            extractor = NovelCorpusExtractor(args.config)
            extractor.memory_manager.output_dir = output_dir
            
            # 尝试从结果文件加载数据
            chunk_results = []
            outline = None
            workflow_summary = None
            
            # 查找结果文件
            result_files = list(output_dir.glob("*_result.json"))
            if result_files:
                # 从最新的结果文件加载
                latest_file = max(result_files, key=lambda p: p.stat().st_mtime)
                CLIFormatter.info(f"从文件加载结果: {latest_file}")
                try:
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        result_data = json.load(f)
                        chunk_results = result_data.get('chunkResults', result_data.get('chunk_results', []))
                        outline = result_data.get('outline')
                        workflow_summary = result_data.get('workflow')
                    CLIFormatter.success(f"已加载 {len(chunk_results)} 个文本块结果")
                except Exception as e:
                    CLIFormatter.warning(f"加载结果文件失败: {e}")
            else:
                CLIFormatter.warning("未找到结果文件，将仅导出记忆体数据")
            
            # 执行导出
            asyncio.run(export_data(
                extractor,
                {
                    'chunk_results': chunk_results,
                    'outline': outline,
                    'workflow': workflow_summary
                },
                export_format=args.format,
                export_dir=args.export_dir or str(output_dir / "exports")
            ))
        
    except KeyboardInterrupt:
        CLIFormatter.warning("操作被用户中断")
        sys.exit(1)
    except Exception as e:
        CLIFormatter.error(f"执行失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

