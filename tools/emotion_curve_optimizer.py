"""
25_情感曲线优化器
优化小说的情感曲线，确保节奏张弛有度
"""

from typing import Dict, List, Optional, Tuple
import logging
import numpy as np

logger = logging.getLogger(__name__)


class EmotionCurveOptimizer:
    """情感曲线优化器"""
    
    def __init__(self):
        self.emotion_keywords = self._build_emotion_keywords()
        self.curve_patterns = self._build_curve_patterns()
    
    def _build_emotion_keywords(self) -> Dict[str, List[str]]:
        """构建情感关键词"""
        return {
            "positive": ["开心", "快乐", "兴奋", "满足", "成功", "胜利", "获得", "突破"],
            "negative": ["悲伤", "痛苦", "愤怒", "失望", "失败", "失去", "挫折", "困境"],
            "tension": ["紧张", "危险", "危机", "冲突", "对决", "战斗", "挑战"],
            "relief": ["放松", "安全", "平静", "和解", "解决", "完成"]
        }
    
    def _build_curve_patterns(self) -> Dict[str, List[float]]:
        """构建情感曲线模式"""
        return {
            "wave": [0.3, 0.7, 0.4, 0.8, 0.5, 0.9, 0.6, 1.0],  # 波浪式上升
            "sawtooth": [0.5, 0.8, 0.4, 0.9, 0.5, 1.0, 0.6, 0.95],  # 锯齿式
            "climax": [0.3, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0],  # 逐步高潮
            "roller_coaster": [0.5, 0.8, 0.3, 0.9, 0.4, 1.0, 0.6, 0.95]  # 过山车式
        }
    
    def analyze_emotion_curve(self, chapters: List[Dict]) -> Dict:
        """
        分析情感曲线
        Args:
            chapters: 章节列表，每个章节包含content
        Returns:
            情感曲线分析结果
        """
        emotion_scores = []
        
        for i, chapter in enumerate(chapters):
            content = chapter.get("content", "")
            score = self._calculate_emotion_score(content)
            emotion_scores.append({
                "chapter": i + 1,
                "score": score,
                "emotion_type": self._classify_emotion(score)
            })
        
        # 计算曲线特征
        scores = [s["score"] for s in emotion_scores]
        smoothed_scores = self._smooth_scores(scores)
        curve_features = {
            "average": np.mean(scores) if scores else 0.5,
            "variance": np.var(scores) if scores else 0.0,
            "trend": self._calculate_trend(scores),
            "peaks": self._find_peaks(scores),
            "valleys": self._find_valleys(scores),
            "pattern_similarity": self._calculate_pattern_similarity(smoothed_scores)
        }
        
        # 生成优化建议
        suggestions = self._generate_curve_suggestions(curve_features, emotion_scores)
        
        return {
            "emotion_scores": emotion_scores,
            "curve_features": curve_features,
            "suggestions": suggestions,
            "recommended_pattern": self._recommend_pattern(curve_features)
        }
    
    def optimize_emotion_curve(self, chapters: List[Dict], 
                               target_pattern: str = "wave") -> List[Dict]:
        """
        优化情感曲线
        Args:
            chapters: 章节列表
            target_pattern: 目标曲线模式
        """
        target_curve = self.curve_patterns.get(target_pattern, self.curve_patterns["wave"])
        
        # 分析当前曲线
        analysis = self.analyze_emotion_curve(chapters)
        current_scores = [s["score"] for s in analysis["emotion_scores"]]
        
        # 调整章节情感强度
        optimized_chapters = []
        for i, chapter in enumerate(chapters):
            target_score = target_curve[i % len(target_curve)]
            current_score = current_scores[i] if i < len(current_scores) else 0.5
            
            # 计算需要调整的幅度
            adjustment = target_score - current_score
            
            optimized_chapter = chapter.copy()
            optimized_chapter["emotion_adjustment"] = {
                "current_score": current_score,
                "target_score": target_score,
                "adjustment": adjustment,
                "suggestion": self._get_adjustment_suggestion(adjustment)
            }
            
            optimized_chapters.append(optimized_chapter)
        
        return optimized_chapters

    def get_curve_dashboard(self, chapters: List[Dict], target_pattern: str = "wave") -> Dict:
        """生成参数化仪表盘数据"""
        analysis = self.analyze_emotion_curve(chapters)
        optimized = self.optimize_emotion_curve(chapters, target_pattern=target_pattern)
        return {
            "analysis": analysis,
            "optimized_plan": optimized,
            "target_pattern": target_pattern,
            "pattern_similarity": analysis["curve_features"]["pattern_similarity"]
        }
    
    def _calculate_emotion_score(self, text: str) -> float:
        """计算情感分数（0-1，越高越积极/紧张）"""
        positive_count = sum(1 for word in self.emotion_keywords["positive"] if word in text)
        negative_count = sum(1 for word in self.emotion_keywords["negative"] if word in text)
        tension_count = sum(1 for word in self.emotion_keywords["tension"] if word in text)
        relief_count = sum(1 for word in self.emotion_keywords["relief"] if word in text)
        
        # 计算总分（正面和紧张增加分数，负面和放松降低分数）
        total_words = len(text) / 100  # 归一化
        if total_words == 0:
            return 0.5
        
        score = 0.5  # 基准分
        score += (positive_count + tension_count) / total_words * 0.3
        score -= (negative_count + relief_count) / total_words * 0.2
        
        return max(0.0, min(1.0, score))
    
    def _classify_emotion(self, score: float) -> str:
        """分类情感类型"""
        if score > 0.7:
            return "高潮"
        elif score > 0.5:
            return "上升"
        elif score > 0.3:
            return "平稳"
        else:
            return "低谷"
    
    def _calculate_trend(self, scores: List[float]) -> str:
        """计算趋势"""
        if len(scores) < 2:
            return "平稳"
        
        # 简单线性回归
        x = np.arange(len(scores))
        y = np.array(scores)
        
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 0.01:
            return "上升"
        elif slope < -0.01:
            return "下降"
        else:
            return "平稳"
    
    def _find_peaks(self, scores: List[float], threshold: float = 0.7) -> List[int]:
        """找到峰值位置"""
        peaks = []
        for i in range(1, len(scores) - 1):
            if scores[i] > scores[i-1] and scores[i] > scores[i+1] and scores[i] > threshold:
                peaks.append(i + 1)  # 章节号从1开始
        return peaks
    
    def _find_valleys(self, scores: List[float], threshold: float = 0.3) -> List[int]:
        """找到低谷位置"""
        valleys = []
        for i in range(1, len(scores) - 1):
            if scores[i] < scores[i-1] and scores[i] < scores[i+1] and scores[i] < threshold:
                valleys.append(i + 1)
        return valleys
    
    def _generate_curve_suggestions(self, features: Dict, scores: List[Dict]) -> List[str]:
        """生成曲线优化建议"""
        suggestions = []
        
        # 检查平均值
        if features["average"] < 0.4:
            suggestions.append("整体情感过于低沉，建议增加积极情节")
        elif features["average"] > 0.8:
            suggestions.append("整体情感过于高涨，建议增加缓冲情节")
        
        # 检查方差
        if features["variance"] < 0.05:
            suggestions.append("情感曲线过于平缓，建议增加起伏")
        elif features["variance"] > 0.2:
            suggestions.append("情感曲线波动过大，建议平滑过渡")
        
        # 检查峰值分布
        if len(features["peaks"]) < len(scores) / 10:
            suggestions.append("高潮点过少，建议每10章至少有一个高潮")
        
        # 检查连续低谷
        consecutive_lows = 0
        for score in scores:
            if score["score"] < 0.3:
                consecutive_lows += 1
                if consecutive_lows > 3:
                    suggestions.append("连续低谷过多，建议插入缓冲情节")
                    break
            else:
                consecutive_lows = 0
        
        return suggestions
    
    def _recommend_pattern(self, features: Dict) -> str:
        """推荐曲线模式"""
        if features["variance"] < 0.05:
            return "climax"  # 需要更多起伏
        elif features["average"] < 0.4:
            return "wave"  # 需要提升整体
        else:
            return "roller_coaster"  # 保持刺激
    
    def _get_adjustment_suggestion(self, adjustment: float) -> str:
        """获取调整建议"""
        if adjustment > 0.2:
            return "建议增加积极情节或紧张冲突"
        elif adjustment > 0.1:
            return "建议适度增加情感强度"
        elif adjustment < -0.2:
            return "建议增加缓冲情节或降低强度"
        elif adjustment < -0.1:
            return "建议适度降低情感强度"
        else:
            return "情感强度适中，无需调整"

    def _smooth_scores(self, scores: List[float], window: int = 3) -> List[float]:
        """平滑曲线，避免噪声"""
        if not scores:
            return []
        smoothed = []
        half = window // 2
        for i in range(len(scores)):
            start = max(0, i - half)
            end = min(len(scores), i + half + 1)
            smoothed.append(np.mean(scores[start:end]))
        return smoothed

    def _calculate_pattern_similarity(self, scores: List[float]) -> Dict[str, float]:
        """计算与预设模式的相似度"""
        similarities = {}
        if not scores:
            return {name: 0.0 for name in self.curve_patterns}
        normalized_scores = self._normalize_series(scores)
        for name, pattern in self.curve_patterns.items():
            normalized_pattern = self._normalize_series(pattern)
            aligned_pattern = self._resize_pattern(normalized_pattern, len(normalized_scores))
            diff = np.mean(np.abs(np.array(aligned_pattern) - np.array(normalized_scores)))
            similarities[name] = round(1 - diff, 3)
        return similarities

    def _normalize_series(self, series: List[float]) -> List[float]:
        array = np.array(series)
        if array.ptp() == 0:
            return array.tolist()
        return ((array - array.min()) / array.ptp()).tolist()

    def _resize_pattern(self, pattern: List[float], target_len: int) -> List[float]:
        if not pattern or target_len == len(pattern):
            return pattern[:target_len]
        indices = np.linspace(0, len(pattern) - 1, target_len)
        resized = []
        for idx in indices:
            lower = int(np.floor(idx))
            upper = min(lower + 1, len(pattern) - 1)
            weight = idx - lower
            resized.append(pattern[lower] * (1 - weight) + pattern[upper] * weight)
        return resized

