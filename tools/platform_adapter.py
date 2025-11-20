"""
24_平台算法适配器
适配不同平台的算法规则，优化推荐和曝光
"""

from typing import Dict, List, Optional
from enum import Enum
import logging
from statistics import mean

logger = logging.getLogger(__name__)


class Platform(Enum):
    """平台枚举"""
    QIDIAN = "起点中文网"
    ZONGHENG = "纵横中文网"
    FANQIE = "番茄小说"
    QIDIAN_READ = "起点读书"
    QIMIAO = "奇妙小说网"
    ZHIHU = "知乎"
    JINJIANG = "晋江文学城"


class PlatformAdapter:
    """平台算法适配器"""
    
    def __init__(self):
        self.platform_rules = self._build_platform_rules()
    
    def _build_platform_rules(self) -> Dict[Platform, Dict]:
        """构建平台规则"""
        return {
            Platform.QIDIAN: {
                "update_frequency": "每日更新",
                "chapter_length": (2000, 4000),  # 每章字数
                "keywords": ["爽文", "升级", "打脸", "逆袭"],
                "tags": ["玄幻", "都市", "历史"],
                "title_length": (10, 20),
                "description_length": (100, 300),
                "algorithm_factors": ["点击率", "收藏率", "推荐票", "打赏", "完读率"]
            },
            Platform.ZONGHENG: {
                "update_frequency": "每日更新1-2章",
                "chapter_length": (1800, 3800),
                "keywords": ["江湖", "朝堂", "争霸", "权谋"],
                "tags": ["历史", "奇幻", "武侠"],
                "title_length": (10, 18),
                "description_length": (120, 280),
                "algorithm_factors": ["收藏率", "订阅转化", "推荐位表现"]
            },
            Platform.FANQIE: {
                "update_frequency": "每日更新2-3章",
                "chapter_length": (1500, 3000),
                "keywords": ["系统", "重生", "穿越", "爽文"],
                "tags": ["都市", "玄幻", "历史"],
                "title_length": (8, 18),
                "description_length": (80, 200),
                "algorithm_factors": ["完读率", "停留时长", "互动率", "分享率"]
            },
            Platform.ZHIHU: {
                "update_frequency": "每周更新",
                "chapter_length": (1000, 2500),
                "keywords": ["脑洞", "反转", "悬疑", "推理"],
                "tags": ["悬疑", "推理", "脑洞"],
                "title_length": (5, 15),
                "description_length": (50, 150),
                "algorithm_factors": ["点赞", "评论", "收藏", "分享"]
            },
            Platform.JINJIANG: {
                "update_frequency": "每日更新",
                "chapter_length": (2000, 3500),
                "keywords": ["甜宠", "虐恋", "重生", "穿书"],
                "tags": ["言情", "古言", "现言"],
                "title_length": (8, 20),
                "description_length": (100, 250),
                "algorithm_factors": ["收藏", "评论", "营养液", "地雷"]
            },
            Platform.QIDIAN_READ: {
                "update_frequency": "每日更新+活动加更",
                "chapter_length": (2200, 4200),
                "keywords": ["燃爆", "联盟", "军团", "天才"],
                "tags": ["玄幻", "科幻", "电竞"],
                "title_length": (10, 20),
                "description_length": (120, 260),
                "algorithm_factors": ["点击率", "完读率", "分享率", "互动率"]
            },
            Platform.QIMIAO: {
                "update_frequency": "每日更新2章",
                "chapter_length": (1600, 3000),
                "keywords": ["脑洞", "反套路", "设定党"],
                "tags": ["科幻", "轻小说", "群像"],
                "title_length": (8, 18),
                "description_length": (80, 220),
                "algorithm_factors": ["互动率", "分享率", "完读率"]
            }
        }
    
    def adapt_for_platform(self, content: Dict, platform: Platform) -> Dict:
        """
        适配平台规则
        Args:
            content: 内容字典（包含title, description, chapters等）
            platform: 目标平台
        """
        rules = self.platform_rules.get(platform, {})
        
        adapted = {
            "title": self._adapt_title(content.get("title", ""), rules),
            "description": self._adapt_description(content.get("description", ""), rules),
            "chapters": self._adapt_chapters(content.get("chapters", []), rules),
            "tags": self._suggest_tags(content.get("novel_type", ""), rules),
            "update_schedule": self._suggest_update_schedule(rules),
            "optimization_suggestions": self._generate_optimization_suggestions(content, rules)
        }
        
        return adapted
    
    def score_against_rules(self, content: Dict, platform: Platform) -> Dict:
        """打分：当前内容距平台标准的匹配度"""
        rules = self.platform_rules.get(platform, {})
        title_len = len(content.get("title", ""))
        desc_len = len(content.get("description", ""))
        chapter_samples = content.get("chapters", [])[:3]
        chapter_lengths = [len(ch.get("content", "")) for ch in chapter_samples] or [0]
        title_score = self._score_length(title_len, rules.get("title_length", (10, 20)))
        desc_score = self._score_length(desc_len, rules.get("description_length", (100, 300)))
        chapter_score = mean(self._score_length(length, rules.get("chapter_length", (2000, 4000)))
                             for length in chapter_lengths)
        keyword_score = self._score_keywords(content.get("title", ""), rules.get("keywords", []))
        overall = round(mean([title_score, desc_score, chapter_score, keyword_score]), 2)
        return {
            "platform": platform.value,
            "overall_score": overall,
            "title_score": round(title_score, 2),
            "description_score": round(desc_score, 2),
            "chapter_score": round(chapter_score, 2),
            "keyword_score": round(keyword_score, 2)
        }

    def benchmark_content(self, content: Dict, platforms: Optional[List[Platform]] = None) -> List[Dict]:
        """跨平台比较适配度"""
        targets = platforms or list(self.platform_rules.keys())
        scores = [self.score_against_rules(content, platform) for platform in targets]
        return sorted(scores, key=lambda item: item["overall_score"], reverse=True)
    
    def _adapt_title(self, title: str, rules: Dict) -> str:
        """适配标题"""
        # 检查长度
        min_len, max_len = rules.get("title_length", (10, 20))
        
        if len(title) < min_len:
            # 添加关键词
            keywords = rules.get("keywords", [])
            if keywords:
                title += f"：{keywords[0]}"
        elif len(title) > max_len:
            # 缩短标题
            title = title[:max_len-2] + "..."
        
        return title
    
    def _adapt_description(self, description: str, rules: Dict) -> str:
        """适配简介"""
        min_len, max_len = rules.get("description_length", (100, 300))
        
        if len(description) < min_len:
            # 补充内容
            keywords = rules.get("keywords", [])
            if keywords:
                description += f"关键词：{', '.join(keywords[:3])}"
        elif len(description) > max_len:
            # 缩短简介
            description = description[:max_len-3] + "..."
        
        return description
    
    def _adapt_chapters(self, chapters: List[Dict], rules: Dict) -> List[Dict]:
        """适配章节"""
        min_len, max_len = rules.get("chapter_length", (2000, 4000))
        adapted = []
        
        for chapter in chapters:
            content = chapter.get("content", "")
            content_len = len(content)
            
            if content_len < min_len:
                # 章节太短，建议补充
                chapter["warning"] = f"章节过短（{content_len}字），建议至少{min_len}字"
            elif content_len > max_len:
                # 章节太长，建议拆分
                chapter["warning"] = f"章节过长（{content_len}字），建议拆分或压缩到{max_len}字以内"
            
            adapted.append(chapter)
        
        return adapted
    
    def _suggest_tags(self, novel_type: str, rules: Dict) -> List[str]:
        """建议标签"""
        platform_tags = rules.get("tags", [])
        
        # 如果类型匹配平台标签，优先使用
        if novel_type in platform_tags:
            return [novel_type] + platform_tags[:2]
        else:
            return platform_tags[:3]
    
    def _suggest_update_schedule(self, rules: Dict) -> Dict:
        """建议更新计划"""
        frequency = rules.get("update_frequency", "每日更新")
        
        return {
            "frequency": frequency,
            "suggested_times": ["09:00", "18:00", "21:00"],  # 推荐更新时间
            "optimal_days": ["周一", "周三", "周五", "周日"]  # 最佳更新日
        }
    
    def _generate_optimization_suggestions(self, content: Dict, rules: Dict) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        algorithm_factors = rules.get("algorithm_factors", [])
        
        if "完读率" in algorithm_factors:
            suggestions.append("提升完读率：确保每章都有吸引点，章节结尾设置悬念")
        
        if "互动率" in algorithm_factors:
            suggestions.append("提升互动率：在章节末尾设置讨论话题，引导读者评论")
        
        if "推荐票" in algorithm_factors:
            suggestions.append("提升推荐票：在关键章节提醒读者投票")
        
        if "打赏" in algorithm_factors:
            suggestions.append("提升打赏：在精彩情节后设置打赏提醒")
        
        return suggestions

    def _score_length(self, value: int, bounds: tuple) -> float:
        """根据目标区间计算分数"""
        min_len, max_len = bounds
        if min_len <= value <= max_len:
            return 0.95
        delta = min(abs(value - min_len), abs(value - max_len))
        penalty = min(0.7, delta / max_len)
        return max(0.2, 0.95 - penalty)

    def _score_keywords(self, title: str, keywords: List[str]) -> float:
        if not keywords:
            return 0.6
        hits = sum(1 for kw in keywords if kw in title)
        return min(1.0, 0.4 + hits * 0.2)
    
    def get_platform_recommendations(self, platform: Platform) -> Dict:
        """获取平台推荐策略"""
        rules = self.platform_rules.get(platform, {})
        
        return {
            "platform": platform.value,
            "algorithm_factors": rules.get("algorithm_factors", []),
            "optimization_tips": self._get_optimization_tips(platform),
            "best_practices": self._get_best_practices(platform)
        }
    
    def _get_optimization_tips(self, platform: Platform) -> List[str]:
        """获取优化技巧"""
        tips_map = {
            Platform.QIDIAN: [
                "保持稳定更新，每日至少1章",
                "关注推荐票和收藏数据",
                "在关键情节设置打赏点",
                "积极参与平台活动"
            ],
            Platform.FANQIE: [
                "提升完读率是关键",
                "章节长度控制在2000-3000字",
                "标题要有吸引力",
                "利用完读率数据优化内容"
            ],
            Platform.ZHIHU: [
                "内容要有深度和反转",
                "标题要引发好奇心",
                "积极回复评论",
                "利用知乎的推荐机制"
            ],
            Platform.JINJIANG: [
                "关注收藏和评论数据",
                "标签要准确",
                "保持稳定更新",
                "与读者互动"
            ]
        }
        
        return tips_map.get(platform, [])
    
    def _get_best_practices(self, platform: Platform) -> List[str]:
        """获取最佳实践"""
        practices_map = {
            Platform.QIDIAN: [
                "开篇要有冲击力",
                "保持爽点密集",
                "定期爆发更新",
                "关注读者反馈"
            ],
            Platform.FANQIE: [
                "前3章要有爽点",
                "控制章节长度",
                "标题要吸引眼球",
                "完读率是核心指标"
            ],
            Platform.ZHIHU: [
                "内容要有新意",
                "标题要有悬念",
                "保持更新频率",
                "与读者互动"
            ],
            Platform.JINJIANG: [
                "情感线要清晰",
                "人物塑造要立体",
                "保持稳定更新",
                "关注读者评论"
            ]
        }
        
        return practices_map.get(platform, [])

