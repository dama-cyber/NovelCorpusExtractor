"""
创作工作流编排器
将10个辅助工具串联成可执行流水线，确保文档示例与CLI保持一致
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from tools.ai_detection_evader import AIDetectionEvader
from tools.chapter_title_generator import ChapterTitleGenerator
from tools.character_consistency_checker import CharacterConsistencyChecker
from tools.commercial_optimizer import CommercialOptimizer
from tools.emotion_curve_optimizer import EmotionCurveOptimizer
from tools.ending_optimizer import EndingOptimizer
from tools.foreshadowing_reminder import ForeshadowingReminder
from tools.hook_optimizer import HookOptimizer
from tools.opening_scene_generator import OpeningSceneGenerator
from tools.platform_adapter import Platform, PlatformAdapter
from tools.worldview_conflict_detector import WorldviewConflictDetector

logger = logging.getLogger(__name__)


class CreativeWorkflowPipeline:
    """串联ALL_TOOLS_GUIDE中的工具，形成可编排的创作工作流"""

    def __init__(self, memory_manager, workflow_config: Optional[Dict[str, Any]] = None):
        self.memory_manager = memory_manager
        self.config = workflow_config or {}

        # 工具实例
        self.opening_generator = OpeningSceneGenerator()
        self.title_generator = ChapterTitleGenerator()
        self.commercial_optimizer = CommercialOptimizer()
        self.platform_adapter = PlatformAdapter()
        self.emotion_optimizer = EmotionCurveOptimizer()
        self.character_checker = CharacterConsistencyChecker(memory_manager)
        self.foreshadowing_reminder = ForeshadowingReminder(memory_manager)
        self.ending_optimizer = EndingOptimizer(memory_manager)
        self.worldview_detector = WorldviewConflictDetector(memory_manager)
        self.ai_evader = AIDetectionEvader()
        self.hook_optimizer = HookOptimizer()

        self.platform_target = self._resolve_platform(self.config.get("platform"))
        self.preview_chars = int(self.config.get("max_preview_chars", 800))

    def run(
        self,
        chunks: List[Dict[str, Any]],
        novel_type: str,
        agent_results: Optional[List[Dict[str, Any]]] = None,
        outline: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """执行完整创作工作流"""
        if not chunks:
            return {}

        logger.debug("创作工作流: 开始执行，chunks=%d", len(chunks))

        creation_flow = self._safe_call(
            "creation_flow",
            lambda: self._run_creation_flow(chunks, novel_type, outline),
            default={},
        )
        optimization_flow = self._safe_call(
            "optimization_flow",
            lambda: self._run_optimization_flow(chunks, novel_type, agent_results),
            default={},
        )
        detection_flow = self._safe_call(
            "detection_flow",
            lambda: self._run_detection_flow(chunks),
            default={},
        )

        return {
            "creation_flow": creation_flow,
            "optimization_flow": optimization_flow,
            "detection_flow": detection_flow,
        }

    # ------------------------------------------------------------------
    # Creation flow
    # ------------------------------------------------------------------
    def _run_creation_flow(
        self, chunks: List[Dict[str, Any]], novel_type: str, outline: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        first_chapter = self._extract_chapter_text(chunks, 0)
        if not first_chapter:
            return {}

        context = {
            "protagonist": self.config.get("protagonist", "主角"),
            "location": self.config.get("location", ""),
            "time": self.config.get("time", "某日"),
            "sample_text": first_chapter[:1000],
        }
        opening_style = self.config.get("opening_style", "auto")
        opening = self.opening_generator.generate_opening(
            novel_type=novel_type, opening_style=opening_style, context=context
        )

        title_details = self.title_generator.generate_title(
            first_chapter,
            chapter_number=1,
            style=self.config.get("title_style", "auto"),
            tone=self.config.get("title_tone"),
            return_details=True,
        )
        selected_title = (title_details.get("titles") or ["临时标题"])[0]
        commercial_summary = self.commercial_optimizer.optimize_title(
            selected_title, novel_type=novel_type, return_details=True
        )

        hook_report = self.hook_optimizer.optimize_chapter(first_chapter, 1)

        platform_payload = {
            "title": selected_title,
            "description": opening.get("full_opening", ""),
            "chapters": self._build_chapter_payload(chunks[:3]),
            "novel_type": novel_type,
            "outline": outline or {},
        }
        platform_target = self.platform_target or Platform.FANQIE
        platform_result = self.platform_adapter.adapt_for_platform(platform_payload, platform_target)
        platform_score = self.platform_adapter.score_against_rules(platform_payload, platform_target)

        return {
            "opening": opening,
            "chapter_titles": title_details,
            "commercial": commercial_summary,
            "platform_adaptation": {
                "target_platform": platform_target.value,
                "adapted": platform_result,
                "score": platform_score,
            },
            "hook_diagnostics": hook_report,
        }

    # ------------------------------------------------------------------
    # Optimization flow
    # ------------------------------------------------------------------
    def _run_optimization_flow(
        self, chunks: List[Dict[str, Any]], novel_type: str, agent_results: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        chapters = self._build_chapter_payload(chunks)
        if not chapters:
            return {}

        target_pattern = self.config.get("emotion_pattern", "wave")
        emotion_dashboard = self.emotion_optimizer.get_curve_dashboard(chapters, target_pattern=target_pattern)

        character_issues = self.character_checker.check_all_characters()
        current_chapter = chapters[-1].get("chapter") or len(chapters)
        foreshadow_report = self.foreshadowing_reminder.get_reminder_report(current_chapter)
        foreshadow_schedule = self.foreshadowing_reminder.schedule_followups(current_chapter)

        ending_style = self.config.get("ending_style", "happy_ending")
        ending_source = chapters[-3:] if len(chapters) >= 3 else chapters
        ending_analysis = self.ending_optimizer.optimize_ending(ending_source, novel_type, ending_style)

        worldview_patch = self.config.get("worldview_patch")
        worldview_conflicts = (
            self.worldview_detector.generate_conflict_report(worldview_patch)
            if worldview_patch
            else {}
        )

        return {
            "emotion_dashboard": emotion_dashboard,
            "character_issues": character_issues,
            "foreshadowing_report": foreshadow_report,
            "foreshadowing_schedule": foreshadow_schedule,
            "ending_analysis": ending_analysis,
            "worldview_conflicts": worldview_conflicts,
            "agent_summary_sample": (agent_results or [])[:3],
        }

    # ------------------------------------------------------------------
    # Detection flow
    # ------------------------------------------------------------------
    def _run_detection_flow(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        sample_text = self._collect_sample_text(chunks)
        if not sample_text:
            return {}

        ai_likelihood = self.ai_evader.analyze_ai_likelihood(sample_text)
        evasion_strategy = self.config.get("ai_strategy", "all")
        evasion_intensity = self.config.get("ai_intensity", "medium")
        evaded_text = self.ai_evader.evade_detection(
            sample_text, strategy=evasion_strategy, intensity=evasion_intensity
        )

        preview = evaded_text[: self.preview_chars]
        if len(evaded_text) > self.preview_chars:
            preview += "…"

        return {
            "ai_likelihood": ai_likelihood,
            "evasion_preview": preview,
            "strategy": evasion_strategy,
            "intensity": evasion_intensity,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _safe_call(self, name: str, func, default: Any) -> Any:
        try:
            return func()
        except Exception as exc:  # pragma: no cover - 容错逻辑
            logger.exception("创作工作流阶段 %s 执行失败: %s", name, exc)
            return default

    def _extract_chapter_text(self, chunks: List[Dict[str, Any]], index: int) -> str:
        if index >= len(chunks):
            return ""
        chunk = chunks[index]
        return chunk.get("text") or chunk.get("content", "")

    def _build_chapter_payload(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        payload = []
        for idx, chunk in enumerate(chunks, start=1):
            content = chunk.get("text") or chunk.get("content", "")
            if not content:
                continue
            payload.append(
                {
                    "content": content,
                    "chunk_id": chunk.get("chunk_id"),
                    "chapter": chunk.get("chapter", idx),
                    "metadata": chunk.get("metadata", {}),
                }
            )
        return payload

    def _collect_sample_text(self, chunks: List[Dict[str, Any]]) -> str:
        texts = []
        total_chars = 0
        max_chars = self.config.get("detection_sample_chars", 3000)
        for chunk in chunks:
            text = chunk.get("text") or chunk.get("content", "")
            if not text:
                continue
            texts.append(text)
            total_chars += len(text)
            if total_chars >= max_chars:
                break
        return "\n".join(texts)

    def _resolve_platform(self, platform_name: Optional[str]) -> Optional[Platform]:
        if not platform_name:
            return None
        name_upper = platform_name.upper()
        for platform in Platform:
            if platform.name == name_upper or platform.value == platform_name:
                return platform
        logger.warning("未知平台 %s，已回退至 FANQIE", platform_name)
        return Platform.FANQIE





