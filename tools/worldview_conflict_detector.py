"""
27_世界观冲突检测器
检测世界观设定中的冲突和不一致
"""

from typing import Dict, List
import logging
from ..core.memory_manager import MemoryManager

logger = logging.getLogger(__name__)


class WorldviewConflictDetector:
    """世界观冲突检测器"""
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager
    
    def detect_conflicts(self, new_worldview: Dict, detailed: bool = False) -> List:
        """
        检测世界观冲突
        Returns:
            冲突列表
        """
        conflicts = []
        current = self.memory_manager.load_worldview()
        
        # 检查力量体系冲突
        if "力量体系" in current and "力量体系" in new_worldview:
            conflicts.extend(self._check_power_system_conflicts(
                current["力量体系"], new_worldview["力量体系"]
            ))
        
        # 检查地理设定冲突
        if "地理设定" in current and "地理设定" in new_worldview:
            conflicts.extend(self._check_geography_conflicts(
                current["地理设定"], new_worldview["地理设定"]
            ))
        
        # 检查势力设定冲突
        if "势力设定" in current and "势力设定" in new_worldview:
            conflicts.extend(self._check_faction_conflicts(
                current["势力设定"], new_worldview["势力设定"]
            ))
        
        if detailed:
            return conflicts
        return [conflict["message"] for conflict in conflicts]
    
    def _check_power_system_conflicts(self, current: Dict, new_data: Dict) -> List[str]:
        """检查力量体系冲突"""
        conflicts = []
        
        if "等级划分" in current and "等级划分" in new_data:
            current_levels = current["等级划分"]
            new_levels = new_data["等级划分"]
            
            # 检查等级数量是否一致
            if len(current_levels) != len(new_levels):
                conflicts.append(f"等级数量不一致: {len(current_levels)} vs {len(new_levels)}")
            
            # 检查等级名称是否一致
            for i, (curr, new) in enumerate(zip(current_levels, new_levels)):
                if isinstance(curr, dict) and isinstance(new, dict):
                    if curr.get("名称") != new.get("名称"):
                        conflicts.append(f"第{i+1}级名称不一致: {curr.get('名称')} vs {new.get('名称')}")
        
        return conflicts
    
    def _check_geography_conflicts(self, current: Dict, new_data: Dict) -> List[str]:
        """检查地理设定冲突"""
        conflicts = []
        current_regions = {region.get("名称"): region for region in current.get("区域", [])}
        for region in new_data.get("区域", []):
            name = region.get("名称")
            if name in current_regions:
                curr = current_regions[name]
                if curr.get("气候") != region.get("气候"):
                    conflicts.append(self._build_conflict(
                        "地理设定", f"{name}气候不一致：{curr.get('气候')} vs {region.get('气候')}", "medium"))
                if curr.get("资源") and region.get("资源"):
                    diff = set(curr["资源"]) ^ set(region["资源"])
                    if diff:
                        conflicts.append(self._build_conflict(
                            "地理设定", f"{name}资源设定不一致：{diff}", "low"))
        return conflicts
    
    def _check_faction_conflicts(self, current: Dict, new_data: Dict) -> List[str]:
        """检查势力设定冲突"""
        conflicts = []
        current_factions = {f.get("名称"): f for f in current.get("势力列表", [])}
        for faction in new_data.get("势力列表", []):
            name = faction.get("名称")
            if name in current_factions:
                curr = current_factions[name]
                if curr.get("阵营") != faction.get("阵营"):
                    conflicts.append(self._build_conflict(
                        "势力设定", f"{name}阵营变化：{curr.get('阵营')} -> {faction.get('阵营')}", "high"))
                overlap = set(curr.get("盟友", [])) ^ set(faction.get("盟友", []))
                if overlap:
                    conflicts.append(self._build_conflict(
                        "势力关系", f"{name}盟友列表不一致：{overlap}", "medium"))
        return conflicts

    def generate_conflict_report(self, new_worldview: Dict) -> Dict:
        """生成带优先级的冲突报告"""
        detailed_conflicts = self.detect_conflicts(new_worldview, detailed=True)
        severity_map = {"high": 3, "medium": 2, "low": 1}
        total_score = sum(severity_map.get(conf["severity"], 1) for conf in detailed_conflicts)
        risk_level = "low"
        if total_score >= 9:
            risk_level = "high"
        elif total_score >= 5:
            risk_level = "medium"
        return {
            "conflict_count": len(detailed_conflicts),
            "risk_level": risk_level,
            "conflicts": detailed_conflicts,
            "suggestions": self._build_resolution_suggestions(detailed_conflicts)
        }

    def _build_conflict(self, field: str, message: str, severity: str) -> Dict:
        return {"field": field, "message": message, "severity": severity}

    def _build_resolution_suggestions(self, conflicts: List[Dict]) -> List[str]:
        suggestions = []
        for conflict in conflicts:
            if conflict["field"] == "力量体系":
                suggestions.append("统一力量等级表，补充跨度差异的设定缘由")
            elif conflict["field"] == "势力设定":
                suggestions.append("绘制势力关系图，确认阵营转变是否合理")
            elif conflict["field"] == "地理设定":
                suggestions.append("在设定手册中补充环境变动或时代差异说明")
        return list(dict.fromkeys(suggestions))

