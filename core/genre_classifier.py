"""
小说类型分类器
支持36+种小说类型、流派、设定和背景分类
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class GenreCategory(Enum):
    """类型分类枚举"""
    # 基础类型
    ROMANCE = "言情"
    XUANHUAN = "玄幻"
    XIANXIA = "仙侠"
    SUSPENSE = "悬疑"
    SCIFI = "科幻"
    FANTASY = "奇幻"
    BRAINHOLE = "脑洞"
    URBAN = "都市"
    HISTORY = "历史"
    GUVAN = "古言"
    NO_CP = "无CP"
    
    # 核心情节与流派
    REBIRTH = "重生文"
    TRANSMIGRATION = "穿越文"
    BOOK_TRANSMIGRATION = "穿书文"
    SYSTEM = "系统文"
    UNLIMITED_FLOW = "无限流"
    REVENGE = "复仇文"
    LEVEL_UP = "升级流"
    
    # 热门设定与"梗"
    SATISFYING = "爽文"
    UNDERDOG = "屌丝逆袭"
    TRASH_TO_TREASURE = "废柴流"
    FACE_SLAPPING = "打脸爽文"
    GROVELING = "追妻火葬场"
    SECRET_IDENTITY = "马甲文"
    TRUE_FALSE_DAUGHTER = "真假千金"
    DEIFICATION = "迪化文"
    GOING_CRAZY = "发疯文学"
    ANGST = "虐文"
    CP_FOCUSED = "CP塑造"
    
    # 背景与职业
    FARMING = "种田文"
    PALACE_INTRIGUE = "宫斗/宅斗"
    APOCALYPTIC = "末世文"
    ENTERTAINMENT = "娱乐圈文"
    CEO = "总裁文"
    SUPERNATURAL = "灵异文"
    CYBERPUNK = "赛博朋克"
    BUSINESS_WAR = "商战文"
    ADVENTURE = "冒险小说"


class GenreClassifier:
    """小说类型分类器"""
    
    def __init__(self):
        """初始化分类器"""
        self.genre_patterns = self._build_patterns()
        self.genre_descriptions = self._build_descriptions()
        self.genre_tags = self._build_tags()
    
    def _build_patterns(self) -> Dict[GenreCategory, List[str]]:
        """构建类型识别模式"""
        return {
            # 基础类型
            GenreCategory.ROMANCE: [
                r"言情|爱情|恋爱|感情|情感|CP|配对|甜宠|虐恋",
                r"男女主|男主|女主|男配|女配",
                r"心动|喜欢|爱|恨|情|恋"
            ],
            GenreCategory.XUANHUAN: [
                r"玄幻|修炼|法术|魔法|斗气|灵力",
                r"境界|等级|突破|晋升",
                r"宗门|门派|势力"
            ],
            GenreCategory.XIANXIA: [
                r"仙侠|修仙|成仙|飞升|渡劫",
                r"仙|神|魔|妖|鬼",
                r"仙界|神界|魔界"
            ],
            GenreCategory.SUSPENSE: [
                r"悬疑|推理|谜题|线索|真相",
                r"疑点|疑问|猜测|推理",
                r"紧张|刺激|悬念"
            ],
            GenreCategory.SCIFI: [
                r"科幻|未来|科技|星际|太空",
                r"机器人|AI|人工智能|基因|克隆",
                r"飞船|星舰|外星|宇宙"
            ],
            GenreCategory.FANTASY: [
                r"奇幻|魔法|异世界|异界|魔法师",
                r"精灵|龙|兽人|矮人",
                r"魔法阵|魔法杖|魔法书"
            ],
            GenreCategory.BRAINHOLE: [
                r"脑洞|创意|新颖|独特|设定",
                r"反套路|不按常理|出乎意料"
            ],
            GenreCategory.URBAN: [
                r"都市|现代|城市|都市生活",
                r"职场|公司|企业|商业",
                r"现代科技|互联网|金融"
            ],
            GenreCategory.HISTORY: [
                r"历史|古代|朝代|皇帝|朝廷",
                r"历史事件|历史人物|史实"
            ],
            GenreCategory.GUVAN: [
                r"古言|古代言情|古代背景",
                r"古代|古代社会|古代生活"
            ],
            GenreCategory.NO_CP: [
                r"无CP|无感情线|无恋爱|无配对",
                r"专注事业|专注升级|无感情"
            ],
            
            # 核心情节与流派
            GenreCategory.REBIRTH: [
                r"重生|回到过去|重来一次|再来一次",
                r"前世|今生|上辈子|这辈子"
            ],
            GenreCategory.TRANSMIGRATION: [
                r"穿越|魂穿|身体穿越|时空穿越",
                r"异世界|另一个世界|不同时空"
            ],
            GenreCategory.BOOK_TRANSMIGRATION: [
                r"穿书|穿进小说|书中世界|小说世界",
                r"剧情|原著|原书|书中角色"
            ],
            GenreCategory.SYSTEM: [
                r"系统|金手指|任务系统|游戏系统",
                r"系统提示|系统奖励|系统任务",
                r"面板|属性|技能|等级"
            ],
            GenreCategory.UNLIMITED_FLOW: [
                r"无限流|副本|任务世界|主神空间",
                r"无限|轮回|循环|任务"
            ],
            GenreCategory.REVENGE: [
                r"复仇|报仇|报复|报复|复仇",
                r"血海深仇|深仇大恨|报仇雪恨"
            ],
            GenreCategory.LEVEL_UP: [
                r"升级|提升|进阶|突破|成长",
                r"打怪升级|修炼升级|任务升级"
            ],
            
            # 热门设定与"梗"
            GenreCategory.SATISFYING: [
                r"爽文|爽点|畅快|满足|解气",
                r"打脸|逆袭|翻身|扬眉吐气"
            ],
            GenreCategory.UNDERDOG: [
                r"屌丝逆袭|草根逆袭|底层逆袭",
                r"平凡|普通|底层|逆袭|翻身"
            ],
            GenreCategory.TRASH_TO_TREASURE: [
                r"废柴|废物|天赋|觉醒|爆发",
                r"被人看不起|看不起|轻视"
            ],
            GenreCategory.FACE_SLAPPING: [
                r"打脸|打脸爽|震惊|后悔|后悔莫及",
                r"看不起|轻视|嘲讽|被打脸"
            ],
            GenreCategory.GROVELING: [
                r"追妻火葬场|追回|挽回|后悔",
                r"伤害|虐待|离开|追回|道歉"
            ],
            GenreCategory.SECRET_IDENTITY: [
                r"马甲|多重身份|隐藏身份|真实身份",
                r"身份揭露|暴露|震惊"
            ],
            GenreCategory.TRUE_FALSE_DAUGHTER: [
                r"真假千金|身份互换|抱错|换回",
                r"真千金|假千金|身份揭露"
            ],
            GenreCategory.DEIFICATION: [
                r"迪化|误解|过度解读|深不可测",
                r"误会|误解|脑补|过度理解"
            ],
            GenreCategory.GOING_CRAZY: [
                r"发疯|疯批|不按常理|直接|解气",
                r"打破常规|不合常理|直接应对"
            ],
            GenreCategory.ANGST: [
                r"虐|虐心|痛苦|曲折|悲伤",
                r"虐恋|虐文|虐点"
            ],
            GenreCategory.CP_FOCUSED: [
                r"CP|配对|感情线|情感发展",
                r"由恨生爱|步步为营|感情"
            ],
            
            # 背景与职业
            GenreCategory.FARMING: [
                r"种田|种地|发家致富|经商|基建",
                r"农业|农村|田园|致富"
            ],
            GenreCategory.PALACE_INTRIGUE: [
                r"宫斗|宅斗|权力斗争|地位|人际关系",
                r"皇宫|大家族|斗争|算计"
            ],
            GenreCategory.APOCALYPTIC: [
                r"末世|末日|丧尸|天灾|求生",
                r"末世文|末日世界|生存"
            ],
            GenreCategory.ENTERTAINMENT: [
                r"娱乐圈|演艺圈|明星|演员|经纪人",
                r"演戏|综艺|公关|娱乐"
            ],
            GenreCategory.CEO: [
                r"总裁|霸道总裁|CEO|董事长",
                r"总裁文|霸道总裁|商业帝国"
            ],
            GenreCategory.SUPERNATURAL: [
                r"灵异|鬼怪|灵异事件|超自然",
                r"鬼|怪|灵|异|超自然"
            ],
            GenreCategory.CYBERPUNK: [
                r"赛博朋克|高科技低生活|未来社会",
                r"赛博|网络|虚拟|现实"
            ],
            GenreCategory.BUSINESS_WAR: [
                r"商战|商业竞争|公司斗争|商业",
                r"竞争|斗争|商业|企业"
            ],
            GenreCategory.ADVENTURE: [
                r"冒险|探索|未知|危险|磨难",
                r"冒险小说|探索|冒险"
            ]
        }
    
    def _build_descriptions(self) -> Dict[GenreCategory, str]:
        """构建类型描述"""
        return {
            GenreCategory.ROMANCE: "以男女主角的情感拉扯为核心的故事",
            GenreCategory.XUANHUAN: "包含东方幻想元素，如修炼、法术等的小说",
            GenreCategory.XIANXIA: "以修仙、成仙为主题的幻想小说",
            GenreCategory.SUSPENSE: "充满谜题、信息差和紧张氛围，让读者不断猜测的故事",
            GenreCategory.SCIFI: "包含未来科技、星际社会等元素的小说",
            GenreCategory.FANTASY: "泛指包含魔法、异世界等元素的幻想故事",
            GenreCategory.BRAINHOLE: "设定新颖、创意独特的小说",
            GenreCategory.URBAN: "故事背景发生在现代城市的小说，常与异能、商战等元素结合",
            GenreCategory.HISTORY: "以历史时期为背景的小说",
            GenreCategory.GUVAN: "背景设定在古代的言情小说",
            GenreCategory.NO_CP: "没有固定恋爱关系或感情线的小说",
            GenreCategory.REBIRTH: "主角死亡后回到过去，获得重来一次机会的故事",
            GenreCategory.TRANSMIGRATION: "主角的灵魂穿越到另一个时空或另一个人身上的故事",
            GenreCategory.BOOK_TRANSMIGRATION: "主角穿越到自己读过的一本小说世界里的故事",
            GenreCategory.SYSTEM: "主角获得一个类似游戏系统的金手指，可以通过完成任务获得奖励",
            GenreCategory.UNLIMITED_FLOW: "主角被卷入一个个不同的、充满任务和危机的副本世界中求生",
            GenreCategory.REVENGE: "以主角向仇人复仇为主线的故事",
            GenreCategory.LEVEL_UP: "主角通过不断打怪、修炼或完成任务来提升自身实力",
            GenreCategory.SATISFYING: "情节让读者感到极度畅快、满足的小说",
            GenreCategory.UNDERDOG: "出身平凡或处于困境的主角，最终逆风翻盘，走向人生巅峰",
            GenreCategory.TRASH_TO_TREASURE: "开局是被人看不起的'废柴'主角，后期展现出惊人天赋",
            GenreCategory.FACE_SLAPPING: "主角通过展示实力或揭露真相，让曾经看不起自己的人感到震惊",
            GenreCategory.GROVELING: "前期伤害女主角的男主角，在女主角离开后，幡然醒悟并追回",
            GenreCategory.SECRET_IDENTITY: "主角拥有多重不为人知的强大身份，并在关键时刻逐一揭露",
            GenreCategory.TRUE_FALSE_DAUGHTER: "围绕身份被互换的两位女性角色展开的故事",
            GenreCategory.DEIFICATION: "主角的普通行为被周围人过度解读，误认为他是深不可测的高人",
            GenreCategory.GOING_CRAZY: "主角打破常规，用不合常理但又极其直接的方式应对冲突",
            GenreCategory.ANGST: "情节曲折，情感痛苦，旨在让读者感受到'虐心'体验",
            GenreCategory.CP_FOCUSED: "以塑造和描写人物配对的互动和情感发展为核心",
            GenreCategory.FARMING: "主角通过种地、经商、搞基建等方式，从无到有、发家致富",
            GenreCategory.PALACE_INTRIGUE: "故事背景设定在皇宫或大家族，围绕权力、地位和人际关系斗争",
            GenreCategory.APOCALYPTIC: "故事背景设定在世界末日，主角需要努力求生",
            GenreCategory.ENTERTAINMENT: "故事围绕演艺圈的明星、经纪人等展开",
            GenreCategory.CEO: "以霸道总裁和普通女主角的爱情故事为核心的现代言情小说",
            GenreCategory.SUPERNATURAL: "包含鬼怪、灵异事件等元素的故事",
            GenreCategory.CYBERPUNK: "背景通常是'高科技、低生活'的未来社会",
            GenreCategory.BUSINESS_WAR: "以现代商业竞争、公司斗争为主要情节的小说",
            GenreCategory.ADVENTURE: "主角前往未知或危险的地方进行探索，经历重重磨难"
        }
    
    def _build_tags(self) -> Dict[GenreCategory, List[str]]:
        """构建类型标签（用于检索和分类）"""
        return {
            GenreCategory.ROMANCE: ["言情", "Romance", "爱情", "情感"],
            GenreCategory.XUANHUAN: ["玄幻", "Xuanhuan", "Fantasy", "东方幻想"],
            GenreCategory.XIANXIA: ["仙侠", "Xianxia", "修仙"],
            GenreCategory.SUSPENSE: ["悬疑", "Suspense", "推理", "谜题"],
            GenreCategory.SCIFI: ["科幻", "Sci-Fi", "未来", "科技"],
            GenreCategory.FANTASY: ["奇幻", "Fantasy", "魔法", "异世界"],
            GenreCategory.BRAINHOLE: ["脑洞", "High-concept", "创意"],
            GenreCategory.URBAN: ["都市", "Urban", "现代", "城市"],
            GenreCategory.HISTORY: ["历史", "History", "古代"],
            GenreCategory.GUVAN: ["古言", "Historical Romance", "古代言情"],
            GenreCategory.NO_CP: ["无CP", "No Couple", "无感情线"],
            GenreCategory.REBIRTH: ["重生文", "Rebirth", "重生"],
            GenreCategory.TRANSMIGRATION: ["穿越文", "Transmigration", "穿越"],
            GenreCategory.BOOK_TRANSMIGRATION: ["穿书文", "Book Transmigration", "穿书"],
            GenreCategory.SYSTEM: ["系统文", "System", "系统", "金手指"],
            GenreCategory.UNLIMITED_FLOW: ["无限流", "Unlimited Flow", "无限"],
            GenreCategory.REVENGE: ["复仇文", "Revenge", "复仇"],
            GenreCategory.LEVEL_UP: ["升级流", "Level-up", "升级"],
            GenreCategory.SATISFYING: ["爽文", "Satisfying", "爽"],
            GenreCategory.UNDERDOG: ["屌丝逆袭", "Underdog", "逆袭"],
            GenreCategory.TRASH_TO_TREASURE: ["废柴流", "Trash-to-Treasure", "废柴"],
            GenreCategory.FACE_SLAPPING: ["打脸爽文", "Face-slapping", "打脸"],
            GenreCategory.GROVELING: ["追妻火葬场", "Groveling", "追妻"],
            GenreCategory.SECRET_IDENTITY: ["马甲文", "Secret Identity", "马甲"],
            GenreCategory.TRUE_FALSE_DAUGHTER: ["真假千金", "True/False Daughter", "真假"],
            GenreCategory.DEIFICATION: ["迪化文", "Deification", "迪化", "误解"],
            GenreCategory.GOING_CRAZY: ["发疯文学", "Going Crazy", "发疯"],
            GenreCategory.ANGST: ["虐文", "Angst", "虐"],
            GenreCategory.CP_FOCUSED: ["CP塑造", "CP-focused", "CP"],
            GenreCategory.FARMING: ["种田文", "Farming", "种田"],
            GenreCategory.PALACE_INTRIGUE: ["宫斗/宅斗", "Palace Intrigue", "宫斗"],
            GenreCategory.APOCALYPTIC: ["末世文", "Apocalyptic", "末世"],
            GenreCategory.ENTERTAINMENT: ["娱乐圈文", "Entertainment", "娱乐圈"],
            GenreCategory.CEO: ["总裁文", "CEO", "总裁"],
            GenreCategory.SUPERNATURAL: ["灵异文", "Supernatural", "灵异"],
            GenreCategory.CYBERPUNK: ["赛博朋克", "Cyberpunk", "赛博"],
            GenreCategory.BUSINESS_WAR: ["商战文", "Business War", "商战"],
            GenreCategory.ADVENTURE: ["冒险小说", "Adventure", "冒险"]
        }
    
    def classify_text(self, text: str) -> Dict[GenreCategory, float]:
        """
        分类文本，返回类型及其匹配度
        Returns:
            {类型: 匹配度(0-1)}
        """
        scores = {}
        text_lower = text.lower()
        
        for genre, patterns in self.genre_patterns.items():
            score = 0.0
            matches = 0
            
            for pattern in patterns:
                pattern_matches = len(re.findall(pattern, text, re.IGNORECASE))
                matches += pattern_matches
                score += pattern_matches * 0.1  # 每个匹配增加0.1分
            
            # 归一化到0-1
            scores[genre] = min(score, 1.0)
        
        return scores
    
    def get_primary_genres(self, text: str, top_k: int = 3) -> List[Tuple[GenreCategory, float]]:
        """获取主要类型（按匹配度排序）"""
        scores = self.classify_text(text)
        sorted_genres = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [(genre, score) for genre, score in sorted_genres[:top_k] if score > 0]
    
    def get_genre_description(self, genre: GenreCategory) -> str:
        """获取类型描述"""
        return self.genre_descriptions.get(genre, "")
    
    def get_genre_tags(self, genre: GenreCategory) -> List[str]:
        """获取类型标签"""
        return self.genre_tags.get(genre, [])
    
    def get_all_genres(self) -> List[GenreCategory]:
        """获取所有支持的类型"""
        return list(GenreCategory)
    
    def get_genres_by_category(self, category: str) -> List[GenreCategory]:
        """
        按分类获取类型
        category: "基础类型" / "核心情节" / "热门设定" / "背景职业"
        """
        if category == "基础类型":
            return [
                GenreCategory.ROMANCE, GenreCategory.XUANHUAN, GenreCategory.XIANXIA,
                GenreCategory.SUSPENSE, GenreCategory.SCIFI, GenreCategory.FANTASY,
                GenreCategory.BRAINHOLE, GenreCategory.URBAN, GenreCategory.HISTORY,
                GenreCategory.GUVAN, GenreCategory.NO_CP
            ]
        elif category == "核心情节":
            return [
                GenreCategory.REBIRTH, GenreCategory.TRANSMIGRATION,
                GenreCategory.BOOK_TRANSMIGRATION, GenreCategory.SYSTEM,
                GenreCategory.UNLIMITED_FLOW, GenreCategory.REVENGE,
                GenreCategory.LEVEL_UP
            ]
        elif category == "热门设定":
            return [
                GenreCategory.SATISFYING, GenreCategory.UNDERDOG,
                GenreCategory.TRASH_TO_TREASURE, GenreCategory.FACE_SLAPPING,
                GenreCategory.GROVELING, GenreCategory.SECRET_IDENTITY,
                GenreCategory.TRUE_FALSE_DAUGHTER, GenreCategory.DEIFICATION,
                GenreCategory.GOING_CRAZY, GenreCategory.ANGST,
                GenreCategory.CP_FOCUSED
            ]
        elif category == "背景职业":
            return [
                GenreCategory.FARMING, GenreCategory.PALACE_INTRIGUE,
                GenreCategory.APOCALYPTIC, GenreCategory.ENTERTAINMENT,
                GenreCategory.CEO, GenreCategory.SUPERNATURAL,
                GenreCategory.CYBERPUNK, GenreCategory.BUSINESS_WAR,
                GenreCategory.ADVENTURE
            ]
        else:
            return []

