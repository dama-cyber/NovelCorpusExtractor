"""
分析者Agent
负责深度分析文本片段并提取关键信息
"""

from typing import Dict, List, Optional
import logging
import re
import yaml
from ..core.model_interface import LLMClient
from ..core.genre_classifier import GenreClassifier
from ..core.villain_analysis import VillainAnalyzer, SevenDeadlySins
from ..core.hook_model import HookModelGuide, HookStage

logger = logging.getLogger(__name__)


class AnalystAgent:
    """分析者Agent - 深度分析文本并提取信息"""
    
    def __init__(self, llm_client: LLMClient, prompt_template: Optional[str] = None):
        """
        初始化分析者
        Args:
            llm_client: LLM客户端
            prompt_template: 分析提示词模板
        """
        self.llm_client = llm_client
        self.prompt_template = prompt_template or self._default_prompt_template()
        self.genre_classifier = GenreClassifier()
        self.villain_analyzer = VillainAnalyzer()
        self.hook_guide = HookModelGuide()
        
        # 滚动摘要缓冲区
        self.summary_buffer = {
            "worldview_snapshot": {},
            "unresolved_foreshadowings": [],
            "character_states": {}
        }
    
    def analyze_chunk(self, chunk: Dict, novel_type: str = "通用") -> Dict:
        """
        分析文本块
        Returns:
            提取的信息字典，包含世界观、人物、伏笔等
        """
        text = chunk.get("text", "")
        chunk_id = chunk.get("chunk_id", "")
        
        # 构建分析提示词
        prompt = self._build_analysis_prompt(text, novel_type, chunk_id)
        
        try:
            # 调用LLM分析
            response = self.llm_client.send_prompt(prompt, system_prompt=self._get_system_prompt())
            
            # 解析响应
            extracted_info = self._parse_response(response)
            
            # 更新摘要缓冲区
            self._update_summary_buffer(extracted_info)
            
            # 分析反派角色（如果存在）
            villain_analysis = self._analyze_villains(extracted_info)
            
            # 分析Hook模型应用
            try:
                chapter_num = int(chunk_id.split('_')[-1]) if '_' in chunk_id else 1
            except:
                chapter_num = 1
            hook_analysis = self.hook_guide.analyze_chapter(text, chapter_num)
            
            return {
                "chunk_id": chunk_id,
                "extracted_info": extracted_info,
                "summary_buffer": self.summary_buffer.copy(),
                "villain_analysis": villain_analysis,
                "hook_analysis": {k.value: v for k, v in hook_analysis.items()}  # 转换为字符串键
            }
        except Exception as e:
            logger.error(f"分析块 {chunk_id} 失败: {e}")
            return {
                "chunk_id": chunk_id,
                "extracted_info": {},
                "error": str(e)
            }
    
    def _analyze_villains(self, extracted_info: Dict) -> Dict:
        """分析反派角色"""
        villains = {}
        
        # 从提取信息中查找反派角色
        characters = extracted_info.get("characters", [])
        if isinstance(characters, list):
            for char in characters:
                if isinstance(char, dict):
                    char_name = char.get("name", "")
                    char_desc = char.get("description", "") or char.get("role", "")
                    
                    # 判断是否为反派
                    if any(keyword in char_desc for keyword in ["反派", "敌人", "对手", "恶", "坏"]):
                        sin_result = self.villain_analyzer.get_primary_sin(char_desc)
                        if sin_result:
                            sin, score = sin_result
                            villains[char_name] = {
                                "sin": sin.value,
                                "score": score,
                                "analysis": self.villain_analyzer.get_sin_analysis(sin)
                            }
        
        return villains
    
    def _build_analysis_prompt(self, text: str, novel_type: str, chunk_id: str) -> str:
        """构建分析提示词"""
        summary_context = self._format_summary_buffer()
        
        # 自动识别类型标签
        detected_genres = self.genre_classifier.get_primary_genres(text, top_k=3)
        genre_info = f"{novel_type}"
        if detected_genres:
            genre_names = [f"{g.value}({score:.2f})" for g, score in detected_genres if score > 0.3]
            if genre_names:
                genre_info += f" | 检测到: {', '.join(genre_names)}"
        
        prompt = f"""请分析以下小说文本片段，提取关键信息。

文本片段ID: {chunk_id}
小说类型: {genre_info}

当前已知信息摘要:
{summary_context}

文本片段:
{text[:2000]}  # 限制长度避免超出token限制

请提取以下信息（以YAML格式输出）:
1. 世界观设定（如有新设定）:
   - 力量体系/等级
   - 地理设定
   - 势力设定
   - 特殊规则

2. 人物信息（如有新人物或人物变化）:
   - 姓名
   - 性格特征
   - 能力/境界
   - 关系变化

3. 伏笔线索（如有）:
   - 伏笔内容
   - 埋设方式
   - 预期回收章节

4. 高价值片段（精彩段落）:
   - 片段类型（战斗/对话/环境描写等）
   - 片段内容
   - 标签

请以YAML格式输出，如果某项没有新信息，则标记为null。
"""
        return prompt
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的小说分析专家，擅长从文本中提取结构化信息。
请仔细分析文本，识别世界观设定、人物信息、伏笔线索和高价值片段。
输出格式必须严格遵循YAML格式。"""
    
    def _parse_response(self, response: str) -> Dict:
        """解析LLM响应为结构化数据"""
        import yaml
        try:
            # 尝试提取YAML部分
            yaml_match = re.search(r'```yaml\n(.*?)\n```', response, re.DOTALL)
            if yaml_match:
                yaml_text = yaml_match.group(1)
            else:
                # 如果没有代码块，尝试直接解析
                yaml_text = response
            
            data = yaml.safe_load(yaml_text) or {}
            return data
        except Exception as e:
            logger.warning(f"解析YAML响应失败: {e}, 原始响应: {response[:200]}")
            # 返回原始响应作为fallback
            return {"raw_response": response}
    
    def _update_summary_buffer(self, extracted_info: Dict):
        """更新摘要缓冲区"""
        # 更新世界观快照
        if "世界观设定" in extracted_info and extracted_info["世界观设定"]:
            self.summary_buffer["worldview_snapshot"].update(
                extracted_info["世界观设定"]
            )
        
        # 更新未解决伏笔
        if "伏笔线索" in extracted_info and extracted_info["伏笔线索"]:
            for foreshadowing in extracted_info["伏笔线索"]:
                if foreshadowing not in self.summary_buffer["unresolved_foreshadowings"]:
                    self.summary_buffer["unresolved_foreshadowings"].append(foreshadowing)
        
        # 更新人物状态
        if "人物信息" in extracted_info and extracted_info["人物信息"]:
            for char_name, char_info in extracted_info["人物信息"].items():
                if char_name not in self.summary_buffer["character_states"]:
                    self.summary_buffer["character_states"][char_name] = {}
                self.summary_buffer["character_states"][char_name].update(char_info)
    
    def _format_summary_buffer(self) -> str:
        """格式化摘要缓冲区为文本"""
        summary = []
        
        if self.summary_buffer["worldview_snapshot"]:
            summary.append("世界观快照:")
            summary.append(str(self.summary_buffer["worldview_snapshot"]))
        
        if self.summary_buffer["unresolved_foreshadowings"]:
            summary.append("\n未解决伏笔:")
            for f in self.summary_buffer["unresolved_foreshadowings"][-5:]:  # 只保留最近5个
                summary.append(f"- {f}")
        
        if self.summary_buffer["character_states"]:
            summary.append("\n人物状态:")
            for char_name, char_state in list(self.summary_buffer["character_states"].items())[-10:]:
                summary.append(f"- {char_name}: {char_state}")
        
        return "\n".join(summary) if summary else "暂无已知信息"
    
    def _default_prompt_template(self) -> str:
        """默认提示词模板"""
        return """分析小说文本片段，提取世界观、人物、伏笔等信息。"""

