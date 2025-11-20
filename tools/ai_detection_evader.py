"""
22_AI检测规避器
用于规避AI检测，使生成内容更自然、更像人类创作
"""

from typing import Any, Dict, List, Optional
import logging
import re
import random

logger = logging.getLogger(__name__)


class AIDetectionEvader:
    """AI检测规避器"""
    
    def __init__(self, seed: Optional[int] = None):
        self.random = random.Random(seed)
        self.evasion_strategies = self._build_strategies()
        self.intensity_map = {
            "low": 0.75,
            "medium": 1.0,
            "high": 1.3,
        }
        self.synonym_map = {
            "突然": ["猛地", "倏然", "一下子"],
            "但是": ["不过", "可是", "然而"],
            "因为": ["由于", "缘于", "出于"],
            "所以": ["因此", "于是", "因而"],
            "虽然": ["尽管", "固然", "虽说"],
            "如果": ["要是", "倘若", "假如"],
            "非常": ["特别", "极其", "相当"],
            "重要": ["关键", "核心", "要紧"],
        }
        self.personal_details = [
            "我之前在论坛上看到过类似的讨论",
            "这跟我朋友的经历真的很像",
            "我前段时间亲自试过一次，印象挺深",
            "之前写文卡文时我也遇到过类似问题",
            "这让我想起小时候看的某本书",
        ]
        self.hesitation_phrases = ["呃", "额", "就是", "好像", "其实", "反正"]
        self.parenthetical_asides = [
            "（真的）",
            "（别问为什么）",
            "（说来话长）",
            "（这可不是玩笑）",
        ]
        self.micro_typo_map = {
            "的": ["地", "得"],
            "吗": ["嘛"],
            "了": ["啦"],
            "啊": ["呀"],
        }
    
    def _build_strategies(self) -> Dict[str, List[str]]:
        """构建规避策略"""
        return {
            "语言风格": [
                "增加口语化表达",
                "使用不完美句式",
                "适当使用语气词",
                "增加个人化表达",
                "使用网络流行语"
            ],
            "文本结构": [
                "增加段落长度变化",
                "使用不规则标点",
                "增加情感色彩",
                "使用比喻和修辞",
                "增加细节描写"
            ],
            "内容特征": [
                "增加主观判断",
                "使用模糊表达",
                "增加个人经验",
                "使用情感词汇",
                "增加不确定性"
            ]
        }
    
    def evade_detection(
        self,
        text: str,
        strategy: str = "all",
        intensity: str = "medium",
    ) -> str:
        """
        规避AI检测
        Args:
            text: 原始文本
            strategy: 策略类型（"all"或具体策略）
            intensity: 调整改写强度（"low"、"medium"、"high"）
        """
        strategy_key = (strategy or "all").lower()
        funcs = self._get_strategy_functions(strategy_key)
        if not funcs:
            logger.warning("未知策略 %s，将回退到全部策略", strategy)
            funcs = self._get_strategy_functions("all")

        intensity_factor = self._get_intensity_factor(intensity)
        
        for func in funcs:
            text = func(text, intensity_factor=intensity_factor)
        
        return text

    def evade_with_feedback(
        self,
        text: str,
        max_iterations: int = 3,
        target_likelihood: float = 0.45,
        strategy: str = "all",
        intensity: str = "medium",
    ) -> Dict[str, Any]:
        """
        迭代规避：结合检测结果多轮微调
        """
        history: List[Dict[str, Any]] = []
        current_text = text
        current_intensity = intensity

        for iteration in range(max_iterations):
            analysis = self.analyze_ai_likelihood(current_text)
            history.append({"iteration": iteration, **analysis})

            if analysis["ai_likelihood"] <= target_likelihood:
                break

            # 若仍高于目标，逐步提高强度
            if analysis["ai_likelihood"] > target_likelihood and current_intensity != "high":
                current_intensity = "high"

            current_text = self.evade_detection(
                current_text,
                strategy=strategy,
                intensity=current_intensity,
            )

        return {"text": current_text, "history": history}
    
    def _get_strategy_functions(self, strategy: str):
        mapping = {
            "language": [
                self._add_oral_expressions,
                self._synonym_replace,
                self._add_colloquial_idioms,
                self._insert_hesitation_breaks,
                self._introduce_micro_typos,
            ],
            "structure": [
                self._vary_sentence_length,
                self._inject_punctuation_variants,
                self._shuffle_clause_sequence,
                self._add_parenthetical_asides,
            ],
            "content": [
                self._add_subjective_expressions,
                self._add_personal_experiences,
                self._add_emotional_words,
                self._add_contextual_noise,
            ],
            "all": [
                self._add_oral_expressions,
                self._synonym_replace,
                self._vary_sentence_length,
                self._inject_punctuation_variants,
                self._add_emotional_words,
                self._add_subjective_expressions,
                self._add_personal_experiences,
                self._add_colloquial_idioms,
                self._shuffle_clause_sequence,
                self._insert_hesitation_breaks,
                self._add_parenthetical_asides,
                self._introduce_micro_typos,
                self._add_contextual_noise,
            ],
        }
        return mapping.get(strategy, [])
    
    def _get_intensity_factor(self, intensity: str) -> float:
        """获取强度系数"""
        return self.intensity_map.get(intensity.lower(), self.intensity_map["medium"])

    def _add_oral_expressions(
        self,
        text: str,
        probability: float = 0.2,
        intensity_factor: float = 1.0,
    ) -> str:
        """添加口语化表达"""
        # 在适当位置添加语气词
        oral_words = ["呢", "啊", "吧", "嘛", "哦", "嗯"]
        sentences = re.split(r'[。！？]', text)
        result = []
        
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                # 随机在部分句子后添加语气词
                if self.random.random() < min(0.9, probability * intensity_factor) and len(sentence) > 10:
                    sentence += self.random.choice(oral_words)
                result.append(sentence)
        
        return '。'.join(result) + '。'
    
    def _synonym_replace(
        self,
        text: str,
        max_replacements: int = 3,
        intensity_factor: float = 1.0,
    ) -> str:
        """做同义改写"""
        replacements = 0
        allowed = max(1, int(max_replacements * intensity_factor))
        for word, alternatives in self.synonym_map.items():
            if word in text and replacements < allowed:
                text = text.replace(word, self.random.choice(alternatives), 1)
                replacements += 1
        return text
    
    def _vary_sentence_length(
        self,
        text: str,
        long_threshold: int = 50,
        intensity_factor: float = 1.0,
    ) -> str:
        """变化句子长度"""
        # 将过长的句子拆分，过短的句子合并
        sentences = re.split(r'[。！？]', text)
        result = []
        
        for sentence in sentences:
            threshold = max(30, int(long_threshold / max(0.5, intensity_factor)))
            if len(sentence) > threshold:
                # 拆分长句
                parts = re.split(r'[，,]', sentence)
                if len(parts) > 2:
                    result.append('，'.join(parts[:2]) + '，')
                    result.append('，'.join(parts[2:]))
                else:
                    result.append(sentence)
            else:
                result.append(sentence)
        
        return '。'.join([s for s in result if s.strip()]) + '。'

    def _inject_punctuation_variants(
        self,
        text: str,
        intensity_factor: float = 1.0,
    ) -> str:
        """引入不同的标点组合，降低机械感"""
        punctuation_map = {
            "，": ["，", "，", "，", "……", "——"],
            "。": ["。", "。", "！", "？"],
            "！": ["！", "！", "！！"],
        }
        characters = list(text)
        for idx, char in enumerate(characters):
            if char in punctuation_map and self.random.random() < min(0.9, 0.15 * intensity_factor):
                characters[idx] = self.random.choice(punctuation_map[char])
        return ''.join(characters)
    
    def _add_emotional_words(self, text: str, intensity_factor: float = 1.0) -> str:
        """添加情感词汇"""
        emotional_words = {
            "非常": ["特别", "极其", "超级", "十分"],
            "很": ["挺", "相当", "颇为", "蛮"],
            "好": ["不错", "可以", "还行", "挺好"]
        }
        
        for word, alternatives in emotional_words.items():
            if word in text and self.random.random() < min(0.9, 0.3 * intensity_factor):
                text = text.replace(word, self.random.choice(alternatives), 1)
        
        return text
    
    def _add_subjective_expressions(
        self,
        text: str,
        intensity_factor: float = 1.0,
    ) -> str:
        """添加主观表达"""
        subjective_phrases = [
            "我觉得", "在我看来", "说实话", "坦率地说",
            "可能", "也许", "大概", "似乎"
        ]
        
        # 在部分句子前添加主观表达
        sentences = re.split(r'[。！？]', text)
        result = []
        
        for sentence in sentences:
            if sentence.strip() and len(sentence) > 15:
                if self.random.random() < min(0.8, 0.15 * intensity_factor):
                    sentence = self.random.choice(subjective_phrases) + "，" + sentence
            result.append(sentence)
        
        return '。'.join([s for s in result if s.strip()]) + '。'
    
    def _add_personal_experiences(
        self,
        text: str,
        intensity_factor: float = 1.0,
    ) -> str:
        """插入个人化体验句"""
        sentences = re.split(r'(。|！|？)', text)
        probability = min(0.8, 0.3 * intensity_factor)
        if sentences and self.random.random() < probability:
            insert_idx = self.random.randrange(0, len(sentences), 2)
            sentences.insert(insert_idx, self.random.choice(self.personal_details))
            sentences.insert(insert_idx + 1, "。")
        return ''.join(sentences)
    
    def _add_colloquial_idioms(
        self,
        text: str,
        intensity_factor: float = 1.0,
    ) -> str:
        """添加俗语或成语来提升自然度"""
        idioms = [
            "说句心里话",
            "老实讲",
            "换句话说",
            "打个比方",
            "说白了",
            "按理说",
            "抛开客套",
        ]
        sentences = re.split(r'[。！？]', text)
        result = []
        for sentence in sentences:
            if sentence.strip():
                if self.random.random() < min(0.7, 0.1 * intensity_factor):
                    sentence = self.random.choice(idioms) + "，" + sentence
                result.append(sentence)
        return '。'.join(result) + '。'
    
    def _shuffle_clause_sequence(
        self,
        text: str,
        intensity_factor: float = 1.0,
    ) -> str:
        """对部分复句进行子句重排"""
        sentences = re.split(r'[。！？]', text)
        adjusted = []
        for sentence in sentences:
            clauses = [c.strip() for c in re.split(r'[，,]', sentence) if c.strip()]
            probability = min(0.7, 0.2 * intensity_factor)
            if len(clauses) > 2 and self.random.random() < probability:
                self.random.shuffle(clauses)
                adjusted.append('，'.join(clauses))
            else:
                adjusted.append(sentence)
        return '。'.join([s for s in adjusted if s]) + '。'

    def _insert_hesitation_breaks(
        self,
        text: str,
        intensity_factor: float = 1.0,
    ) -> str:
        """加入停顿和犹豫词"""
        fillers = self.hesitation_phrases
        sentences = re.split(r'[。！？]', text)
        result = []

        for sentence in sentences:
            if sentence.strip():
                if self.random.random() < min(0.6, 0.12 * intensity_factor):
                    sentence = self.random.choice(fillers) + "，" + sentence
                result.append(sentence)
        return '。'.join(result) + '。'

    def _add_parenthetical_asides(
        self,
        text: str,
        intensity_factor: float = 1.0,
    ) -> str:
        """在句子中插入括号补充说明"""
        sentences = re.split(r'[。！？]', text)
        result = []
        for sentence in sentences:
            if sentence.strip() and self.random.random() < min(0.5, 0.1 * intensity_factor):
                aside = self.random.choice(self.parenthetical_asides)
                insertion_point = min(len(sentence), max(1, int(len(sentence) * self.random.random())))
                sentence = sentence[:insertion_point] + aside + sentence[insertion_point:]
            result.append(sentence)
        return '。'.join([s for s in result if s.strip()]) + '。'

    def _introduce_micro_typos(
        self,
        text: str,
        intensity_factor: float = 1.0,
    ) -> str:
        """模拟轻微口误或错别字"""
        characters = list(text)
        for idx, char in enumerate(characters):
            if char in self.micro_typo_map and self.random.random() < min(0.5, 0.05 * intensity_factor):
                characters[idx] = self.random.choice(self.micro_typo_map[char])
        return ''.join(characters)

    def _add_contextual_noise(
        self,
        text: str,
        intensity_factor: float = 1.0,
    ) -> str:
        """添加与情境相关的碎碎念"""
        noise_phrases = [
            "顺带一提",
            "题外话",
            "扯远了",
            "说回来",
            "闲话少说",
        ]
        sentences = re.split(r'[。！？]', text)
        result = []
        for sentence in sentences:
            if sentence.strip():
                if self.random.random() < min(0.5, 0.1 * intensity_factor):
                    sentence += "，" + self.random.choice(noise_phrases) + "，"
                result.append(sentence)
        return '。'.join(result) + '。'
    
    def analyze_ai_likelihood(self, text: str) -> Dict:
        """分析文本的AI可能性"""
        scores = {
            "perfection_score": self._check_perfection(text),
            "variety_score": self._check_variety(text),
            "emotional_score": self._check_emotional(text),
            "subjective_score": self._check_subjective(text),
            "readability_score": self._estimate_readability(text),
            "burstiness_score": self._estimate_burstiness(text),
            "idiom_score": self._check_idiom_usage(text),
            "noise_score": self._check_human_noise(text),
            "personal_score": self._check_personal_presence(text),
        }
        
        total_score = sum(scores.values()) / len(scores)
        
        return {
            "ai_likelihood": total_score,
            "scores": scores,
            "suggestions": self._generate_suggestions(scores)
        }
    
    def _check_perfection(self, text: str) -> float:
        """检查完美度（AI文本通常更完美）"""
        # 检查句子长度是否过于均匀
        sentences = re.split(r'[。！？]', text)
        if len(sentences) < 3:
            return 0.5
        
        lengths = [len(s) for s in sentences if s.strip()]
        if not lengths:
            return 0.5
        
        avg_length = sum(lengths) / len(lengths)
        variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
        
        # 方差越小，越像AI
        return min(1.0, 1.0 - variance / 100)
    
    def _check_variety(self, text: str) -> float:
        """检查多样性"""
        # 检查词汇重复度
        words = re.findall(r'\w+', text)
        if len(words) < 10:
            return 0.5
        
        unique_ratio = len(set(words)) / len(words)
        # 唯一词比例越低，越像AI
        return 1.0 - unique_ratio
    
    def _check_emotional(self, text: str) -> float:
        """检查情感色彩"""
        emotional_words = ["非常", "特别", "极其", "很", "好", "坏", "喜欢", "讨厌"]
        count = sum(1 for word in emotional_words if word in text)
        # 情感词越少，越像AI
        return max(0.0, 1.0 - count / 10)
    
    def _check_subjective(self, text: str) -> float:
        """检查主观性"""
        subjective_words = ["我觉得", "我认为", "可能", "也许", "大概"]
        count = sum(1 for word in subjective_words if word in text)
        # 主观词越少，越像AI
        return max(0.0, 1.0 - count / 5)
    
    def _generate_suggestions(self, scores: Dict) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if scores["perfection_score"] > 0.7:
            suggestions.append("增加句子长度变化，避免过于规整")
        
        if scores["variety_score"] > 0.7:
            suggestions.append("增加词汇多样性，避免重复使用相同词汇")
        
        if scores["emotional_score"] > 0.7:
            suggestions.append("增加情感词汇，让文本更有温度")
        
        if scores["subjective_score"] > 0.7:
            suggestions.append("增加主观表达，体现个人观点")
        
        if scores["readability_score"] > 0.7:
            suggestions.append("适当加入停顿与小插曲，使节奏更有起伏")
        
        if scores["burstiness_score"] > 0.7:
            suggestions.append("交替使用长短句，避免节奏单调")
        
        if scores["idiom_score"] > 0.7:
            suggestions.append("穿插口语化俗语或成语，提升生活气息")

        if scores["noise_score"] > 0.7:
            suggestions.append("适当加入犹豫、停顿或感叹，模拟自然思考过程")

        if scores["personal_score"] > 0.7:
            suggestions.append("添加个人经历或评价，让叙述更具现场感")
        
        return suggestions
    
    def _estimate_readability(self, text: str) -> float:
        """估算可读性（越低越口语）"""
        words = re.findall(r'\w+', text)
        if not words:
            return 0.5
        avg_len = sum(len(w) for w in words) / len(words)
        return min(1.0, avg_len / 5)
    
    def _estimate_burstiness(self, text: str) -> float:
        """衡量长短句交替程度"""
        sentences = [s for s in re.split(r'[。！？]', text) if s.strip()]
        if len(sentences) < 3:
            return 0.5
        lengths = [len(s) for s in sentences]
        long_ratio = sum(1 for l in lengths if l > 40) / len(lengths)
        short_ratio = sum(1 for l in lengths if l < 15) / len(lengths)
        burstiness = abs(long_ratio - short_ratio)
        return min(1.0, burstiness + 0.3)
    
    def _check_idiom_usage(self, text: str) -> float:
        """检测成语/俗语使用"""
        idiom_candidates = ["说白了", "老实讲", "按理说", "打个比方", "换句话说"]
        count = sum(text.count(phrase) for phrase in idiom_candidates)
        return max(0.0, 1.0 - count / 3)

    def _check_human_noise(self, text: str) -> float:
        """检测停顿/语气词存在"""
        markers = self.hesitation_phrases + ["呢", "吧", "嘛", "我觉得"]
        count = sum(text.count(marker) for marker in markers)
        return max(0.0, 1.0 - count / 8)

    def _check_personal_presence(self, text: str) -> float:
        """检测个人化内容"""
        personal_markers = ["我", "我们", "亲自", "经历", "朋友"]
        count = sum(text.count(marker) for marker in personal_markers)
        return max(0.0, 1.0 - count / 10)

