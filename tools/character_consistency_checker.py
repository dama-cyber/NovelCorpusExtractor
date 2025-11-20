"""
26_人物一致性检查器
检查人物性格、语言风格、行为模式的一致性
"""

from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import logging
from ..core.memory_manager import MemoryManager

logger = logging.getLogger(__name__)


@dataclass
class ConsistencyIssue:
    field: str
    message: str
    severity: str = "medium"
    reference: Optional[str] = None


class CharacterConsistencyChecker:
    """人物一致性检查器"""
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager
        self.severity_map = {
            "MBTI类型": "high",
            "核心性格": "high",
            "语言镜头": "medium",
            "口头禅": "low",
            "行为准则": "medium",
            "成长轨迹": "medium",
            "人际关系": "medium"
        }
    
    def check_character(self, character_name: str, new_behavior: Dict,
                        detailed: bool = False) -> Union[List[str], List[ConsistencyIssue]]:
        """
        检查人物行为一致性
        Returns:
            不一致问题列表
        """
        issues: List[ConsistencyIssue] = []
        characters = self.memory_manager.load_characters()
        
        if character_name not in characters:
            return [] if not detailed else issues
        
        char_data = characters[character_name]
        
        issues.extend(self._check_mbti(char_data, new_behavior))
        issues.extend(self._check_language_style(char_data, new_behavior))
        issues.extend(self._check_core_traits(char_data, new_behavior))
        issues.extend(self._check_relationships(char_data, new_behavior))
        issues.extend(self._check_growth_timeline(char_data, new_behavior))
        
        if detailed:
            return issues
        return [issue.message for issue in issues]
    
    def check_all_characters(self) -> Dict[str, List[str]]:
        """检查所有人物的一致性"""
        characters = self.memory_manager.load_characters()
        all_issues = {}
        
        for char_name in characters:
            issues = self.check_character(char_name, {}, detailed=True)
            if issues:
                all_issues[char_name] = [issue.message for issue in issues]
        
        return all_issues

    def generate_consistency_report(self, character_name: str, new_behavior: Dict) -> Dict:
        """生成详细一致性报告"""
        detailed_issues = self.check_character(character_name, new_behavior, detailed=True)
        if not detailed_issues:
            return {"character": character_name, "status": "一致", "issues": [], "risk_level": "low"}
        
        risk_score = sum(3 if issue.severity == "high" else 2 if issue.severity == "medium" else 1
                         for issue in detailed_issues)
        risk_level = "high" if risk_score >= 6 else "medium" if risk_score >= 3 else "low"
        
        return {
            "character": character_name,
            "status": "存在不一致",
            "issues": [issue.__dict__ for issue in detailed_issues],
            "risk_level": risk_level,
            "suggestions": self._build_suggestions(detailed_issues)
        }

    def _check_mbti(self, baseline: Dict, new_data: Dict) -> List[ConsistencyIssue]:
        issues = []
        if "MBTI类型" in baseline and "MBTI类型" in new_data and baseline["MBTI类型"] != new_data["MBTI类型"]:
            issues.append(self._make_issue("MBTI类型",
                                           f"MBTI类型不一致: {baseline['MBTI类型']} vs {new_data['MBTI类型']}",
                                           "MBTI类型"))
        return issues

    def _check_language_style(self, baseline: Dict, new_data: Dict) -> List[ConsistencyIssue]:
        issues = []
        baseline_style = baseline.get("语言镜头", {})
        new_style = new_data.get("语言镜头", {})
        tracked_fields = ["口头禅", "语速", "语气", "惯用句式"]
        for field in tracked_fields:
            if field in baseline_style and field in new_style and baseline_style[field] != new_style[field]:
                issues.append(self._make_issue("语言镜头", f"{field}不一致", field))
        return issues

    def _check_core_traits(self, baseline: Dict, new_data: Dict) -> List[ConsistencyIssue]:
        issues = []
        for field in ["核心性格", "行为准则", "底线"]:
            if field in baseline and field in new_data and baseline[field] != new_data[field]:
                issues.append(self._make_issue("核心性格", f"{field}描述不一致", field))
        return issues

    def _check_relationships(self, baseline: Dict, new_data: Dict) -> List[ConsistencyIssue]:
        issues = []
        baseline_rel = baseline.get("人际关系", {})
        new_rel = new_data.get("人际关系", {})
        for person, relation in new_rel.items():
            if person in baseline_rel and baseline_rel[person] != relation:
                issues.append(self._make_issue("人际关系",
                                               f"与{person}的关系变化：{baseline_rel[person]} -> {relation}",
                                               person))
        return issues

    def _check_growth_timeline(self, baseline: Dict, new_data: Dict) -> List[ConsistencyIssue]:
        issues = []
        baseline_arc = baseline.get("成长轨迹")
        new_arc = new_data.get("成长轨迹")
        if baseline_arc and new_arc and baseline_arc.get("阶段") and new_arc.get("阶段"):
            if abs(baseline_arc["阶段"] - new_arc["阶段"]) > 1:
                issues.append(self._make_issue("成长轨迹",
                                               f"成长阶段跳跃：{baseline_arc['阶段']} -> {new_arc['阶段']}",
                                               "成长阶段"))
        return issues

    def _make_issue(self, field: str, message: str, reference: Optional[str] = None) -> ConsistencyIssue:
        severity = self.severity_map.get(field, "medium")
        return ConsistencyIssue(field=field, message=message, severity=severity, reference=reference)

    def _build_suggestions(self, issues: List[ConsistencyIssue]) -> List[str]:
        suggestions = []
        for issue in issues:
            if issue.field == "MBTI类型":
                suggestions.append("回顾人物设定稿，确认性格维度是否发生重大变化")
            elif issue.field == "语言镜头":
                suggestions.append("检查人物对话样例，保持语言节奏与口头禅统一")
            elif issue.field == "核心性格":
                suggestions.append("梳理人物成长弧光，明确此处性格变化的动因")
            elif issue.field == "人际关系":
                suggestions.append("补写关系转折桥段，给读者合理解释")
        return list(dict.fromkeys(suggestions))

