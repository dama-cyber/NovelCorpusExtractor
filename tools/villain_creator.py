"""
反派角色创建工具
基于七宗罪理论框架
"""

from typing import Dict, List, Optional
import logging
from ..core.villain_analysis import VillainAnalyzer, SevenDeadlySins

logger = logging.getLogger(__name__)


class VillainCreator:
    """反派角色创建器"""
    
    def __init__(self):
        self.analyzer = VillainAnalyzer()
    
    def create_villain(self, sin: SevenDeadlySins, name: str, 
                      story_context: str = "") -> Dict:
        """
        创建反派角色
        Args:
            sin: 七宗罪类型
            name: 反派名称
            story_context: 故事背景
        """
        analysis = self.analyzer.get_sin_analysis(sin)
        development = self.analyzer.suggest_villain_development(sin, story_context)
        
        villain = {
            "name": name,
            "sin_type": sin.value,
            "psychological_profile": analysis.psychological_analysis,
            "key_traits": analysis.key_traits,
            "literary_symbolism": analysis.literary_symbolism,
            "narrative_function": analysis.narrative_function,
            "suggested_scenes": development["suggested_scenes"],
            "plot_points": analysis.plot_points,
            "typical_examples": analysis.typical_examples
        }
        
        return villain
    
    def generate_villain_prompt(self, sin: SevenDeadlySins, 
                               story_context: str = "") -> str:
        """生成反派角色创建提示词"""
        analysis = self.analyzer.get_sin_analysis(sin)
        guidance = self.analyzer.generate_villain_guidance(sin)
        
        prompt = f"""请基于七宗罪理论框架，创建一个{sin.value}型反派角色。

故事背景：
{story_context}

{guidance}

请创建这个反派角色，包括：
1. 角色名称和基本设定
2. 性格特征（体现{sin.value}的特点）
3. 背景故事（解释为何会有这种罪）
4. 行为模式（如何体现{sin.value}）
5. 与主角的冲突点
6. 可能的结局（体现该罪的报应）

请以YAML格式输出。
"""
        return prompt

