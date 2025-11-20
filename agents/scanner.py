"""
扫描者Agent
负责粗粒度分类打标，识别文本片段类型
"""

from typing import Dict, List, Optional
import re
import logging

logger = logging.getLogger(__name__)


class ScannerAgent:
    """扫描者Agent - 粗粒度分类"""
    
    # 文本类型模式
    TYPE_PATTERNS = {
        "战斗场景": [
            r"挥[剑刀]|出拳|出掌|招式|攻击|防御|战斗|对决|厮杀",
            r"剑气|刀光|拳风|内力|灵力|法力",
            r"败|胜|击退|斩杀|击败"
        ],
        "对话密集区": [
            r'["""''].*?["""'']',
            r"说道|说道|问道|回答|说|问|答",
            r"对话|交谈|聊天"
        ],
        "环境描写": [
            r"山|水|林|城|屋|殿|楼|阁",
            r"风景|景色|环境|氛围|气息",
            r"阳光|月光|星光|风|雨|雪"
        ],
        "心理描写": [
            r"心想|思考|思索|回忆|想起",
            r"感到|觉得|认为|意识到",
            r"内心|心中|脑海里"
        ],
        "修炼突破": [
            r"突破|晋升|升级|境界|修为",
            r"修炼|打坐|运功|调息",
            r"瓶颈|契机|顿悟"
        ],
        "情感戏": [
            r"爱|恨|情|恋|思念|想念",
            r"拥抱|亲吻|牵手|相视",
            r"心动|心跳|脸红|羞涩"
        ],
        "悬念钩子": [
            r"突然|忽然|没想到|竟然|居然",
            r"秘密|真相|谜团|疑问",
            r"就在这时|就在这时|就在这时"
        ]
    }
    
    def __init__(self):
        """初始化扫描者"""
        # 编译正则表达式
        self.compiled_patterns = {}
        for type_name, patterns in self.TYPE_PATTERNS.items():
            self.compiled_patterns[type_name] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def scan_chunk(self, chunk: Dict) -> Dict:
        """
        扫描文本块，进行分类打标
        Returns:
            包含类型标签的块信息
        """
        text = chunk.get("text", "")
        chunk_id = chunk.get("chunk_id", "")
        
        # 计算每种类型的匹配度
        type_scores = {}
        for type_name, patterns in self.compiled_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(pattern.findall(text))
                score += matches
            type_scores[type_name] = score
        
        # 选择得分最高的类型（如果得分>0）
        primary_type = max(type_scores.items(), key=lambda x: x[1]) if type_scores else None
        if primary_type and primary_type[1] > 0:
            primary_type_name = primary_type[0]
        else:
            primary_type_name = "普通叙述"
        
        # 获取所有匹配的类型（得分>0）
        matched_types = [t for t, s in type_scores.items() if s > 0]
        
        return {
            **chunk,
            "primary_type": primary_type_name,
            "matched_types": matched_types,
            "type_scores": type_scores
        }
    
    def batch_scan(self, chunks: List[Dict]) -> List[Dict]:
        """批量扫描"""
        return [self.scan_chunk(chunk) for chunk in chunks]

