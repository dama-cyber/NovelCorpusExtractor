"""
数据导出模块
支持将处理结果导出为多种格式：JSON、CSV、Excel、Markdown、HTML等
"""

import json
import csv
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import yaml

logger = logging.getLogger(__name__)

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logger.warning("pandas未安装，Excel导出功能将不可用")

try:
    from markdown import markdown
    from markdown.extensions import tables, fenced_code
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
    logger.warning("markdown未安装，部分Markdown功能可能受限")


class DataExporter:
    """数据导出器"""
    
    def __init__(self, output_dir: Union[str, Path] = "exports"):
        """
        初始化导出器
        
        Args:
            output_dir: 导出文件保存目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_json(
        self,
        data: Dict[str, Any],
        filename: Optional[str] = None,
        pretty: bool = True
    ) -> Path:
        """
        导出为JSON格式
        
        Args:
            data: 要导出的数据
            filename: 文件名（不含扩展名），如果为None则使用时间戳
            pretty: 是否格式化输出
        
        Returns:
            导出文件路径
        """
        if filename is None:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if not filename.endswith('.json'):
            filename += '.json'
        
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                json.dump(data, f, ensure_ascii=False)
        
        logger.info(f"JSON导出完成: {output_path}")
        return output_path
    
    def export_csv(
        self,
        data: List[Dict[str, Any]],
        filename: Optional[str] = None,
        flatten_nested: bool = True
    ) -> Path:
        """
        导出为CSV格式
        
        Args:
            data: 要导出的数据列表
            filename: 文件名（不含扩展名）
            flatten_nested: 是否展平嵌套字典
        
        Returns:
            导出文件路径
        """
        if not data:
            raise ValueError("数据列表不能为空")
        
        if filename is None:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        output_path = self.output_dir / filename
        
        # 展平嵌套字典
        if flatten_nested:
            flattened_data = [self._flatten_dict(item) for item in data]
        else:
            flattened_data = data
        
        # 获取所有字段名
        fieldnames = set()
        for item in flattened_data:
            fieldnames.update(item.keys())
        fieldnames = sorted(fieldnames)
        
        # 写入CSV
        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for item in flattened_data:
                # 确保所有字段都存在
                row = {field: item.get(field, '') for field in fieldnames}
                writer.writerow(row)
        
        logger.info(f"CSV导出完成: {output_path}")
        return output_path
    
    def export_excel(
        self,
        data: Dict[str, List[Dict[str, Any]]],
        filename: Optional[str] = None
    ) -> Path:
        """
        导出为Excel格式（多工作表）
        
        Args:
            data: 字典，键为工作表名，值为数据列表
            filename: 文件名（不含扩展名）
        
        Returns:
            导出文件路径
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas未安装，无法导出Excel格式。请运行: pip install pandas openpyxl")
        
        if filename is None:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'
        
        output_path = self.output_dir / filename
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for sheet_name, sheet_data in data.items():
                if sheet_data:
                    # 展平嵌套字典
                    flattened_data = [self._flatten_dict(item) for item in sheet_data]
                    df = pd.DataFrame(flattened_data)
                    df.to_excel(writer, sheet_name=sheet_name[:31], index=False)  # Excel工作表名限制31字符
                else:
                    # 空工作表
                    pd.DataFrame().to_excel(writer, sheet_name=sheet_name[:31], index=False)
        
        logger.info(f"Excel导出完成: {output_path}")
        return output_path
    
    def export_markdown(
        self,
        data: Dict[str, Any],
        filename: Optional[str] = None,
        include_metadata: bool = True
    ) -> Path:
        """
        导出为Markdown格式
        
        Args:
            data: 要导出的数据
            filename: 文件名（不含扩展名）
            include_metadata: 是否包含元数据
        
        Returns:
            导出文件路径
        """
        if filename is None:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if not filename.endswith('.md'):
            filename += '.md'
        
        output_path = self.output_dir / filename
        
        md_content = []
        
        # 标题
        md_content.append("# 小说语料提取结果\n")
        md_content.append(f"**导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        md_content.append("\n---\n")
        
        # 文本块结果
        if 'chunkResults' in data or 'chunk_results' in data:
            chunk_results = data.get('chunkResults') or data.get('chunk_results', [])
            if chunk_results:
                md_content.append("\n## 文本块分析结果\n\n")
                md_content.append(f"共 {len(chunk_results)} 个文本块\n\n")
                
                for i, chunk in enumerate(chunk_results, 1):
                    md_content.append(f"### 文本块 {i}\n\n")
                    if 'title' in chunk:
                        md_content.append(f"**标题**: {chunk['title']}\n\n")
                    if 'summary' in chunk:
                        md_content.append(f"**摘要**: {chunk['summary']}\n\n")
                    if 'themes' in chunk:
                        md_content.append(f"**主题**: {', '.join(chunk['themes']) if isinstance(chunk['themes'], list) else chunk['themes']}\n\n")
                    if 'hookScore' in chunk:
                        md_content.append(f"**钩子分数**: {chunk['hookScore']}\n\n")
                    md_content.append("---\n\n")
        
        # 大纲
        if 'outline' in data and data['outline']:
            md_content.append("\n## 剧情大纲\n\n")
            md_content.append(f"{data['outline']}\n\n")
            md_content.append("---\n\n")
        
        # 记忆体
        if 'memories' in data and data['memories']:
            md_content.append("\n## 记忆体\n\n")
            for memory in data['memories']:
                if 'title' in memory:
                    md_content.append(f"### {memory['title']}\n\n")
                if 'entries' in memory:
                    for entry in memory['entries']:
                        md_content.append(f"- {entry}\n")
                md_content.append("\n")
            md_content.append("---\n\n")
        
        # 工作流信息
        if 'workflow' in data and data['workflow']:
            md_content.append("\n## 工作流信息\n\n")
            workflow = data['workflow']
            if isinstance(workflow, dict):
                for key, value in workflow.items():
                    md_content.append(f"**{key}**: {value}\n\n")
            md_content.append("---\n\n")
        
        # 创作输出
        if 'creative' in data and data['creative']:
            md_content.append("\n## 创作输出\n\n")
            creative = data['creative']
            if isinstance(creative, dict):
                for key, value in creative.items():
                    md_content.append(f"### {key}\n\n")
                    if isinstance(value, str):
                        md_content.append(f"{value}\n\n")
                    elif isinstance(value, dict):
                        for k, v in value.items():
                            md_content.append(f"**{k}**: {v}\n\n")
            md_content.append("---\n\n")
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(''.join(md_content))
        
        logger.info(f"Markdown导出完成: {output_path}")
        return output_path
    
    def export_html(
        self,
        data: Dict[str, Any],
        filename: Optional[str] = None,
        template: Optional[str] = None
    ) -> Path:
        """
        导出为HTML格式
        
        Args:
            data: 要导出的数据
            filename: 文件名（不含扩展名）
            template: 自定义HTML模板（可选）
        
        Returns:
            导出文件路径
        """
        if filename is None:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if not filename.endswith('.html'):
            filename += '.html'
        
        output_path = self.output_dir / filename
        
        # 生成Markdown内容
        md_exporter = DataExporter(self.output_dir)
        md_path = md_exporter.export_markdown(data, filename.replace('.html', '_temp.md'), include_metadata=False)
        
        # 读取Markdown内容
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # 删除临时Markdown文件
        md_path.unlink()
        
        # 转换为HTML
        if MARKDOWN_AVAILABLE:
            html_body = markdown(md_content, extensions=['tables', 'fenced_code'])
        else:
            # 简单转换
            html_body = md_content.replace('\n', '<br>\n')
        
        # HTML模板
        html_template = template or """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>小说语料提取结果</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        h3 {{
            color: #555;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
{body}
</body>
</html>"""
        
        html_content = html_template.format(body=html_body)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML导出完成: {output_path}")
        return output_path
    
    def export_all_formats(
        self,
        data: Dict[str, Any],
        base_filename: Optional[str] = None
    ) -> Dict[str, Path]:
        """
        导出为所有支持的格式
        
        Args:
            data: 要导出的数据
            base_filename: 基础文件名（不含扩展名）
        
        Returns:
            字典，键为格式名，值为文件路径
        """
        if base_filename is None:
            base_filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        results = {}
        
        # JSON
        results['json'] = self.export_json(data, base_filename)
        
        # CSV（如果有文本块结果）
        if 'chunkResults' in data or 'chunk_results' in data:
            chunk_results = data.get('chunkResults') or data.get('chunk_results', [])
            if chunk_results:
                results['csv'] = self.export_csv(chunk_results, f"{base_filename}_chunks")
        
        # Excel（如果有多个数据表）
        if 'chunkResults' in data or 'chunk_results' in data:
            chunk_results = data.get('chunkResults') or data.get('chunk_results', [])
            if chunk_results and PANDAS_AVAILABLE:
                excel_data = {
                    '文本块结果': chunk_results,
                }
                if 'memories' in data and data['memories']:
                    excel_data['记忆体'] = data['memories']
                results['excel'] = self.export_excel(excel_data, base_filename)
        
        # Markdown
        results['markdown'] = self.export_markdown(data, base_filename)
        
        # HTML
        results['html'] = self.export_html(data, base_filename)
        
        return results
    
    def export_from_memory_manager(
        self,
        memory_manager,
        chunk_results: Optional[List[Dict]] = None,
        outline: Optional[str] = None,
        workflow_summary: Optional[Dict] = None,
        base_filename: Optional[str] = None
    ) -> Dict[str, Path]:
        """
        从MemoryManager导出数据
        
        Args:
            memory_manager: MemoryManager实例
            chunk_results: 文本块结果列表
            outline: 剧情大纲
            workflow_summary: 工作流摘要
            base_filename: 基础文件名
        
        Returns:
            导出文件路径字典
        """
        # 收集所有数据
        data = {}
        
        if chunk_results:
            data['chunkResults'] = chunk_results
        
        if outline:
            data['outline'] = outline
        
        if workflow_summary:
            data['workflow'] = workflow_summary
        
        # 加载记忆体
        memories = []
        
        worldview = memory_manager.load_worldview()
        if worldview:
            memories.append({
                'id': 'worldview',
                'title': '世界观记忆体',
                'data': worldview
            })
        
        characters = memory_manager.load_characters()
        if characters:
            memories.append({
                'id': 'character',
                'title': '人物记忆体',
                'data': characters
            })
        
        plot = memory_manager.load_plot()
        if plot:
            memories.append({
                'id': 'plot',
                'title': '剧情规划大纲',
                'data': plot
            })
        
        foreshadowing = memory_manager.load_foreshadowing()
        if foreshadowing:
            memories.append({
                'id': 'foreshadowing',
                'title': '伏笔追踪表',
                'data': foreshadowing
            })
        
        if memories:
            data['memories'] = memories
        
        # 导出所有格式
        return self.export_all_formats(data, base_filename)
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """
        展平嵌套字典
        
        Args:
            d: 要展平的字典
            parent_key: 父键名
            sep: 分隔符
        
        Returns:
            展平后的字典
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # 列表转换为字符串
                items.append((new_key, ', '.join(str(item) for item in v)))
            else:
                items.append((new_key, v))
        return dict(items)


def create_exporter(output_dir: Union[str, Path] = "exports") -> DataExporter:
    """
    创建数据导出器的便捷函数
    
    Args:
        output_dir: 导出文件保存目录
    
    Returns:
        DataExporter实例
    """
    return DataExporter(output_dir)


