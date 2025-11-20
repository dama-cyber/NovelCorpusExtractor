"""
类型增强器
在生成小说时根据类型标签添加相应的元素和特征
"""

from typing import Dict, List, Optional
import logging
from .genre_classifier import GenreClassifier, GenreCategory

logger = logging.getLogger(__name__)


class GenreEnhancer:
    """类型增强器 - 根据类型标签增强生成内容"""
    
    def __init__(self):
        self.classifier = GenreClassifier()
        self.enhancement_rules = self._build_enhancement_rules()
    
    def _build_enhancement_rules(self) -> Dict[GenreCategory, Dict]:
        """构建增强规则"""
        return {
            # 基础类型增强
            GenreCategory.ROMANCE: {
                "required_elements": ["情感冲突", "CP互动", "感情发展"],
                "style_features": ["细腻情感描写", "对话丰富", "心理活动"],
                "plot_points": ["初遇", "心动", "误会", "和解", "告白"]
            },
            GenreCategory.XUANHUAN: {
                "required_elements": ["修炼体系", "境界等级", "战斗场景"],
                "style_features": ["气势磅礴", "战斗描写", "修炼描写"],
                "plot_points": ["获得功法", "突破境界", "战斗胜利", "获得宝物"]
            },
            GenreCategory.XIANXIA: {
                "required_elements": ["修仙体系", "天劫", "飞升"],
                "style_features": ["仙气飘飘", "道法自然", "超脱世俗"],
                "plot_points": ["入门修仙", "突破瓶颈", "渡劫", "飞升"]
            },
            GenreCategory.SUSPENSE: {
                "required_elements": ["谜题", "线索", "推理", "反转"],
                "style_features": ["紧张氛围", "信息差", "悬念设置"],
                "plot_points": ["发现疑点", "收集线索", "推理过程", "真相揭露"]
            },
            GenreCategory.SCIFI: {
                "required_elements": ["未来科技", "科学设定", "技术细节"],
                "style_features": ["硬科幻", "逻辑严谨", "技术描写"],
                "plot_points": ["科技突破", "技术应用", "科技冲突"]
            },
            GenreCategory.SYSTEM: {
                "required_elements": ["系统提示", "任务系统", "奖励机制"],
                "style_features": ["系统界面", "数据面板", "任务描述"],
                "plot_points": ["系统激活", "接取任务", "完成任务", "获得奖励"]
            },
            GenreCategory.REBIRTH: {
                "required_elements": ["前世记忆", "改变命运", "预知未来"],
                "style_features": ["对比描写", "心理活动", "决心改变"],
                "plot_points": ["重生觉醒", "利用记忆", "改变事件", "避免悲剧"]
            },
            GenreCategory.REVENGE: {
                "required_elements": ["仇恨", "复仇计划", "打脸"],
                "style_features": ["爽点密集", "对比强烈", "情绪释放"],
                "plot_points": ["仇恨觉醒", "制定计划", "执行复仇", "大仇得报"]
            },
            GenreCategory.SATISFYING: {
                "required_elements": ["爽点", "打脸", "逆袭"],
                "style_features": ["节奏快", "冲突强", "情绪高"],
                "plot_points": ["被轻视", "展现实力", "震惊众人", "获得认可"]
            },
            GenreCategory.FACE_SLAPPING: {
                "required_elements": ["打脸", "震惊", "后悔"],
                "style_features": ["对比强烈", "情绪渲染", "爽点突出"],
                "plot_points": ["被嘲讽", "展现实力", "打脸成功", "对方后悔"]
            },
            GenreCategory.SECRET_IDENTITY: {
                "required_elements": ["多重身份", "身份揭露", "震惊"],
                "style_features": ["悬念设置", "身份暗示", "揭露震撼"],
                "plot_points": ["隐藏身份", "身份暗示", "身份揭露", "众人震惊"]
            },
            GenreCategory.DEIFICATION: {
                "required_elements": ["误解", "过度解读", "脑补"],
                "style_features": ["误会加深", "脑补描写", "反差萌"],
                "plot_points": ["普通行为", "被误解", "误解加深", "真相揭露"]
            },
            GenreCategory.FARMING: {
                "required_elements": ["种田", "经商", "发家致富"],
                "style_features": ["细节描写", "过程展示", "成就感"],
                "plot_points": ["开始种田", "收获成果", "扩大规模", "发家致富"]
            },
            GenreCategory.APOCALYPTIC: {
                "required_elements": ["末世环境", "生存危机", "资源争夺"],
                "style_features": ["紧张氛围", "生存描写", "危机感"],
                "plot_points": ["末世降临", "适应环境", "生存挑战", "建立基地"]
            }
        }
    
    def enhance_prompt(self, prompt: str, genres: List[GenreCategory]) -> str:
        """
        根据类型标签增强提示词
        Args:
            prompt: 原始提示词
            genres: 类型列表
        Returns:
            增强后的提示词
        """
        if not genres:
            return prompt
        
        enhancements = []
        
        for genre in genres:
            if genre in self.enhancement_rules:
                rules = self.enhancement_rules[genre]
                desc = self.classifier.get_genre_description(genre)
                
                enhancement = f"\n【{genre.value}类型要求】\n"
                enhancement += f"类型说明: {desc}\n"
                
                if "required_elements" in rules:
                    enhancement += f"必需元素: {', '.join(rules['required_elements'])}\n"
                
                if "style_features" in rules:
                    enhancement += f"风格特征: {', '.join(rules['style_features'])}\n"
                
                if "plot_points" in rules:
                    enhancement += f"关键情节点: {', '.join(rules['plot_points'])}\n"
                
                enhancements.append(enhancement)
        
        enhanced_prompt = prompt
        if enhancements:
            enhanced_prompt += "\n\n" + "="*50 + "\n"
            enhanced_prompt += "类型标签增强要求:\n"
            enhanced_prompt += "="*50
            enhanced_prompt += "\n".join(enhancements)
            enhanced_prompt += "\n" + "="*50 + "\n"
            enhanced_prompt += "请根据以上类型要求，在生成内容时融入相应的元素和特征。\n"
        
        return enhanced_prompt
    
    def get_genre_guidance(self, genres: List[GenreCategory]) -> str:
        """获取类型指导文本"""
        guidance = []
        
        for genre in genres:
            desc = self.classifier.get_genre_description(genre)
            tags = self.classifier.get_genre_tags(genre)
            
            guidance.append(f"- {genre.value}: {desc}")
            if tags:
                guidance.append(f"  标签: {', '.join(tags[:3])}")
        
        return "\n".join(guidance)
    
    def suggest_plot_elements(self, genres: List[GenreCategory]) -> List[str]:
        """根据类型建议情节元素"""
        elements = []
        
        for genre in genres:
            if genre in self.enhancement_rules:
                rules = self.enhancement_rules[genre]
                if "plot_points" in rules:
                    elements.extend(rules["plot_points"])
        
        # 去重
        return list(set(elements))
    
    def suggest_style_features(self, genres: List[GenreCategory]) -> List[str]:
        """根据类型建议风格特征"""
        features = []
        
        for genre in genres:
            if genre in self.enhancement_rules:
                rules = self.enhancement_rules[genre]
                if "style_features" in rules:
                    features.extend(rules["style_features"])
        
        return list(set(features))

