"""
30_开篇场景生成器
生成吸引人的开篇场景
"""

from typing import Dict, List, Optional
import logging
from ..core.hook_model import HookModelGuide, HookStage
from ..core.genre_classifier import GenreClassifier

logger = logging.getLogger(__name__)


class OpeningSceneGenerator:
    """开篇场景生成器"""
    
    def __init__(self):
        if HookModelGuide:
            self.hook_guide = HookModelGuide()
        else:
            self.hook_guide = None
        if GenreClassifier:
            self.genre_classifier = GenreClassifier()
        else:
            self.genre_classifier = None
        self.opening_templates = self._build_templates()
    
    def _build_templates(self) -> Dict[str, List[str]]:
        """构建开篇模板"""
        return {
            "conflict": [
                "{场景}，{主角}面临{危机}",
                "{时间}，{地点}，{事件}突然发生",
                "{主角}没想到，{转折}竟然{结果}"
            ],
            "mystery": [
                "{场景}，{主角}发现了{秘密}",
                "{时间}，{地点}，{疑问}浮现在{主角}心中",
                "{主角}不知道，{真相}即将揭晓"
            ],
            "action": [
                "{场景}，{主角}正在{行动}",
                "{时间}，{地点}，{主角}遭遇{事件}",
                "{主角}来不及反应，{危机}已经{状态}"
            ],
            "emotion": [
                "{场景}，{主角}感到{情感}",
                "{时间}，{地点}，{主角}想起了{回忆}",
                "{主角}没想到，{情感}会如此{程度}"
            ]
        }
    
    def generate_opening(self, novel_type: str = "通用", 
                        opening_style: str = "conflict",
                        context: Dict = None) -> Dict:
        """
        生成开篇场景
        Args:
            novel_type: 小说类型
            opening_style: 开篇风格（conflict/mystery/action/emotion/auto）
            context: 上下文信息（主角、世界观等）
        """
        context = context or {}
        
        # 获取Hook触发阶段指导
        if self.hook_guide and HookStage:
            trigger_guide = self.hook_guide.get_stage_guide(HookStage.TRIGGER)
        else:
            trigger_guide = None
        
        # 选择模板
        if opening_style == "auto":
            opening_style = self._detect_best_style(novel_type, context)
        
        templates = self.opening_templates.get(opening_style, self.opening_templates["conflict"])
        
        # 生成开篇场景
        opening_scenes = []
        for template in templates:
            scene = self._fill_template(template, novel_type, context)
            if scene:
                opening_scenes.append(scene)
        
        # 生成完整开篇（包含第一段）
        full_opening = self._generate_full_opening(opening_scenes[0] if opening_scenes else "", novel_type, trigger_guide)
        
        return {
            "opening_scene": opening_scenes[0] if opening_scenes else "",
            "alternative_scenes": opening_scenes[1:],
            "full_opening": full_opening,
            "hook_elements": self._extract_hook_elements(full_opening),
            "hook_score": self._score_opening(full_opening),
            "optimization_suggestions": self._generate_opening_suggestions(full_opening, trigger_guide) if trigger_guide else []
        }
    
    def _detect_best_style(self, novel_type: str, context: Dict) -> str:
        """检测最佳开篇风格"""
        style_map = {
            "悬疑": "mystery",
            "玄幻": "action",
            "言情": "emotion",
            "都市": "conflict",
            "重生文": "conflict",
            "系统文": "action"
        }
        if self.genre_classifier and context.get("sample_text"):
            detected = self.genre_classifier.classify(context["sample_text"])
            return style_map.get(detected, style_map.get(novel_type, "conflict"))
        return style_map.get(novel_type, "conflict")
    
    def _fill_template(self, template: str, novel_type: str, context: Dict) -> str:
        """填充模板"""
        scene = template
        
        # 从context获取信息
        protagonist = context.get("protagonist", "主角")
        location = context.get("location", "未知地点")
        time = context.get("time", "某日")
        
        # 根据类型填充
        if "玄幻" in novel_type or "仙侠" in novel_type:
            location = location or "宗门"
            crisis = context.get("crisis") or "强敌来袭"
        elif "都市" in novel_type:
            location = location or "都市"
            crisis = context.get("crisis", "商业危机")
        elif "言情" in novel_type:
            location = location or "咖啡厅"
            crisis = context.get("crisis", "情感危机")
        else:
            crisis = context.get("crisis", "未知危机")
        
        # 替换占位符
        scene = scene.replace("{主角}", protagonist)
        scene = scene.replace("{地点}", location)
        scene = scene.replace("{时间}", time)
        scene = scene.replace("{场景}", f"{time}，{location}")
        scene = scene.replace("{危机}", crisis)
        scene = scene.replace("{事件}", crisis)
        scene = scene.replace("{转折}", "这个变化")
        scene = scene.replace("{结果}", "发生")
        
        return scene
    
    def _generate_full_opening(self, opening_scene: str, novel_type: str, 
                              trigger_guide=None) -> str:
        """生成完整开篇（第一段）"""
        # 构建开篇段落
        opening = f"{opening_scene}。\n\n"
        
        # 添加类型特定的元素
        if "重生" in novel_type:
            opening += "他没想到，自己竟然重生了。"
        elif "系统" in novel_type:
            opening += "突然，一个声音在他脑海中响起。"
        elif "穿越" in novel_type:
            opening += "当他再次睁开眼睛时，发现自己来到了一个完全陌生的世界。"
        elif "悬疑" in novel_type:
            opening += "这个发现，将彻底改变他的命运。"
        else:
            opening += "这一刻，他的人生将发生翻天覆地的变化。"
        
        return opening
    
    def _extract_hook_elements(self, opening: str) -> Dict:
        """提取钩子元素"""
        trigger_keywords = ["逆袭", "打脸", "屈辱", "愤怒", "不甘", "突然", "没想到"]
        
        elements = {
            "has_conflict": any(kw in opening for kw in ["冲突", "危机", "危险", "挑战"]),
            "has_mystery": any(kw in opening for kw in ["秘密", "真相", "谜团", "疑问"]),
            "has_emotion": any(kw in opening for kw in ["愤怒", "悲伤", "震惊", "不甘"]),
            "has_action": any(kw in opening for kw in ["战斗", "行动", "发生", "开始"]),
            "trigger_keywords_count": sum(1 for kw in trigger_keywords if kw in opening)
        }
        
        return elements
    
    def _generate_opening_suggestions(self, opening: str, trigger_guide=None) -> List[str]:
        """生成开篇优化建议"""
        suggestions = []
        elements = self._extract_hook_elements(opening)
        
        if not elements["has_conflict"]:
            suggestions.append("建议增加冲突元素，引发读者情绪")
        
        if elements["trigger_keywords_count"] < 2:
            suggestions.append("建议增加更多触发关键词，提升吸引力")
        
        if len(opening) < 100:
            suggestions.append("建议扩展开篇内容，增加细节描写")
        elif len(opening) > 500:
            suggestions.append("建议精简开篇，保持紧凑")
        
        if not any(elements[k] for k in ["has_conflict", "has_mystery", "has_action"]):
            suggestions.append("建议增加冲突、悬念或行动元素")
        
        return suggestions

    def _score_opening(self, opening: str) -> float:
        """根据钩子元素给开篇打分"""
        elements = self._extract_hook_elements(opening)
        weights = {
            "has_conflict": 0.3,
            "has_mystery": 0.2,
            "has_emotion": 0.1,
            "has_action": 0.2,
            "trigger_keywords_count": 0.2
        }
        score = 0.0
        for key, weight in weights.items():
            if key == "trigger_keywords_count":
                score += min(1, elements[key] / 3) * weight
            else:
                score += weight if elements[key] else 0
        length_penalty = 0.05 if len(opening) > 500 else 0
        return round(max(0.0, min(1.0, score - length_penalty)), 2)

