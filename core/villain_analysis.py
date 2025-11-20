"""
七宗罪反派人性刻画理论框架
用于分析和塑造反派角色
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class SevenDeadlySins(Enum):
    """七宗罪枚举"""
    PRIDE = "傲慢"
    ENVY = "嫉妒"
    WRATH = "愤怒"
    SLOTH = "懒惰"
    GREED = "贪婪"
    GLUTTONY = "暴食"
    LUST = "色欲"


@dataclass
class SinAnalysis:
    """罪的分析结构"""
    sin: SevenDeadlySins
    psychological_analysis: str  # 心理分析
    literary_symbolism: str  # 文学象征意义
    narrative_function: str  # 叙事功能
    typical_examples: List[str]  # 典型反派举例
    key_traits: List[str]  # 关键特征
    plot_points: List[str]  # 关键情节点


class VillainAnalyzer:
    """反派分析器 - 基于七宗罪理论"""
    
    def __init__(self):
        self.sin_framework = self._build_sin_framework()
    
    def _build_sin_framework(self) -> Dict[SevenDeadlySins, SinAnalysis]:
        """构建七宗罪理论框架"""
        return {
            SevenDeadlySins.PRIDE: SinAnalysis(
                sin=SevenDeadlySins.PRIDE,
                psychological_analysis="过度以自我为中心，夸大自我价值，蔑视他人。深层不安全感或极端优越感，通过贬低他人维持自尊。性格缺陷：自负、自大，听不进劝告，容易低估敌人。",
                literary_symbolism="象征权力腐化和道德堕落，对公正与平等的侵犯。'骄兵必败'、'满招损，谦受益'。警示'德不配位'的危险。",
                narrative_function="冲突催化剂，自负使其低估主角，给予可乘之机推动反转。激起读者反感增强代入感。磨炼主角性格，学会谦逊与自省。高潮时因过度自信露出破绽，走向自我毁灭。",
                typical_examples=["魂天帝（《斗破苍穹》）", "宗门天才、公子哥反派"],
                key_traits=["自负", "自大", "目中无人", "蔑视他人", "听不进劝告"],
                plot_points=["展现傲慢", "低估主角", "给予机会", "露出破绽", "自我毁灭"]
            ),
            SevenDeadlySins.ENVY: SinAnalysis(
                sin=SevenDeadlySins.ENVY,
                psychological_analysis="对他人的成功、才能、地位或情感心怀不满，因自身缺憾产生强烈羡慕和怨恨。性格不自信，自卑却好强，见不得别人比自己好。潜在动机：童年阴影、不公平对待、对主角拥有的资源充满渴望却无法得到。",
                literary_symbolism="象征人性中对公平与爱的扭曲。'嫉妒吞噬心灵'、'因妒生恨'。警示见不得人好的阴暗心理。人性欲望失衡的象征。",
                narrative_function="阴暗镜像角色，映射主角可能堕落的一种可能性。嫉妒心引发的阴谋诡计推动情节。隐藏在主角身边的对手，用表面友善掩盖内心不满。促使主角直面挫折并反思。",
                typical_examples=["皇后乌拉那拉·宜修（《甄嬛传》）", "妒贤嫉能的同门师兄", "对主角恋人暗生嫉恨的情敌"],
                key_traits=["嫉妒", "怨恨", "自卑", "好强", "见不得人好"],
                plot_points=["发现嫉妒", "暗中使绊", "阴谋诡计", "暴露真面目", "自食恶果"]
            ),
            SevenDeadlySins.WRATH: SinAnalysis(
                sin=SevenDeadlySins.WRATH,
                psychological_analysis="难以遏制的暴怒、仇恨与冲动。因遭受伤害或不公积累强烈怨气与怒火。性格暴躁、残忍，遇事容易情绪失控。将自身不幸归咎于外界，把仇恨投射到他人身上。缺乏平和与原谅，沉湎于复仇欲望。",
                literary_symbolism="象征失控的破坏力和扭曲的正义。'以正义为名，扭曲对公义的爱为复仇和憎恨'。警示克制愤怒的重要性。批判极端主义或滥用私刑。",
                narrative_function="矛盾冲突最直观的制造者。暴躁和冲动使剧情充满紧迫感和危险。倒逼主角成长，学会冷静和策略。充当主角的'试金石'，迫使主角坚守道德底线。",
                typical_examples=["北帝段德（《遮天》）", "都市爽文中的仇家反派", "黑道大佬角色"],
                key_traits=["暴怒", "仇恨", "冲动", "残忍", "情绪失控"],
                plot_points=["积累愤怒", "爆发冲突", "失去理智", "激烈对决", "情绪宣泄"]
            ),
            SevenDeadlySins.SLOTH: SinAnalysis(
                sin=SevenDeadlySins.SLOTH,
                psychological_analysis="怠于尽责、贪图安逸的性格弱点。缺乏进取心和责任感，逃避应当承担的义务或行动。沉迷于舒适区，对需要付出努力或冒险的事敬而远之。漫不经心、散漫拖沓，遇事推诿或袖手旁观。可能源于内心虚无和绝望。",
                literary_symbolism="象征堕落与荒废。对善良和责任的冷漠，阻碍道德和精神的进步。对腐朽统治阶级的讽刺。警示不作为的恶果。",
                narrative_function="出现行动上的漏洞，疏于防范或管理，给主角创造可乘之机。制造缓慢腐烂的冲突。以喜剧性或反差性呈现，调节作品气氛。与勤奋主角形成鲜明对比。",
                typical_examples=["尸位素餐的掌门/长老", "贪睡的邪道长老", "商纣王（懒政）"],
                key_traits=["怠惰", "散漫", "推诿", "贪图安逸", "缺乏责任感"],
                plot_points=["展现懒惰", "疏于防范", "给主角机会", "错失良机", "自食其果"]
            ),
            SevenDeadlySins.GREED: SinAnalysis(
                sin=SevenDeadlySins.GREED,
                psychological_analysis="无止境的占有欲和欲壑难填的心态。被渴求所支配，无论金钱、权力、资源甚至他人生命都想据为己有。永不知足，得到一点就想要更多，欲望膨胀失控。源于深层不安全感和匮乏感，或野心极大渴望掌控一切。",
                literary_symbolism="象征人性对物欲的沉溺和反噬。'贪财是万恶之源'、'人为财死，鸟为食亡'。批判社会弊病，警示物欲的奴役。象征侵犯与掠夺。",
                narrative_function="主要冲突的源头之一。贪欲引发战争或阴谋，拉开剧情大幕。不断升级冲突难度。赋予主角明确使命。与主角的奉献形成鲜明对照，升华主题。",
                typical_examples=["魂天帝（《斗破苍穹》）", "财阀恶棍", "贪官污吏", "邪修魔头"],
                key_traits=["贪婪", "占有欲", "永不知足", "野心", "不择手段"],
                plot_points=["展现贪婪", "引发冲突", "不断升级", "露出破绽", "自取灭亡"]
            ),
            SevenDeadlySins.GLUTTONY: SinAnalysis(
                sin=SevenDeadlySins.GLUTTONY,
                psychological_analysis="无节制的纵欲和沉迷。对感官享受的难以抑制的欲望与强迫行为。沉溺于美食、美酒、药物或其他令人成瘾的享乐中无法自拔。自控力极差、贪图即时满足。内心空虚或压力驱动，通过过度摄取逃避现实。",
                literary_symbolism="象征放纵无度的享乐主义和浪费。缺乏节制，过分贪图逸乐最终引入堕落。'酒池肉林'警示奢侈浪费亡国之因。象征欲望的无底洞和感官的奴役。",
                narrative_function="制造触目惊心的情境。缺乏克制，往往会因为一时的享受而犯错误。主角利用反派贪杯好色或瘾头发作之际设计反制。为故事增添人情味和复杂性。",
                typical_examples=["商纣王（酒池肉林）", "吞天魔帝传说", "嗜食珍稀野味的反派"],
                key_traits=["纵欲", "沉迷", "缺乏节制", "贪图享乐", "自控力差"],
                plot_points=["展现暴食", "沉迷享乐", "露出破绽", "被利用", "欲望反噬"]
            ),
            SevenDeadlySins.LUST: SinAnalysis(
                sin=SevenDeadlySins.LUST,
                psychological_analysis="沉溺于不道德的情欲和肉欲之中。强烈而难以克制的性欲望和占有冲动。道德感缺失和自我放纵，将他人视为满足自身欲望的工具。好色成瘾、风流成性，甚至发展出变态的占有欲和虐待倾向。",
                literary_symbolism="象征情欲对于理性的吞噬和对纯洁情感的亵渎。'万恶淫为首'。警示色欲会引发家庭和社会的巨大危机。象征对弱者的侵犯和道德底线的失守。",
                narrative_function="制造危机，觊觎主角或主角挚爱之人，引发绑架、胁迫等情节。引发读者强烈的情绪反应。体现主角的品格，以正直和克制回应反派的下流行径。",
                typical_examples=["妲己（《封神演义》）", "采补派反派", "魔教尊主", "权色交易的贪官"],
                key_traits=["好色", "纵欲", "道德缺失", "占有欲", "虐待倾向"],
                plot_points=["展现色欲", "觊觎目标", "制造危机", "主角反击", "自食恶果"]
            )
        }
    
    def analyze_villain(self, villain_description: str) -> Dict[SevenDeadlySins, float]:
        """
        分析反派角色，返回各罪的匹配度
        Args:
            villain_description: 反派角色描述
        Returns:
            {罪: 匹配度(0-1)}
        """
        scores = {}
        text_lower = villain_description.lower()
        
        # 关键词匹配
        keywords = {
            SevenDeadlySins.PRIDE: ["傲慢", "自负", "自大", "目中无人", "蔑视", "看不起"],
            SevenDeadlySins.ENVY: ["嫉妒", "羡慕", "怨恨", "见不得", "眼红", "妒忌"],
            SevenDeadlySins.WRATH: ["愤怒", "暴怒", "仇恨", "报复", "残忍", "暴躁"],
            SevenDeadlySins.SLOTH: ["懒惰", "怠惰", "散漫", "推诿", "贪图安逸", "不作为"],
            SevenDeadlySins.GREED: ["贪婪", "占有", "野心", "不择手段", "永不知足", "贪财"],
            SevenDeadlySins.GLUTTONY: ["暴食", "纵欲", "沉迷", "享乐", "酒池肉林", "缺乏节制"],
            SevenDeadlySins.LUST: ["色欲", "好色", "淫乱", "纵欲", "占有", "道德缺失"]
        }
        
        for sin, sin_keywords in keywords.items():
            score = 0.0
            matches = sum(1 for keyword in sin_keywords if keyword in text_lower)
            if matches > 0:
                score = min(matches / len(sin_keywords) * 2, 1.0)  # 归一化到0-1
            scores[sin] = score
        
        return scores
    
    def get_primary_sin(self, villain_description: str) -> Optional[Tuple[SevenDeadlySins, float]]:
        """获取主要罪行"""
        scores = self.analyze_villain(villain_description)
        if not scores:
            return None
        
        max_sin = max(scores.items(), key=lambda x: x[1])
        return max_sin if max_sin[1] > 0.3 else None
    
    def get_sin_analysis(self, sin: SevenDeadlySins) -> SinAnalysis:
        """获取特定罪的分析"""
        return self.sin_framework[sin]
    
    def generate_villain_guidance(self, sin: SevenDeadlySins) -> str:
        """生成反派塑造指导"""
        analysis = self.sin_framework[sin]
        
        guidance = f"""
【{sin.value}型反派塑造指导】

心理特征：
{analysis.psychological_analysis}

文学象征：
{analysis.literary_symbolism}

叙事功能：
{analysis.narrative_function}

关键特征：
{', '.join(analysis.key_traits)}

关键情节点：
{', '.join(analysis.plot_points)}

典型案例：
{', '.join(analysis.typical_examples)}
"""
        return guidance
    
    def suggest_villain_development(self, sin: SevenDeadlySins, story_context: str = "") -> Dict:
        """建议反派发展路径"""
        analysis = self.sin_framework[sin]
        
        return {
            "sin": sin.value,
            "key_traits": analysis.key_traits,
            "plot_points": analysis.plot_points,
            "narrative_function": analysis.narrative_function,
            "suggested_scenes": self._generate_suggested_scenes(sin, analysis)
        }
    
    def _generate_suggested_scenes(self, sin: SevenDeadlySins, analysis: SinAnalysis) -> List[str]:
        """生成建议场景"""
        scene_templates = {
            SevenDeadlySins.PRIDE: [
                "反派在众人面前展现傲慢，蔑视主角",
                "反派因自负而低估主角实力",
                "反派拒绝听取他人劝告",
                "反派在关键时刻因过度自信露出破绽",
                "反派最终因傲慢而失败"
            ],
            SevenDeadlySins.ENVY: [
                "反派看到主角的成功，心生嫉妒",
                "反派暗中使绊子，陷害主角",
                "反派的嫉妒心逐渐暴露",
                "反派的阴谋被主角识破",
                "反派因嫉妒而自食恶果"
            ],
            SevenDeadlySins.WRATH: [
                "反派因愤怒而爆发冲突",
                "反派失去理智，大开杀戒",
                "主角面对愤怒反派的挑战",
                "主角以冷静策略对抗愤怒反派",
                "反派的愤怒最终导致自我毁灭"
            ],
            SevenDeadlySins.SLOTH: [
                "反派展现怠惰和散漫",
                "反派疏于防范，给主角机会",
                "主角利用反派的懒惰",
                "反派因懒惰错失良机",
                "反派最终因怠惰而失败"
            ],
            SevenDeadlySins.GREED: [
                "反派展现贪婪和占有欲",
                "反派为利益不择手段",
                "反派的贪婪引发主要冲突",
                "反派的贪欲不断升级",
                "反派因贪婪而自取灭亡"
            ],
            SevenDeadlySins.GLUTTONY: [
                "反派沉溺于享乐",
                "反派因纵欲露出破绽",
                "主角利用反派的弱点",
                "反派的欲望失控",
                "反派因暴食而自食恶果"
            ],
            SevenDeadlySins.LUST: [
                "反派展现色欲和道德缺失",
                "反派觊觎主角或重要角色",
                "反派制造危机",
                "主角反击色欲反派",
                "反派因色欲而自食恶果"
            ]
        }
        
        return scene_templates.get(sin, [])

