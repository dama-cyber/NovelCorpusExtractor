"""
Hook模型优化工具
用于优化章节的Hook模型应用
"""

from typing import Dict, List, Optional
import logging
from ..core.hook_model import HookModelGuide, HookStage

logger = logging.getLogger(__name__)


class HookOptimizer:
    """Hook模型优化器"""
    
    def __init__(self):
        self.guide = HookModelGuide()
    
    def optimize_chapter(self, chapter_content: str, chapter_number: int,
                         expected_stage: Optional[HookStage] = None) -> Dict:
        """
        优化章节的Hook模型应用
        Returns:
            优化建议和改进后的内容建议
        """
        # 分析当前章节
        scores = self.guide.analyze_chapter(chapter_content, chapter_number)
        suggestions = self.guide.suggest_improvements(chapter_content, chapter_number)
        
        # 确定主要阶段
        primary_stage = max(scores.items(), key=lambda x: x[1])[0]
        stage_guide = self.guide.get_stage_guide(primary_stage)
        delta = None
        if expected_stage and expected_stage != primary_stage:
            delta = f"预期阶段为{expected_stage.value}，当前主要阶段为{primary_stage.value}"
        
        return {
            "chapter_number": chapter_number,
            "current_scores": scores,
            "primary_stage": primary_stage.value,
            "expected_stage": expected_stage.value if expected_stage else None,
            "stage_mismatch": delta,
            "suggestions": suggestions,
            "stage_guidance": self.guide.generate_stage_guidance(primary_stage),
            "key_phrases_to_add": stage_guide.key_phrases[:5]  # 建议添加的关键短语
        }
    
    def optimize_chapters(self, chapters: List[Dict]) -> Dict:
        """批量优化多个章节并生成覆盖率报告"""
        results = []
        stage_distribution = {stage.value: 0 for stage in HookStage}
        for idx, chapter in enumerate(chapters, start=1):
            content = chapter.get("content", "")
            expected = chapter.get("expected_stage")
            expected_stage = HookStage(expected) if expected else None
            result = self.optimize_chapter(content, idx, expected_stage=expected_stage)
            results.append(result)
            stage_distribution[result["primary_stage"]] += 1
        total = len(results) or 1
        coverage = {stage: round(count / total, 2) for stage, count in stage_distribution.items()}
        return {
            "chapter_reports": results,
            "stage_coverage": coverage,
            "imbalances": self._detect_imbalances(coverage)
        }

    def _detect_imbalances(self, coverage: Dict[str, float]) -> List[str]:
        """识别Hook阶段覆盖率问题"""
        issues = []
        if coverage.get(HookStage.TRIGGER.value, 0) < 0.15:
            issues.append("触发阶段占比偏低，读者代入感不足")
        if coverage.get(HookStage.PAYOFF.value, 0) < 0.15:
            issues.append("兑现阶段不足，爽点可能欠缺")
        if coverage.get(HookStage.RETAIN.value, 0) < 0.15:
            issues.append("留存阶段占比低，难以维持持续阅读")
        return issues

    def generate_hook_prompt(self, stage: HookStage, context: str = "") -> str:
        """生成Hook模型写作提示词"""
        guidance = self.guide.generate_stage_guidance(stage, context)
        
        prompt = f"""请根据Hook模型的{stage.value}阶段指导，优化以下内容：

{context}

{guidance}

请根据以上指导，优化内容，确保：
1. 符合{stage.value}阶段的目标和机制
2. 应用相应的写作策略
3. 适当使用关键提示语
4. 注意避免常见问题

请输出优化后的内容。
"""
        return prompt

