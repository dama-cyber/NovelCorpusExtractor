"""
规划者Agent
负责宏观结构识别与剧情大纲生成
"""

from typing import Dict, List, Optional
import logging
import yaml
from pathlib import Path
from ..core.model_interface import LLMClient
from ..core.memory_manager import MemoryManager
from ..core.genre_classifier import GenreClassifier

logger = logging.getLogger(__name__)


class PlannerAgent:
    """规划者Agent - 剧情架构分析和大纲生成"""
    
    def __init__(self, llm_client: LLMClient, memory_manager: MemoryManager):
        """
        初始化规划者
        Args:
            llm_client: LLM客户端
            memory_manager: 记忆体管理器
        """
        self.llm_client = llm_client
        self.memory_manager = memory_manager
        self.genre_classifier = GenreClassifier()
        self.template_dir = Path(__file__).parent.parent / "outline_templates"
    
    def analyze_structure(self, all_chunks: List[Dict], novel_type: str = "通用") -> Dict:
        """
        分析小说整体结构
        Args:
            all_chunks: 所有文本块
            novel_type: 小说类型
        """
        # 构建结构分析提示词
        chunk_summaries = self._summarize_chunks(all_chunks)
        
        prompt = f"""请分析以下小说的整体剧情结构：

小说类型: {novel_type}
总章节数: {len(set(c.get('chapter', 0) for c in all_chunks))}

章节概要:
{chunk_summaries[:5000]}  # 限制长度

请识别:
1. 叙事结构类型（三幕式/英雄之旅/救猫咪15节拍等）
2. 主要剧情转折点
3. 高潮位置
4. 主线推进节奏
5. 副线设置

以YAML格式输出结构分析结果。"""
        
        try:
            response = self.llm_client.send_prompt(
                prompt,
                system_prompt="你是一个专业的剧情结构分析专家。"
            )
            
            structure = self._parse_structure(response)
            return structure
        except Exception as e:
            logger.error(f"结构分析失败: {e}")
            return {}
    
    def generate_outline(self, structure: Dict, novel_type: str = "通用", 
                        target_chapters: int = 100) -> Dict:
        """
        生成剧情大纲
        Args:
            structure: 结构分析结果
            novel_type: 小说类型
            target_chapters: 目标章节数
        """
        # 加载类型特定的大纲模板
        template = self._load_template_for_genre(novel_type)
        
        # 加载现有世界观和人物信息
        worldview = self.memory_manager.load_worldview()
        characters = self.memory_manager.load_characters()
        
        # 构建模板信息
        template_info = ""
        if template:
            template_info = f"""
推荐的大纲结构: {template.get('structure_type', '三幕式')}
基础结构: {template.get('base_structure', '三幕式')}
特殊元素: {', '.join(template.get('special_elements', []))}
关键情节点: {', '.join(template.get('key_plot_points', []))}
"""
        
        prompt = f"""基于以下信息，生成完整的小说剧情大纲：

小说类型: {novel_type}
目标章节数: {target_chapters}
叙事结构: {structure.get('结构类型', '三幕式')}
{template_info}
世界观设定:
{str(worldview)[:1000]}

主要人物:
{str(characters)[:1000]}

请根据类型特点生成详细的大纲，包括:
1. 总体结构划分（卷/幕）
2. 每章的核心事件
3. 主要冲突和高潮
4. 人物成长弧线
5. 伏笔布局
6. 类型特定元素（{', '.join(template.get('special_elements', [])) if template else '通用元素'}）

以YAML格式输出完整大纲。"""
        
        try:
            response = self.llm_client.send_prompt(
                prompt,
                system_prompt="你是一个专业的小说大纲规划专家。"
            )
            
            outline = self._parse_outline(response)
            
            # 保存到记忆体
            self.memory_manager.save_plot(outline)
            
            return outline
        except Exception as e:
            logger.error(f"大纲生成失败: {e}")
            return {}
    
    def _summarize_chunks(self, chunks: List[Dict]) -> str:
        """汇总文本块为概要"""
        summaries = []
        for chunk in chunks[:100]:  # 限制数量
            chunk_id = chunk.get("chunk_id", "")
            text_preview = chunk.get("text", "")[:100]
            summaries.append(f"{chunk_id}: {text_preview}...")
        return "\n".join(summaries)
    
    def _parse_structure(self, response: str) -> Dict:
        """解析结构分析结果"""
        import yaml
        import re
        
        try:
            yaml_match = re.search(r'```yaml\n(.*?)\n```', response, re.DOTALL)
            if yaml_match:
                yaml_text = yaml_match.group(1)
            else:
                yaml_text = response
            
            return yaml.safe_load(yaml_text) or {}
        except Exception as e:
            logger.warning(f"解析结构分析结果失败: {e}")
            return {"raw_response": response}
    
    def _parse_outline(self, response: str) -> Dict:
        """解析大纲"""
        import re
        
        try:
            yaml_match = re.search(r'```yaml\n(.*?)\n```', response, re.DOTALL)
            if yaml_match:
                yaml_text = yaml_match.group(1)
            else:
                yaml_text = response
            
            return yaml.safe_load(yaml_text) or {}
        except Exception as e:
            logger.warning(f"解析大纲失败: {e}")
            return {"raw_response": response}
    
    def _load_template_for_genre(self, genre: str) -> Optional[Dict]:
        """加载类型特定的大纲模板"""
        if not genre or genre == "通用":
            return None
        
        # 尝试加载类型特定模板
        safe_name = genre.replace("/", "_").replace(" ", "_")
        template_file = self.template_dir / f"{safe_name}_大纲模板.yaml"
        
        if template_file.exists():
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logger.warning(f"加载模板失败 {template_file}: {e}")
        
        # 如果没有特定模板，返回None
        return None
    
    def get_available_templates(self) -> List[str]:
        """获取所有可用的大纲模板"""
        templates = []
        
        # 通用模板（目前实际存在的8个模板）
        generic_templates = [
            "三幕式大纲模板.yaml",
            "起承转合式大纲模板.yaml",
            "环形叙事大纲模板.yaml",
            "英雄之旅大纲模板.yaml",
            "草蛇灰线式大纲模板.yaml",
            "碎片拼贴式大纲模板.yaml",
            "弗莱塔格金字塔模板.yaml",
            "救猫咪15节拍模板.yaml",
        ]
        
        for template_file in generic_templates:
            if (self.template_dir / template_file).exists():
                templates.append(template_file.replace("_大纲模板.yaml", "").replace(".yaml", ""))
        
        # 类型特定模板
        for template_file in self.template_dir.glob("*_大纲模板.yaml"):
            genre_name = template_file.stem.replace("_大纲模板", "")
            templates.append(genre_name)
        
        return templates

