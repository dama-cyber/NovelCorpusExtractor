"""
深度提取者Agent
接收分类后的文本块，应用专用提示词进行强化解析
"""

from typing import Dict, List, Optional
import logging
from ..core.model_interface import LLMClient
from ..core.frankentexts import FrankentextsManager
from ..core.genre_classifier import GenreClassifier, GenreCategory

logger = logging.getLogger(__name__)


class ExtractorAgent:
    """深度提取者Agent - 强化解析特定类型文本"""
    
    def __init__(self, llm_client: LLMClient, frankentexts_manager: FrankentextsManager):
        """
        初始化深度提取者
        Args:
            llm_client: LLM客户端
            frankentexts_manager: Frankentexts管理器
        """
        self.llm_client = llm_client
        self.frankentexts_manager = frankentexts_manager
        self.genre_classifier = GenreClassifier()
        self.prompt_templates = self._load_prompt_templates()
    
    def extract(self, scanned_chunk: Dict, novel_type: str = "通用") -> Dict:
        """
        深度提取文本块
        Args:
            scanned_chunk: 已扫描分类的文本块
            novel_type: 小说类型（支持36+种类型）
        """
        text = scanned_chunk.get("text", "")
        primary_type = scanned_chunk.get("primary_type", "普通叙述")
        chunk_id = scanned_chunk.get("chunk_id", "")
        
        # 自动识别类型标签
        detected_genres = self.genre_classifier.get_primary_genres(text, top_k=3)
        genre_names = [g.value for g, score in detected_genres if score > 0.3]
        
        # 如果指定了类型，也加入
        if novel_type and novel_type != "通用":
            if novel_type not in genre_names:
                genre_names.insert(0, novel_type)
        
        # 根据类型选择专用提示词
        prompt_template = self.prompt_templates.get(primary_type, self._default_template())
        
        # 构建提取提示词
        genre_info = f"类型标签: {', '.join(genre_names)}" if genre_names else f"类型: {novel_type}"
        prompt = prompt_template.format(
            text=text[:2000],  # 限制长度
            novel_type=genre_info,
            chunk_id=chunk_id
        )
        
        try:
            # 调用LLM提取
            response = self.llm_client.send_prompt(
                prompt,
                system_prompt=self._get_system_prompt(primary_type)
            )
            
            # 解析提取结果
            extracted_data = self._parse_extraction(response, primary_type)
            
            # 如果是高价值片段，保存到Frankentexts
            if extracted_data.get("is_valuable", False):
                # 确定保存的genre（使用检测到的类型或指定类型）
                save_genre = genre_names[0] if genre_names else novel_type
                
                fragment = self.frankentexts_manager.extract_fragment(
                    text=text,
                    fragment_type=primary_type,
                    metadata={
                        "novel_type": novel_type,
                        "detected_genres": genre_names,
                        "chunk_id": chunk_id,
                        "extracted_data": extracted_data
                    }
                )
                self.frankentexts_manager.save_fragment(fragment, genre=save_genre)
                logger.info(f"高价值片段已保存: {chunk_id} ({primary_type}, 类型: {save_genre})")
            
            return {
                "chunk_id": chunk_id,
                "type": primary_type,
                "extracted_data": extracted_data
            }
        except Exception as e:
            logger.error(f"深度提取失败 {chunk_id}: {e}")
            return {
                "chunk_id": chunk_id,
                "type": primary_type,
                "error": str(e)
            }
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """加载提示词模板"""
        return {
            "战斗场景": """请深度分析以下战斗场景，提取关键信息：

小说类型: {novel_type}
文本块ID: {chunk_id}

战斗场景文本:
{text}

请提取:
1. 战斗双方信息
2. 使用的招式/技能
3. 战斗节奏和转折点
4. 精彩描写片段（可直接复用）
5. 战斗结果和影响

以YAML格式输出。""",
            
            "对话密集区": """请分析以下对话段落，提取关键信息：

小说类型: {novel_type}
文本块ID: {chunk_id}

对话文本:
{text}

请提取:
1. 对话双方身份和关系
2. 对话的核心信息
3. 人物语言风格特征
4. 潜台词和暗示
5. 精彩对话片段（可直接复用）

以YAML格式输出。""",
            
            "环境描写": """请分析以下环境描写，提取关键信息：

小说类型: {novel_type}
文本块ID: {chunk_id}

环境描写文本:
{text}

请提取:
1. 环境类型和特点
2. 氛围营造手法
3. 感官描写（视觉/听觉/嗅觉等）
4. 环境与情节的关联
5. 精彩描写片段（可直接复用）

以YAML格式输出。""",
            
            "修炼突破": """请分析以下修炼突破场景，提取关键信息：

小说类型: {novel_type}
文本块ID: {chunk_id}

修炼文本:
{text}

请提取:
1. 突破前的境界
2. 突破后的境界
3. 突破过程和契机
4. 突破带来的变化
5. 精彩描写片段（可直接复用）

以YAML格式输出。"""
        }
    
    def _default_template(self) -> str:
        """默认模板"""
        return """请分析以下文本片段，提取关键信息：

小说类型: {novel_type}
文本块ID: {chunk_id}

文本:
{text}

请提取关键信息和可复用片段，以YAML格式输出。"""
    
    def _get_system_prompt(self, text_type: str) -> str:
        """获取系统提示词"""
        return f"""你是一个专业的小说分析专家，擅长深度解析{text_type}类型的文本。
请仔细分析文本，提取结构化信息和可复用的精彩片段。"""
    
    def _parse_extraction(self, response: str, text_type: str) -> Dict:
        """解析提取结果"""
        import yaml
        import re
        
        try:
            # 尝试提取YAML
            yaml_match = re.search(r'```yaml\n(.*?)\n```', response, re.DOTALL)
            if yaml_match:
                yaml_text = yaml_match.group(1)
            else:
                yaml_text = response
            
            data = yaml.safe_load(yaml_text) or {}
            
            # 判断是否为高价值片段
            data["is_valuable"] = self._is_valuable_fragment(data, text_type)
            
            return data
        except Exception as e:
            logger.warning(f"解析提取结果失败: {e}")
            return {"raw_response": response, "is_valuable": False}
    
    def _is_valuable_fragment(self, data: Dict, text_type: str) -> bool:
        """判断是否为高价值片段"""
        # 简单判断逻辑：如果提取到精彩片段标记，则认为是高价值
        valuable_keywords = ["精彩", "经典", "可复用", "优秀", "亮点"]
        data_str = str(data).lower()
        return any(keyword in data_str for keyword in valuable_keywords)

