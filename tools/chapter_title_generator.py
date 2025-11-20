"""
29_章节标题生成器
生成吸引人的章节标题
"""

from typing import Dict, List, Optional, Union
from collections import Counter
import logging
import re

logger = logging.getLogger(__name__)


class ChapterTitleGenerator:
    """章节标题生成器"""
    
    def __init__(self):
        self.title_templates = self._build_templates()
        self.hook_phrases = self._build_hook_phrases()
        self.tone_modifiers = self._build_tone_modifiers()
        self.style_weights = self._build_style_weights()
    
    def _build_templates(self) -> Dict[str, List[str]]:
        """构建标题模板"""
        return {
            "action": [
                "{主角}的{行动}",
                "{行动}！{结果}",
                "第{数字}章：{行动}",
                "{地点}的{事件}"
            ],
            "conflict": [
                "{主角}vs{对手}",
                "{冲突}的{结果}",
                "第{数字}章：{冲突}",
                "{危机}来临"
            ],
            "mystery": [
                "{秘密}的{真相}",
                "{谜团}揭晓",
                "第{数字}章：{疑问}？",
                "{发现}的{影响}"
            ],
            "emotion": [
                "{情感}的{时刻}",
                "{关系}的{变化}",
                "第{数字}章：{情感}",
                "{情感}与{情感}"
            ],
            "achievement": [
                "{主角}的{成就}",
                "{突破}！{影响}",
                "第{数字}章：{成就}",
                "{成功}的{代价}"
            ]
        }
    
    def _build_hook_phrases(self) -> List[str]:
        """构建钩子短语"""
        return [
            "没想到", "竟然", "居然", "突然", "意外",
            "真相", "秘密", "谜团", "发现", "揭露",
            "危机", "危险", "挑战", "对决", "决战",
            "转折", "反转", "变化", "突破", "觉醒"
        ]
    
    def _build_tone_modifiers(self) -> Dict[str, Dict[str, str]]:
        """不同语调下的词汇替换"""
        return {
            "爽文": {"事件": "逆袭", "情感": "燃", "成就": "碾压"},
            "悬疑": {"事件": "疑案", "情感": "诡异", "成就": "真相"},
            "言情": {"事件": "心动", "情感": "怦然", "成就": "携手"},
            "古风": {"事件": "风云", "情感": "柔情", "成就": "封侯"},
            "科幻": {"事件": "异象", "情感": "未知", "成就": "突破"},
        }

    def _build_style_weights(self) -> Dict[str, Dict[str, int]]:
        """不同风格的权重配置"""
        return {
            "action": {"main_action": 3, "conflict": 2, "achievement": 1},
            "conflict": {"conflict": 3, "main_action": 1},
            "mystery": {"mystery": 3, "key_phrases": 2},
            "emotion": {"emotion": 3, "key_phrases": 1},
            "achievement": {"achievement": 3, "main_action": 1},
        }

    def generate_title(self, chapter_content: str, chapter_number: int = 1,
                      style: str = "auto", tone: Optional[str] = None,
                      return_details: bool = False) -> Union[List[str], Dict]:
        """
        生成章节标题
        Args:
            chapter_content: 章节内容
            chapter_number: 章节号
            style: 标题风格（action/conflict/mystery/emotion/achievement/auto）
        """
        # 分析章节内容
        content_analysis = self._analyze_content(chapter_content)
        
        # 自动选择风格
        if style == "auto":
            style = self._detect_style(content_analysis)
        
        # 生成标题候选
        titles = []
        
        # 使用模板生成
        templates = self.title_templates.get(style, self.title_templates["action"])
        for template in templates[:3]:
            title = self._fill_template(template, content_analysis, chapter_number)
            if title:
                titles.append(title)
        
        # 使用钩子短语生成
        hook_titles = self._generate_hook_titles(content_analysis, chapter_number)
        titles.extend(hook_titles)
        
        # 去重、应用语气并限制数量
        toned_titles = []
        for title in titles:
            toned_titles.append(self._apply_tone_modifier(title, tone, content_analysis["tone_signals"]))
        titles = list(dict.fromkeys(filter(None, toned_titles)))[:5]
        
        result = {
            "titles": titles,
            "style": style,
            "analysis": content_analysis,
            "diagnostics": self._build_diagnostics(titles, content_analysis, tone)
        }

        return result if return_details else titles
    
    def _analyze_content(self, content: str) -> Dict:
        """分析章节内容"""
        # 提取关键信息
        protagonist = self._extract_protagonist(content)
        analysis = {
            "main_action": self._extract_main_action(content),
            "conflict": self._extract_conflict(content),
            "mystery": self._extract_mystery(content),
            "emotion": self._extract_emotion(content),
            "achievement": self._extract_achievement(content),
            "key_phrases": self._extract_key_phrases(content),
            "protagonist": protagonist or "主角",
            "tone_signals": self._detect_tone_signals(content)
        }
        
        return analysis
    
    def _extract_main_action(self, content: str) -> str:
        """提取主要行动"""
        action_keywords = ["战斗", "修炼", "突破", "获得", "发现", "前往", "挑战"]
        for keyword in action_keywords:
            if keyword in content[:500]:  # 只看前500字
                return keyword
        return "行动"
    
    def _extract_conflict(self, content: str) -> str:
        """提取冲突"""
        conflict_keywords = ["对决", "战斗", "冲突", "对抗", "挑战", "危机"]
        for keyword in conflict_keywords:
            if keyword in content:
                return keyword
        return ""
    
    def _extract_mystery(self, content: str) -> str:
        """提取谜团"""
        mystery_keywords = ["秘密", "真相", "谜团", "发现", "揭露", "疑问"]
        for keyword in mystery_keywords:
            if keyword in content:
                return keyword
        return ""
    
    def _extract_emotion(self, content: str) -> str:
        """提取情感"""
        emotion_keywords = ["愤怒", "悲伤", "喜悦", "震惊", "感动", "心动"]
        for keyword in emotion_keywords:
            if keyword in content:
                return keyword
        return ""
    
    def _extract_achievement(self, content: str) -> str:
        """提取成就"""
        achievement_keywords = ["突破", "成功", "获得", "胜利", "完成", "觉醒"]
        for keyword in achievement_keywords:
            if keyword in content:
                return keyword
        return ""
    
    def _extract_key_phrases(self, content: str) -> List[str]:
        """提取关键短语"""
        phrases = []
        
        # 查找包含钩子短语的句子
        sentences = re.split(r'[。！？]', content)
        for sentence in sentences[:5]:  # 只看前5句
            for hook in self.hook_phrases:
                if hook in sentence:
                    # 提取包含钩子短语的短句
                    start = sentence.find(hook)
                    phrase = sentence[max(0, start-5):start+10]
                    if phrase.strip():
                        phrases.append(phrase.strip())
                    break
        
        return phrases[:3]
    
    def _detect_style(self, analysis: Dict) -> str:
        """检测章节风格"""
        scores = {}
        for style, weight_map in self.style_weights.items():
            score = 0
            for key, weight in weight_map.items():
                if analysis.get(key):
                    score += weight
            scores[style] = score

        best_style = max(scores.items(), key=lambda x: x[1])[0]
        return best_style if scores[best_style] > 0 else "action"
    
    def _fill_template(self, template: str, analysis: Dict, chapter_number: int) -> str:
        """填充模板"""
        title = template
        
        # 替换占位符
        title = title.replace("{数字}", str(chapter_number))
        title = title.replace("{主角}", analysis.get("protagonist", "主角"))
        title = title.replace("{行动}", analysis["main_action"])
        title = title.replace("{冲突}", analysis["conflict"] or "冲突")
        title = title.replace("{秘密}", analysis["mystery"] or "秘密")
        title = title.replace("{情感}", analysis["emotion"] or "情感")
        title = title.replace("{成就}", analysis["achievement"] or "成就")
        
        # 简化处理其他占位符
        title = re.sub(r'\{[^}]+\}', "事件", title)
        return title if title != template else None
    
    def _generate_hook_titles(self, analysis: Dict, chapter_number: int) -> List[str]:
        """生成钩子标题"""
        titles = []
        
        # 使用关键短语
        for phrase in analysis["key_phrases"]:
            if len(phrase) > 5 and len(phrase) < 20:
                titles.append(f"第{chapter_number}章：{phrase}")
        
        # 使用钩子短语
        for hook in self.hook_phrases[:5]:
            if any(hook in key for key in [analysis["conflict"], analysis["mystery"], analysis["achievement"]]):
                titles.append(f"第{chapter_number}章：{hook}！")
        
        return titles[:3]

    def _apply_tone_modifier(self, title: str, tone: Optional[str], tone_signals: Dict[str, int]) -> Optional[str]:
        """根据语调替换关键词"""
        if not title:
            return title
        chosen_tone = tone
        if not chosen_tone and tone_signals:
            non_zero = [(tone_name, score) for tone_name, score in tone_signals.items() if score > 0]
            source = non_zero or list(tone_signals.items())
            if source:
                chosen_tone = max(source, key=lambda x: x[1])[0]
        if not chosen_tone:
            return title
        modifiers = self.tone_modifiers.get(chosen_tone)
        if not modifiers:
            return title
        for placeholder, replacement in modifiers.items():
            title = title.replace(placeholder, replacement)
        return title

    def _extract_protagonist(self, content: str) -> Optional[str]:
        """从内容中猜测主角名字"""
        candidates = re.findall(r'[\u4e00-\u9fa5]{2,3}', content[:300])
        if not candidates:
            return None
        frequency = Counter(candidates)
        most_common = frequency.most_common()
        for name, count in most_common:
            if count > 1:
                return name
        return most_common[0][0] if most_common else None

    def _detect_tone_signals(self, content: str) -> Dict[str, int]:
        """识别语气信号"""
        tone_words = {
            "爽文": ["打脸", "逆袭", "碾压", "无敌"],
            "悬疑": ["真相", "疑点", "诡异", "调查"],
            "言情": ["心动", "暧昧", "注视", "拥抱"],
            "古风": ["江湖", "宗门", "魂灯", "霜雪"],
            "科幻": ["星舰", "系统", "量子", "宇宙"]
        }
        signals = {}
        for tone, keywords in tone_words.items():
            signals[tone] = sum(content.count(word) for word in keywords)
        return signals

    def _build_diagnostics(self, titles: List[str], analysis: Dict, tone: Optional[str]) -> Dict:
        """构建诊断信息"""
        tone = tone or max(analysis["tone_signals"], key=analysis["tone_signals"].get, default=None)
        diversity_score = len(set(len(t) for t in titles)) / max(len(titles), 1)
        hook_usage = sum(any(hook in title for hook in self.hook_phrases) for title in titles)
        return {
            "tone": tone,
            "diversity_score": round(diversity_score, 2),
            "hook_density": round(hook_usage / max(len(titles), 1), 2),
            "protagonist": analysis.get("protagonist", "主角")
        }

