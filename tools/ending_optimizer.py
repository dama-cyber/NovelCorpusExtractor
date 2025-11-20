"""
31_结尾收束优化器
优化小说结尾，确保圆满收束
"""

from typing import Dict, List, Optional
import logging
from ..core.memory_manager import MemoryManager

logger = logging.getLogger(__name__)


class EndingOptimizer:
    """结尾收束优化器"""
    
    def __init__(self, memory_manager=None):
        self.memory_manager = memory_manager
        self.ending_templates = self._build_templates()
    
    def _build_templates(self) -> Dict[str, List[str]]:
        """构建结尾模板"""
        return {
            "happy_ending": [
                "{主角}终于{成就}，{结果}",
                "经过{历程}，{主角}实现了{目标}",
                "{主角}站在{地点}，回望{过去}，展望{未来}"
            ],
            "open_ending": [
                "{主角}的{旅程}还在继续",
                "{疑问}的答案，留待{未来}揭晓",
                "{主角}知道，{新挑战}即将到来"
            ],
            "tragic_ending": [
                "{主角}虽然{失败}，但{意义}",
                "即使{结果}，{主角}的{精神}永存",
                "{主角}用{代价}换来了{收获}"
            ],
            "circular_ending": [
                "{主角}回到了{起点}，但{变化}",
                "一切似乎回到了原点，但{不同}",
                "{开头}的{场景}再次出现，但{主角}已经{成长}"
            ]
        }
    
    def optimize_ending(self, final_chapters: List[Dict], 
                       novel_type: str = "通用",
                       ending_style: str = "happy_ending") -> Dict:
        """
        优化结尾
        Args:
            final_chapters: 最后几章内容
            novel_type: 小说类型
            ending_style: 结尾风格
        """
        # 检查伏笔回收
        unresolved_foreshadowings = []
        if self.memory_manager:
            foreshadowings = self.memory_manager.load_foreshadowing()
            unresolved_foreshadowings = [
                f for f in foreshadowings 
                if f.get("status") == "未回收"
            ]
        
        # 检查人物结局
        character_resolutions = self._check_character_resolutions(final_chapters)
        subplot_status = self._evaluate_subplots(final_chapters)
        tone_alignment = self._check_tone_alignment(final_chapters, ending_style)
        
        # 检查主线收束
        main_plot_resolution = self._check_main_plot_resolution(final_chapters)
        
        # 生成结尾建议
        suggestions = self._generate_ending_suggestions(
            unresolved_foreshadowings,
            character_resolutions,
            main_plot_resolution,
            ending_style
        )
        
        # 生成结尾段落
        ending_paragraph = self._generate_ending_paragraph(
            final_chapters, novel_type, ending_style
        )
        
        return {
            "ending_style": ending_style,
            "unresolved_foreshadowings": len(unresolved_foreshadowings),
            "foreshadowing_list": unresolved_foreshadowings[:5],
            "character_resolutions": character_resolutions,
            "subplot_closure": subplot_status,
            "tone_alignment": tone_alignment,
            "main_plot_resolution": main_plot_resolution,
            "suggestions": suggestions,
            "ending_paragraph": ending_paragraph
        }
    
    def _check_character_resolutions(self, final_chapters: List[Dict]) -> Dict:
        """检查人物结局"""
        resolutions = {
            "resolved": [],
            "unresolved": [],
            "suggestions": []
        }
        
        # 这里可以分析章节内容，检查主要人物的结局
        # 简化实现
        content = " ".join(ch.get("content", "") for ch in final_chapters)
        
        # 检查是否有明确的结局描述
        ending_keywords = ["结局", "归宿", "最终", "最后", "从此"]
        has_ending = any(kw in content for kw in ending_keywords)
        
        if not has_ending:
            resolutions["suggestions"].append("建议明确交代主要人物的最终结局")
        
        return resolutions
    
    def _check_main_plot_resolution(self, final_chapters: List[Dict]) -> Dict:
        """检查主线收束"""
        content = " ".join(ch.get("content", "") for ch in final_chapters)
        
        resolution_keywords = ["完成", "实现", "达成", "解决", "结束"]
        has_resolution = any(kw in content for kw in resolution_keywords)
        
        return {
            "is_resolved": has_resolution,
            "suggestion": "建议明确交代主线剧情的最终结果" if not has_resolution else "主线收束清晰"
        }
    
    def _generate_ending_suggestions(self, unresolved_foreshadowings: List,
                                    character_resolutions: Dict,
                                    main_plot_resolution: Dict,
                                    ending_style: str) -> List[str]:
        """生成结尾建议"""
        suggestions = []
        
        # 伏笔回收建议
        if unresolved_foreshadowings:
            count = len(unresolved_foreshadowings)
            suggestions.append(f"还有{count}个伏笔未回收，建议在结尾前回收或说明")
        
        # 人物结局建议
        if character_resolutions["suggestions"]:
            suggestions.extend(character_resolutions["suggestions"])
        
        # 主线收束建议
        if not main_plot_resolution["is_resolved"]:
            suggestions.append(main_plot_resolution["suggestion"])
        
        # 结尾风格建议
        if ending_style == "happy_ending":
            suggestions.append("确保所有主要冲突都得到圆满解决")
        elif ending_style == "open_ending":
            suggestions.append("开放式结尾要留有想象空间，但主要线索要收束")
        elif ending_style == "tragic_ending":
            suggestions.append("悲剧结尾要有意义，不能为了虐而虐")
        
        return suggestions
    
    def _generate_ending_paragraph(self, final_chapters: List[Dict],
                                  novel_type: str, ending_style: str) -> str:
        """生成结尾段落"""
        templates = self.ending_templates.get(ending_style, self.ending_templates["happy_ending"])
        template = templates[0]
        
        # 根据类型填充
        if "玄幻" in novel_type or "仙侠" in novel_type:
            achievement = "登临巅峰"
            location = "九天之上"
        elif "都市" in novel_type:
            achievement = "商业帝国"
            location = "都市之巅"
        elif "言情" in novel_type:
            achievement = "幸福生活"
            location = "温馨的家"
        else:
            achievement = "最终目标"
            location = "终点"
        
        ending = template.replace("{主角}", "主角")
        ending = ending.replace("{成就}", achievement)
        ending = ending.replace("{地点}", location)
        ending = ending.replace("{目标}", achievement)
        ending = ending.replace("{结果}", "圆满结局")
        ending = ending.replace("{历程}", "漫长旅程")
        ending = ending.replace("{过去}", "走过的路")
        ending = ending.replace("{未来}", "新的征程")
        
        return ending
    
    def check_ending_quality(self, ending_content: str) -> Dict:
        """检查结尾质量"""
        quality_scores = {
            "completeness": self._check_completeness(ending_content),
            "satisfaction": self._check_satisfaction(ending_content),
            "coherence": self._check_coherence(ending_content),
            "emotional_impact": self._check_emotional_impact(ending_content)
        }
        
        total_score = sum(quality_scores.values()) / len(quality_scores)
        
        return {
            "total_score": total_score,
            "scores": quality_scores,
            "grade": self._get_grade(total_score),
            "suggestions": self._get_quality_suggestions(quality_scores)
        }
    
    def _check_completeness(self, content: str) -> float:
        """检查完整性"""
        completeness_keywords = ["最终", "最后", "结局", "从此", "后来"]
        has_completeness = any(kw in content for kw in completeness_keywords)
        return 0.8 if has_completeness else 0.4
    
    def _check_satisfaction(self, content: str) -> float:
        """检查满意度"""
        satisfaction_keywords = ["圆满", "成功", "幸福", "美好", "完美"]
        has_satisfaction = any(kw in content for kw in satisfaction_keywords)
        return 0.8 if has_satisfaction else 0.5
    
    def _check_coherence(self, content: str) -> float:
        """检查连贯性"""
        # 检查是否有逻辑连接词
        coherence_keywords = ["因为", "所以", "虽然", "但是", "然而", "最终"]
        count = sum(1 for kw in coherence_keywords if kw in content)
        return min(1.0, count / 3)
    
    def _check_emotional_impact(self, content: str) -> float:
        """检查情感冲击"""
        emotional_keywords = ["感动", "震撼", "难忘", "深刻", "意义"]
        has_emotional = any(kw in content for kw in emotional_keywords)
        return 0.8 if has_emotional else 0.5
    
    def _get_grade(self, score: float) -> str:
        """获取等级"""
        if score >= 0.8:
            return "优秀"
        elif score >= 0.6:
            return "良好"
        elif score >= 0.4:
            return "一般"
        else:
            return "需改进"
    
    def _get_quality_suggestions(self, scores: Dict) -> List[str]:
        """获取质量建议"""
        suggestions = []
        
        if scores["completeness"] < 0.6:
            suggestions.append("建议增加明确的结局描述")
        
        if scores["satisfaction"] < 0.6:
            suggestions.append("建议增加让读者满意的元素")
        
        if scores["coherence"] < 0.6:
            suggestions.append("建议增加逻辑连接，使结尾更连贯")
        
        if scores["emotional_impact"] < 0.6:
            suggestions.append("建议增加情感冲击，让结尾更有感染力")
        
        return suggestions

    def generate_final_checklist(self, final_chapters: List[Dict], novel_type: str, ending_style: str) -> Dict:
        """输出可勾选的结尾检查表"""
        optimization = self.optimize_ending(final_chapters, novel_type, ending_style)
        quality = self.check_ending_quality(" ".join(ch.get("content", "") for ch in final_chapters))
        checklist = [
            {"item": "主线收束", "status": optimization["main_plot_resolution"]["is_resolved"]},
            {"item": "伏笔回收", "status": optimization["unresolved_foreshadowings"] == 0},
            {"item": "人物结局交代", "status": not optimization["character_resolutions"]["suggestions"]},
            {"item": "情感余韵", "status": quality["scores"]["emotional_impact"] >= 0.6},
            {"item": "语气统一", "status": optimization["tone_alignment"]["score"] >= 0.6}
        ]
        return {
            "checklist": checklist,
            "quality": quality,
            "optimization": optimization
        }

    def _evaluate_subplots(self, final_chapters: List[Dict]) -> Dict:
        """评估支线回收状态"""
        content = " ".join(ch.get("content", "") for ch in final_chapters)
        subplot_keywords = ["支线", "副线", "暗线", "线索"]
        unresolved_markers = ["未解", "悬而未决", "仍然", "依旧"]
        closure_hits = sum(content.count(kw) for kw in subplot_keywords)
        unresolved_hits = sum(content.count(kw) for kw in unresolved_markers)
        score = max(0.0, min(1.0, (closure_hits - unresolved_hits) / max(closure_hits + 1, 1)))
        status = "完整" if score > 0.6 else "部分回收" if score > 0.3 else "待补完"
        return {"score": round(score, 2), "status": status}

    def _check_tone_alignment(self, final_chapters: List[Dict], ending_style: str) -> Dict:
        """确保情绪基调与预期一致"""
        style_markers = {
            "happy_ending": ["温暖", "圆满", "笑", "光明"],
            "open_ending": ["未知", "继续", "延伸", "未来"],
            "tragic_ending": ["泪", "牺牲", "失去", "痛"],
            "circular_ending": ["循环", "回到", "初见", "再现"]
        }
        content = " ".join(ch.get("content", "") for ch in final_chapters)
        markers = style_markers.get(ending_style, [])
        hits = sum(content.count(marker) for marker in markers)
        score = min(1.0, hits / max(len(final_chapters), 1))
        return {"score": round(score, 2), "matches": hits}

