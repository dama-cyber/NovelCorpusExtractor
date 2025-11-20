"""
23_商业化优化器
优化内容以提升商业价值（点击率、完读率、付费转化等）
"""

from typing import Dict, List, Optional, Union
import logging
from statistics import mean

logger = logging.getLogger(__name__)


class CommercialOptimizer:
    """商业化优化器"""
    
    def __init__(self):
        self.optimization_rules = self._build_rules()
    
    def _build_rules(self) -> Dict:
        """构建优化规则"""
        return {
            "title_optimization": {
                "keywords": ["重生", "系统", "逆袭", "打脸", "爽文", "无敌"],
                "length": (10, 20),  # 标题长度范围
                "patterns": ["{主角}的{能力}", "{类型}：{卖点}", "{冲突}的{结果}"]
            },
            "hook_optimization": {
                "first_sentence": "第一句话要有冲击力",
                "first_paragraph": "第一段要有悬念或冲突",
                "first_chapter": "第一章要有爽点或转折"
            },
            "retention_optimization": {
                "chapter_endings": "章节结尾要有悬念",
                "cliffhangers": "每3-5章要有小高潮",
                "plot_hooks": "每10章要有大转折"
            },
            "monetization_optimization": {
                "vip_chapters": "关键情节放在VIP章节",
                "preview_content": "免费章节要有足够吸引力",
                "paywall_timing": "在读者投入最深时设置付费点"
            }
        }
    
    def optimize_title(self, title: str, novel_type: str = "通用",
                      return_details: bool = False) -> Union[List[str], Dict]:
        """
        优化标题
        Returns:
            优化后的标题候选列表
        """
        suggestions = []
        
        # 检查长度
        if len(title) < 10:
            suggestions.append(f"{title}：{novel_type}逆袭之路")
        elif len(title) > 20:
            # 缩短标题
            words = title[:20]
            suggestions.append(words + "...")
        
        # 添加热门关键词
        keywords = self.optimization_rules["title_optimization"]["keywords"]
        for keyword in keywords[:3]:
            if keyword not in title:
                suggestions.append(f"{title}（{keyword}）")
        
        score = self._score_title(title, novel_type)
        result = {
            "candidates": suggestions if suggestions else [title],
            "score": score,
            "diagnostics": {
                "length": len(title),
                "keyword_hits": sum(1 for kw in keywords if kw in title)
            }
        }
        return result if return_details else result["candidates"]
    
    def optimize_hook(self, first_chapter: str, benchmark: Optional[Dict] = None) -> Dict:
        """优化开篇钩子"""
        analysis = {
            "first_sentence_impact": self._check_first_sentence(first_chapter),
            "first_paragraph_hook": self._check_first_paragraph(first_chapter),
            "first_chapter_satisfaction": self._check_first_chapter(first_chapter),
            "suggestions": []
        }
        
        if benchmark:
            analysis["benchmark_gap"] = {
                "first_sentence_impact": round(analysis["first_sentence_impact"] - benchmark.get("first_sentence_impact", 0.7), 2),
                "first_paragraph_hook": round(analysis["first_paragraph_hook"] - benchmark.get("first_paragraph_hook", 0.65), 2),
                "first_chapter_satisfaction": round(analysis["first_chapter_satisfaction"] - benchmark.get("first_chapter_satisfaction", 0.65), 2)
            }
        
        if analysis["first_sentence_impact"] < 0.5:
            analysis["suggestions"].append("第一句话需要更有冲击力，建议加入冲突或悬念")
        
        if analysis["first_paragraph_hook"] < 0.5:
            analysis["suggestions"].append("第一段需要更强的钩子，建议加入冲突或转折")
        
        if analysis["first_chapter_satisfaction"] < 0.5:
            analysis["suggestions"].append("第一章需要至少一个爽点或转折，提升读者满意度")
        
        analysis["retention_score"] = self._score_retention(analysis)
        return analysis
    
    def optimize_retention(self, chapters: List[Dict]) -> Dict:
        """优化留存率"""
        analysis = {
            "chapter_endings": [],
            "cliffhanger_frequency": 0,
            "plot_hook_frequency": 0,
            "suggestions": []
        }
        
        for i, chapter in enumerate(chapters):
            content = chapter.get("content", "")
            chapter_num = i + 1
            
            # 检查章节结尾
            ending_quality = self._check_chapter_ending(content)
            analysis["chapter_endings"].append({
                "chapter": chapter_num,
                "quality": ending_quality
            })
            
            if ending_quality < 0.5:
                analysis["suggestions"].append(f"第{chapter_num}章结尾需要增加悬念")
            
            # 检查小高潮（每3-5章）
            if chapter_num % 4 == 0:
                if self._check_climax(content) < 0.5:
                    analysis["suggestions"].append(f"第{chapter_num}章建议增加小高潮")
                else:
                    analysis["cliffhanger_frequency"] += 1
            
            # 检查大转折（每10章）
            if chapter_num % 10 == 0:
                if self._check_plot_twist(content) < 0.5:
                    analysis["suggestions"].append(f"第{chapter_num}章建议增加大转折")
                else:
                    analysis["plot_hook_frequency"] += 1
        
        return analysis
    
    def suggest_monetization_points(self, chapters: List[Dict], 
                                   total_chapters: int = 100) -> List[int]:
        """建议付费点位置"""
        # 付费点通常在：
        # 1. 关键情节转折（第10、20、30...章）
        # 2. 读者投入最深时（第15、25、35...章）
        # 3. 高潮前（第9、19、29...章）
        
        paywall_points = []
        
        for i in range(10, total_chapters, 10):
            # 高潮前
            paywall_points.append(i - 1)
            # 关键转折
            paywall_points.append(i)
            # 投入最深时
            paywall_points.append(i + 5)
        
        return sorted(list(set(paywall_points)))[:10]  # 返回前10个
    
    def assess_commercial_potential(self, book_profile: Dict) -> Dict:
        """综合评估商业化潜力"""
        title_score = self._score_title(book_profile.get("title", ""), book_profile.get("novel_type", "通用"))
        hook_info = self.optimize_hook(book_profile.get("first_chapter", ""))
        retention_info = self.optimize_retention(book_profile.get("chapters", []))
        monetization_points = self.suggest_monetization_points(
            book_profile.get("chapters", []),
            total_chapters=book_profile.get("total_chapters", 100)
        )
        
        overall = round(mean([
            title_score,
            hook_info["first_sentence_impact"],
            retention_info["retention_score"]
        ]), 2)
        
        return {
            "overall_score": overall,
            "title_score": title_score,
            "hook_analysis": hook_info,
            "retention_analysis": retention_info,
            "recommended_monetization_points": monetization_points[:5]
        }
    
    def _check_first_sentence(self, text: str) -> float:
        """检查第一句话的冲击力"""
        first_sentence = text.split('。')[0] if '。' in text else text[:50]
        
        # 检查是否包含冲突、悬念、转折等关键词
        impact_keywords = ["突然", "没想到", "竟然", "居然", "然而", "但是", "可是"]
        has_impact = any(keyword in first_sentence for keyword in impact_keywords)
        
        return 0.8 if has_impact else 0.3
    
    def _check_first_paragraph(self, text: str) -> float:
        """检查第一段的钩子"""
        first_paragraph = text.split('\n')[0] if '\n' in text else text[:200]
        
        # 检查是否包含冲突、悬念
        hook_keywords = ["冲突", "危机", "转折", "秘密", "真相", "谜团"]
        has_hook = any(keyword in first_paragraph for keyword in hook_keywords)
        
        return 0.8 if has_hook else 0.3
    
    def _check_first_chapter(self, text: str) -> float:
        """检查第一章的满意度"""
        # 检查是否包含爽点
        satisfaction_keywords = ["打脸", "逆袭", "成功", "胜利", "获得", "突破"]
        has_satisfaction = any(keyword in text for keyword in satisfaction_keywords)
        
        return 0.8 if has_satisfaction else 0.3
    
    def _check_chapter_ending(self, content: str) -> float:
        """检查章节结尾质量"""
        # 检查最后一段是否有悬念
        last_paragraph = content.split('\n')[-1] if '\n' in content else content[-100:]
        
        suspense_keywords = ["突然", "没想到", "竟然", "然而", "但是", "？"]
        has_suspense = any(keyword in last_paragraph for keyword in suspense_keywords)
        
        return 0.8 if has_suspense else 0.3
    
    def _check_climax(self, content: str) -> float:
        """检查是否有高潮"""
        climax_keywords = ["高潮", "爆发", "对决", "决战", "关键时刻"]
        has_climax = any(keyword in content for keyword in climax_keywords)
        
        return 0.8 if has_climax else 0.3
    
    def _check_plot_twist(self, content: str) -> float:
        """检查是否有转折"""
        twist_keywords = ["转折", "反转", "真相", "秘密", "揭露", "发现"]
        has_twist = any(keyword in content for keyword in twist_keywords)
        
        return 0.8 if has_twist else 0.3

    def _score_title(self, title: str, novel_type: str) -> float:
        """根据类型趋势对标题打分"""
        if not title:
            return 0.2
        trend_keywords = {
            "玄幻": ["神", "帝", "圣", "龙", "剑"],
            "都市": ["总裁", "豪门", "首富", "逆袭"],
            "言情": ["宠", "婚", "甜", "心", "蜜"],
            "通用": self.optimization_rules["title_optimization"]["keywords"]
        }
        bucket = trend_keywords.get(novel_type, trend_keywords["通用"])
        hits = sum(1 for kw in bucket if kw in title)
        length = len(title)
        length_score = 0.9 if 10 <= length <= 18 else 0.7 if 8 <= length <= 22 else 0.4
        keyword_score = min(1.0, 0.3 + hits * 0.2)
        return round((length_score + keyword_score) / 2, 2)

    def _score_retention(self, analysis: Dict) -> float:
        """根据留存分析打分"""
        endings = [ending["quality"] for ending in analysis["chapter_endings"]] or [0.3]
        base = mean(endings)
        cliff_ratio = analysis["cliffhanger_frequency"] / max(len(endings) / 4, 1)
        plot_ratio = analysis["plot_hook_frequency"] / max(len(endings) / 10, 1)
        return round(min(1.0, base + cliff_ratio * 0.2 + plot_ratio * 0.2), 2)

