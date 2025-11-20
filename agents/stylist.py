"""
风格塑造者Agent
专注于语言风格和文本微观特征提取
"""

from typing import Dict, List, Optional
import logging
from ..core.model_interface import LLMClient

logger = logging.getLogger(__name__)


class StylistAgent:
    """风格塑造者Agent - 语言风格分析"""
    
    def __init__(self, llm_client: LLMClient):
        """
        初始化风格Agent
        Args:
            llm_client: LLM客户端
        """
        self.llm_client = llm_client
    
    def analyze_style(self, text_samples: List[str], character_name: Optional[str] = None) -> Dict:
        """
        分析语言风格
        Args:
            text_samples: 文本样本列表
            character_name: 如果是人物语言，指定人物名
        """
        combined_text = "\n\n".join(text_samples[:10])  # 限制样本数量
        
        if character_name:
            prompt = f"""请分析以下{character_name}的语言风格特征：

文本样本:
{combined_text[:3000]}

请提取:
1. 常用词汇和表达习惯
2. 句式特点（长句/短句，复杂/简单）
3. 口头禅和固定表达
4. 情绪表达方式
5. 语言节奏和韵律

以YAML格式输出风格特征。"""
        else:
            prompt = f"""请分析以下文本的整体语言风格：

文本样本:
{combined_text[:3000]}

请提取:
1. 文笔风格（华丽/朴实/简洁等）
2. 修辞手法使用
3. 句式特点
4. 节奏控制
5. 氛围营造手法

以YAML格式输出风格特征。"""
        
        try:
            response = self.llm_client.send_prompt(
                prompt,
                system_prompt="你是一个专业的语言风格分析专家。"
            )
            
            style_features = self._parse_style(response)
            return style_features
        except Exception as e:
            logger.error(f"风格分析失败: {e}")
            return {}
    
    def extract_character_voice(self, dialogue_samples: List[str], character_name: str) -> Dict:
        """提取人物语言特征"""
        return self.analyze_style(dialogue_samples, character_name)
    
    def _parse_style(self, response: str) -> Dict:
        """解析风格分析结果"""
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
            logger.warning(f"解析风格分析结果失败: {e}")
            return {"raw_response": response}

