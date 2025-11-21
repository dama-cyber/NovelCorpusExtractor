"""
评论者Agent
负责质量审查和内容优化建议
"""

from typing import Dict, List, Optional
import logging
from ..core.model_interface import LLMClient

logger = logging.getLogger(__name__)


class CriticAgent:
    """评论者Agent - 质量审查和优化建议"""
    
    def __init__(self, llm_client: LLMClient):
        """
        初始化评论者
        Args:
            llm_client: LLM客户端
        """
        self.llm_client = llm_client
    
    async def review_content(
        self, 
        content: str, 
        context: Dict[str, Any],
        review_aspects: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        审查内容质量
        Args:
            content: 要审查的内容
            context: 上下文信息（创作原则、规范等）
            review_aspects: 审查方面列表，如 ["情节", "角色", "风格"]
        Returns:
            审查结果，包含问题列表和建议
        """
        if review_aspects is None:
            review_aspects = ["情节一致性", "角色行为", "风格统一", "逻辑合理性", "可读性"]
        
        # 构建审查提示词
        prompt = self._build_review_prompt(content, context, review_aspects)
        
        try:
            if hasattr(self.llm_client, 'send_prompt_async'):
                response = await self.llm_client.send_prompt_async(prompt)
            else:
                response = self.llm_client.send_prompt(prompt)
            
            # 解析审查结果
            review_result = self._parse_review_response(response)
            
            return {
                "review_aspects": review_aspects,
                "issues": review_result.get("issues", []),
                "suggestions": review_result.get("suggestions", []),
                "overall_score": review_result.get("overall_score", 0),
                "summary": review_result.get("summary", "")
            }
        except Exception as e:
            logger.error(f"内容审查失败: {e}")
            return {
                "error": str(e),
                "issues": [],
                "suggestions": []
            }
    
    def _build_review_prompt(
        self, 
        content: str, 
        context: Dict[str, Any],
        review_aspects: List[str]
    ) -> str:
        """构建审查提示词"""
        constitution = context.get("constitution", "")
        specification = context.get("specification", "")
        plan = context.get("plan", "")
        
        prompt = f"""请对以下创作内容进行质量审查。

创作原则：
{constitution[:1000] if constitution else "无"}

故事规范：
{specification[:1000] if specification else "无"}

创作计划：
{plan[:1000] if plan else "无"}

待审查内容：
{content[:3000]}

请从以下方面进行审查：
{chr(10).join(f"- {aspect}" for aspect in review_aspects)}

对于每个方面，请提供：
1. 问题描述（如有）
2. 严重程度（高/中/低）
3. 具体位置（章节/段落）
4. 改进建议

最后，请给出：
- 总体评分（0-100分）
- 总体评价摘要

请以结构化的格式输出。"""
        return prompt
    
    def _parse_review_response(self, response: str) -> Dict[str, Any]:
        """解析审查响应"""
        import re
        
        issues = []
        suggestions = []
        overall_score = 0
        summary = ""
        
        # 提取问题
        issue_pattern = r'问题[：:]\s*(.+?)(?=\n|$)'
        issues_found = re.findall(issue_pattern, response, re.MULTILINE)
        for issue in issues_found:
            issues.append({"description": issue.strip()})
        
        # 提取建议
        suggestion_pattern = r'建议[：:]\s*(.+?)(?=\n|$)'
        suggestions_found = re.findall(suggestion_pattern, response, re.MULTILINE)
        for suggestion in suggestions_found:
            suggestions.append({"text": suggestion.strip()})
        
        # 提取评分
        score_match = re.search(r'评分[：:]\s*(\d+)', response)
        if score_match:
            overall_score = int(score_match.group(1))
        
        # 提取摘要
        summary_match = re.search(r'摘要[：:]\s*(.+?)(?=\n\n|\Z)', response, re.DOTALL)
        if summary_match:
            summary = summary_match.group(1).strip()
        
        return {
            "issues": issues,
            "suggestions": suggestions,
            "overall_score": overall_score,
            "summary": summary
        }
    
    def quick_review(self, content: str) -> Dict[str, Any]:
        """
        快速审查（同步版本）
        Args:
            content: 要审查的内容
        Returns:
            简化的审查结果
        """
        prompt = f"""请快速审查以下内容，指出最关键的3个问题（如有）：

{content[:2000]}

请以简洁的格式输出问题列表。"""
        
        try:
            response = self.llm_client.send_prompt(prompt)
            return {
                "quick_review": response,
                "has_issues": "问题" in response or "建议" in response
            }
        except Exception as e:
            logger.error(f"快速审查失败: {e}")
            return {"error": str(e)}


