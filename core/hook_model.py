"""
基于Hook模型的网络小说写作策略
用于指导情节设计和节奏控制
"""

from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class HookStage(Enum):
    """Hook模型四个阶段"""
    TRIGGER = "触发"
    ACTION = "行动"
    REWARD = "奖励"
    INVESTMENT = "投入"


@dataclass
class StageGuide:
    """阶段指导"""
    stage: HookStage
    goal: str  # 目标
    mechanism: str  # 机制解析
    strategies: List[str]  # 写作策略
    key_phrases: List[str]  # 关键提示语
    warnings: List[str]  # 注意事项


class HookModelGuide:
    """Hook模型写作指导"""
    
    def __init__(self):
        self.stage_guides = self._build_stage_guides()
    
    def _build_stage_guides(self) -> Dict[HookStage, StageGuide]:
        """构建阶段指导"""
        return {
            HookStage.TRIGGER: StageGuide(
                stage=HookStage.TRIGGER,
                goal="引爆读者兴趣，精准击中读者内心已有的欲望与情绪痛点",
                mechanism="利用读者普遍存在的幻想或不满（逆袭崛起的梦想、不公平遭遇的怨愤），在几句话或开头一章内抓住读者的心",
                strategies=[
                    "围绕读者欲望设计情节：先想目标读者最渴望体验什么爽点",
                    "对准时代共鸣与痛点：融入流行话题或普遍心声",
                    "营造强烈冲突和悬念：一上来就把核心矛盾抛出来",
                    "刺激'妄想'式幻想：适度夸张描写以勾起极致幻想"
                ],
                key_phrases=[
                    "逆袭", "打脸", "莫欺少年穷", "高攀不起", "屈辱", "嘲笑", "愤怒", "不甘",
                    "他攥紧拳头暗下决心...", "今天你对我爱答不理，明天让你高攀不起！",
                    "辱我者，必要百倍奉还！"
                ],
                warnings=[
                    "避免平淡冗长的开局：第一句话就要有钩子",
                    "不要让读者摸不着头脑：只聚焦一两个亮点",
                    "切忌生硬说教或逆潮流：读者爽感高于一切"
                ]
            ),
            HookStage.ACTION: StageGuide(
                stage=HookStage.ACTION,
                goal="促使读者持续不断地阅读下去，降低阅读阻力",
                mechanism="降低阅读门槛，让读者可以毫不费力地反复阅读，形成节奏快、读起来爽的阅读体验",
                strategies=[
                    "降低阅读门槛：用通俗直白的方式讲故事，避免晦涩难懂的词汇",
                    "开篇快速切入正题：坚持'开门见山'的原则",
                    "提供即时满足与期待：让读者尽快品尝到故事的乐趣",
                    "快节奏叙事技巧：多用短句和动词，减少冗长描写"
                ],
                key_phrases=[
                    "立刻", "突然", "说时迟那时快", "眨眼间", "毫不犹豫",
                    "话不多说，直接...", "他来不及细想，本能地...",
                    "到底会怎样呢？（悬念）"
                ],
                warnings=[
                    "信息过载，降低可读性：设定随着剧情逐步展现",
                    "避免剧情平淡无高潮：每一章都设计一个小高潮",
                    "防止读者疲劳：快节奏但不能千篇一律"
                ]
            ),
            HookStage.REWARD: StageGuide(
                stage=HookStage.REWARD,
                goal="制造不确定性的爽点刺激，让读者欲罢不能",
                mechanism="奖励的'不确定性'是关键。出人意料的转折、大起大落的刺激才最让人沉迷。打破读者预期，让爽点呈现出'时高时低、悬念叠生'的节奏",
                strategies=[
                    "避免线性、可预见的情节：不要按最朴素直接的方式发展剧情",
                    "引入'运气元素'提高随机性：增加剧情结果的不确定性",
                    "爽点升级与新奇感：不断迭代升级或推陈出新",
                    "制造悬念链与多波高潮：串联多个悬念和高潮"
                ],
                key_phrases=[
                    "万万没想到", "出乎意料", "岂料", "意外之喜", "峰回路转", "柳暗花明",
                    "突然，一道身影闪现...", "没想到最后得到的竟是...", "异变陡生！"
                ],
                warnings=[
                    "逻辑不能崩塌：每一个大的反转和惊喜，事前最好有所铺垫",
                    "过度重复套路：尽量让爽点花样多变",
                    "注意读者心理节奏：过度高强度的刺激连续不断也可能使读者'爽疲劳'"
                ]
            ),
            HookStage.INVESTMENT: StageGuide(
                stage=HookStage.INVESTMENT,
                goal="积累沉没成本与情感依赖，让读者长期留下来",
                mechanism="读者通过持续阅读在小说虚拟世界中投入的情感和精力，与主角一起累积起来的'虚拟财富'。当这种虚拟财富越来越多时，读者对作品的情感投入就越深",
                strategies=[
                    "帮读者积累'虚拟成就'：有意识地为主角构建一张不断增长的'荣耀清单'",
                    "塑造难以割舍的羁绊：着力塑造一些让读者投入感情的角色和关系",
                    "营造强烈的代入与沉浸：让读者深深沉浸于小说构筑的幻想世界",
                    "引导读者参与社群与互动：增加读者对作品的投入感"
                ],
                key_phrases=[
                    "一步步", "渐渐地", "沧海桑田", "筚路蓝缕", "情同手足", "难舍难分",
                    "回首往昔，他已今非昔比...", "这片土地的每一寸，都浸透了他们的汗与泪。",
                    "多年奋战换来的荣耀，使他再也无法回头。"
                ],
                warnings=[
                    "防止后期崩盘：越到后期，读者投入越深，作者越要谨慎对待剧情走向",
                    "不断提供新的看点：长篇小说写到百万字后，需要注入新鲜元素",
                    "警惕读者移情别恋：需要稳住更新频率和质量"
                ]
            )
        }
    
    def get_stage_guide(self, stage: HookStage) -> StageGuide:
        """获取阶段指导"""
        return self.stage_guides[stage]
    
    def analyze_chapter(self, chapter_content: str, chapter_number: int) -> Dict[HookStage, float]:
        """
        分析章节的Hook模型应用情况
        Returns:
            {阶段: 应用程度(0-1)}
        """
        scores = {}
        
        # 根据章节位置判断主要阶段
        if chapter_number <= 5:
            # 前5章主要是触发和行动阶段
            scores[HookStage.TRIGGER] = self._check_trigger_elements(chapter_content)
            scores[HookStage.ACTION] = self._check_action_elements(chapter_content)
            scores[HookStage.REWARD] = self._check_reward_elements(chapter_content)
            scores[HookStage.INVESTMENT] = 0.2  # 早期投入较少
        elif chapter_number <= 50:
            # 中期主要是行动和奖励阶段
            scores[HookStage.TRIGGER] = 0.3
            scores[HookStage.ACTION] = self._check_action_elements(chapter_content)
            scores[HookStage.REWARD] = self._check_reward_elements(chapter_content)
            scores[HookStage.INVESTMENT] = self._check_investment_elements(chapter_content)
        else:
            # 后期主要是奖励和投入阶段
            scores[HookStage.TRIGGER] = 0.2
            scores[HookStage.ACTION] = 0.4
            scores[HookStage.REWARD] = self._check_reward_elements(chapter_content)
            scores[HookStage.INVESTMENT] = self._check_investment_elements(chapter_content)
        
        return scores
    
    def _check_trigger_elements(self, content: str) -> float:
        """检查触发元素"""
        trigger_keywords = ["逆袭", "打脸", "屈辱", "嘲笑", "愤怒", "不甘", "发誓", "决心"]
        matches = sum(1 for keyword in trigger_keywords if keyword in content)
        return min(matches / len(trigger_keywords) * 3, 1.0)
    
    def _check_action_elements(self, content: str) -> float:
        """检查行动元素"""
        action_keywords = ["立刻", "突然", "眨眼间", "毫不犹豫", "直接", "马上"]
        matches = sum(1 for keyword in action_keywords if keyword in content)
        return min(matches / len(action_keywords) * 2, 1.0)
    
    def _check_reward_elements(self, content: str) -> float:
        """检查奖励元素"""
        reward_keywords = ["没想到", "出乎意料", "意外", "惊喜", "峰回路转", "异变"]
        matches = sum(1 for keyword in reward_keywords if keyword in content)
        return min(matches / len(reward_keywords) * 2, 1.0)
    
    def _check_investment_elements(self, content: str) -> float:
        """检查投入元素"""
        investment_keywords = ["一步步", "渐渐", "积累", "成就", "羁绊", "回忆", "不舍"]
        matches = sum(1 for keyword in investment_keywords if keyword in content)
        return min(matches / len(investment_keywords) * 2, 1.0)
    
    def generate_stage_guidance(self, stage: HookStage, context: str = "") -> str:
        """生成阶段写作指导"""
        guide = self.stage_guides[stage]
        
        guidance = f"""
【{stage.value}阶段写作指导】

目标：
{guide.goal}

机制解析：
{guide.mechanism}

写作策略：
{chr(10).join(f'{i+1}. {s}' for i, s in enumerate(guide.strategies))}

关键提示语：
{', '.join(guide.key_phrases[:10])}...

注意事项：
{chr(10).join(f'⚠ {w}' for w in guide.warnings)}
"""
        return guidance
    
    def suggest_improvements(self, chapter_content: str, chapter_number: int) -> List[str]:
        """建议改进方向"""
        scores = self.analyze_chapter(chapter_content, chapter_number)
        suggestions = []
        
        # 根据章节位置和得分给出建议
        if chapter_number <= 5:
            if scores[HookStage.TRIGGER] < 0.5:
                suggestions.append("增加触发元素：加入冲突、悬念或情绪痛点")
            if scores[HookStage.ACTION] < 0.5:
                suggestions.append("提升行动阶段：加快节奏，降低阅读门槛")
        elif chapter_number <= 50:
            if scores[HookStage.REWARD] < 0.5:
                suggestions.append("增强奖励阶段：加入意外转折和爽点")
            if scores[HookStage.ACTION] < 0.5:
                suggestions.append("保持行动流畅：确保节奏明快")
        else:
            if scores[HookStage.INVESTMENT] < 0.5:
                suggestions.append("强化投入阶段：积累成就和情感羁绊")
            if scores[HookStage.REWARD] < 0.5:
                suggestions.append("持续提供奖励：保持爽点不断")
        
        return suggestions

