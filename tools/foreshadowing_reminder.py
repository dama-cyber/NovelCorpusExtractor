"""
28_伏笔回收提醒器
提醒未回收的伏笔，避免遗漏
"""

from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta
from ..core.memory_manager import MemoryManager

logger = logging.getLogger(__name__)


class ForeshadowingReminder:
    """伏笔回收提醒器"""
    
    def __init__(self, memory_manager: MemoryManager, max_chapters: int = 55):
        """
        初始化提醒器
        Args:
            memory_manager: 记忆体管理器
            max_chapters: 最大未回收章节数（超过此数提醒）
        """
        self.memory_manager = memory_manager
        self.max_chapters = max_chapters
        self.priority_thresholds = {
            "high": max_chapters,
            "medium": max_chapters // 2,
            "low": max_chapters // 4
        }
    
    def check_unresolved_foreshadowings(self, current_chapter: int) -> List[Dict]:
        """
        检查未回收的伏笔
        Args:
            current_chapter: 当前章节数
        Returns:
            需要提醒的伏笔列表
        """
        foreshadowings = self.memory_manager.load_foreshadowing()
        reminders = []
        
        for f in foreshadowings:
            if f.get("status") == "未回收":
                buried_chapter = self._extract_chapter_number(f.get("埋设章节", ""))
                if buried_chapter:
                    chapters_passed = current_chapter - buried_chapter
                    
                    # 检查是否超过最大章节数
                    if chapters_passed > self.max_chapters:
                        reminders.append(self._build_reminder(f, chapters_passed))
        
        return reminders
    
    def _extract_chapter_number(self, chapter_str: str) -> Optional[int]:
        """从章节字符串中提取章节号"""
        import re
        if not chapter_str:
            return None
        
        # 匹配"第X章"格式
        match = re.search(r'第(\d+)章', chapter_str)
        if match:
            return int(match.group(1))
        
        # 匹配纯数字
        match = re.search(r'\d+', chapter_str)
        if match:
            return int(match.group(0))
        
        return None
    
    def get_reminder_report(self, current_chapter: int) -> str:
        """生成提醒报告"""
        reminders = self.check_unresolved_foreshadowings(current_chapter)
        
        if not reminders:
            return "✅ 所有伏笔都在合理范围内，无需提醒"
        
        report = f"⚠️ 发现 {len(reminders)} 个需要关注的伏笔:\n\n"
        for r in reminders:
            report += f"ID: {r['伏笔ID']}\n"
            report += f"内容: {r['伏笔内容']}\n"
            report += f"埋设章节: {r['埋设章节']}\n"
            report += f"已过章节数: {r['已过章节数']}\n"
            report += f"警告: {r['警告']}\n"
            report += "-" * 50 + "\n"
        
        return report

    def schedule_followups(self, current_chapter: int, window: int = 15) -> List[Dict]:
        """规划未来window章节内即将到期的伏笔"""
        foreshadowings = self.memory_manager.load_foreshadowing()
        upcoming = []
        for f in foreshadowings:
            if f.get("status") != "未回收":
                continue
            buried = self._extract_chapter_number(f.get("埋设章节", ""))
            target = self._extract_chapter_number(f.get("预计回收章节", ""))
            if not buried or not target:
                continue
            if current_chapter <= target <= current_chapter + window:
                upcoming.append({
                    "伏笔ID": f.get("id"),
                    "预计回收章节": target,
                    "剩余章节数": target - current_chapter,
                    "伏笔内容": f.get("伏笔内容", "")
                })
        return sorted(upcoming, key=lambda item: item["剩余章节数"])

    def _build_reminder(self, foreshadowing: Dict, chapters_passed: int) -> Dict:
        """构建提醒条目"""
        priority = self._determine_priority(chapters_passed)
        due = foreshadowing.get("预计回收章节", "")
        due_chapter = self._extract_chapter_number(due) or (chapters_passed + self.max_chapters)
        return {
            "伏笔ID": foreshadowing.get("id"),
            "伏笔内容": foreshadowing.get("伏笔内容", ""),
            "埋设章节": foreshadowing.get("埋设章节", ""),
            "已过章节数": chapters_passed,
            "预计回收章节": due,
            "优先级": priority,
            "超期章节数": chapters_passed - self.max_chapters,
            "建议回收章节": f"第{due_chapter}章",
            "警告": f"伏笔已埋设{chapters_passed}章，超过{self.max_chapters}章未回收"
        }

    def _determine_priority(self, chapters_passed: int) -> str:
        if chapters_passed >= self.priority_thresholds["high"]:
            return "high"
        if chapters_passed >= self.priority_thresholds["medium"]:
            return "medium"
        return "low"

