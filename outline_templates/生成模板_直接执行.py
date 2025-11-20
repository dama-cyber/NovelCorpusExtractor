#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""直接执行生成所有36种类型的大纲模板"""

import yaml
from pathlib import Path

# 类型特定的大纲模板配置
GENRE_TEMPLATES = {
    # 基础类型
    "言情": {"structure_type": "言情小说", "base_structure": "三幕式", "special_elements": ["情感线", "CP互动", "感情发展", "误会与和解"], "key_plot_points": ["初遇", "心动", "误会", "分离", "和解", "告白", "圆满"]},
    "玄幻": {"structure_type": "玄幻小说", "base_structure": "升级流", "special_elements": ["修炼体系", "境界突破", "战斗场景", "宝物获得"], "key_plot_points": ["觉醒", "入门", "突破", "战斗", "获得宝物", "实力提升", "最终对决"]},
    "仙侠": {"structure_type": "仙侠小说", "base_structure": "英雄之旅", "special_elements": ["修仙体系", "天劫", "飞升", "道心"], "key_plot_points": ["入门修仙", "修炼", "突破瓶颈", "渡劫", "飞升", "成仙"]},
    "悬疑": {"structure_type": "悬疑小说", "base_structure": "草蛇灰线", "special_elements": ["谜题", "线索", "推理", "反转"], "key_plot_points": ["案件发生", "线索收集", "推理过程", "真相揭示", "反转"]},
    "科幻": {"structure_type": "科幻小说", "base_structure": "三幕式", "special_elements": ["科技设定", "未来世界", "科学原理", "技术应用"], "key_plot_points": ["科技背景", "技术挑战", "科学探索", "技术突破", "未来展望"]},
    "奇幻": {"structure_type": "奇幻小说", "base_structure": "英雄之旅", "special_elements": ["魔法体系", "异世界", "神秘生物", "魔法战斗"], "key_plot_points": ["进入异世界", "学习魔法", "冒险", "战斗", "拯救世界"]},
    "脑洞": {"structure_type": "脑洞小说", "base_structure": "碎片拼贴", "special_elements": ["新颖设定", "创意元素", "反套路", "出乎意料"], "key_plot_points": ["设定引入", "创意展开", "反套路", "意外转折", "创意收束"]},
    "都市": {"structure_type": "都市小说", "base_structure": "三幕式", "special_elements": ["现代背景", "都市生活", "职场", "商战"], "key_plot_points": ["都市生活", "职场挑战", "商战", "成功", "都市传奇"]},
    "历史": {"structure_type": "历史小说", "base_structure": "起承转合", "special_elements": ["历史背景", "历史事件", "历史人物", "时代特色"], "key_plot_points": ["历史背景", "卷入历史", "历史事件", "历史影响", "历史结局"]},
    "古言": {"structure_type": "古言小说", "base_structure": "三幕式", "special_elements": ["古代背景", "情感线", "宫廷", "权谋"], "key_plot_points": ["古代背景", "情感萌芽", "宫廷权谋", "情感考验", "圆满结局"]},
    "无CP": {"structure_type": "无CP小说", "base_structure": "升级流", "special_elements": ["专注事业", "无感情线", "实力提升", "目标达成"], "key_plot_points": ["目标设定", "努力奋斗", "实力提升", "克服困难", "达成目标"]},
    # 核心情节
    "穿越文": {"structure_type": "穿越文", "base_structure": "英雄之旅", "special_elements": ["时空穿越", "适应新环境", "文化差异", "新身份"], "key_plot_points": ["穿越", "适应", "融入", "改变", "新生活"]},
    "穿书文": {"structure_type": "穿书文", "base_structure": "三幕式", "special_elements": ["书中世界", "剧情预知", "改变剧情", "角色命运"], "key_plot_points": ["穿书", "了解剧情", "改变剧情", "避免悲剧", "新结局"]},
    "无限流": {"structure_type": "无限流", "base_structure": "碎片拼贴", "special_elements": ["副本世界", "任务系统", "生存挑战", "主神空间"], "key_plot_points": ["进入副本", "任务挑战", "生存", "通关", "回归"]},
    "复仇文": {"structure_type": "复仇文", "base_structure": "三幕式", "special_elements": ["仇恨", "复仇计划", "打脸", "复仇成功"], "key_plot_points": ["仇恨觉醒", "制定计划", "执行复仇", "打脸", "大仇得报"]},
    "升级流": {"structure_type": "升级流", "base_structure": "升级流", "special_elements": ["等级提升", "实力增长", "突破瓶颈", "不断变强"], "key_plot_points": ["初始等级", "提升", "突破", "变强", "巅峰"]},
    # 热门设定
    "爽文": {"structure_type": "爽文", "base_structure": "三幕式", "special_elements": ["爽点", "打脸", "逆袭", "畅快"], "key_plot_points": ["被轻视", "展现实力", "打脸", "震惊", "逆袭成功"]},
    "屌丝逆袭": {"structure_type": "屌丝逆袭", "base_structure": "英雄之旅", "special_elements": ["平凡出身", "逆袭", "成功", "人生巅峰"], "key_plot_points": ["平凡", "机遇", "努力", "逆袭", "成功"]},
    "废柴流": {"structure_type": "废柴流", "base_structure": "升级流", "special_elements": ["废柴开局", "天赋觉醒", "震惊众人", "逆袭"], "key_plot_points": ["废柴", "觉醒", "展现实力", "震惊", "逆袭"]},
    "打脸爽文": {"structure_type": "打脸爽文", "base_structure": "三幕式", "special_elements": ["被嘲讽", "展现实力", "打脸", "后悔"], "key_plot_points": ["被嘲讽", "展现实力", "打脸", "震惊", "后悔"]},
    "追妻火葬场": {"structure_type": "追妻火葬场", "base_structure": "三幕式", "special_elements": ["伤害", "离开", "追回", "道歉", "和解"], "key_plot_points": ["伤害", "离开", "醒悟", "追回", "和解"]},
    "马甲文": {"structure_type": "马甲文", "base_structure": "草蛇灰线", "special_elements": ["多重身份", "身份揭露", "震惊", "反转"], "key_plot_points": ["隐藏身份", "身份暗示", "身份揭露", "震惊", "反转"]},
    "真假千金": {"structure_type": "真假千金", "base_structure": "三幕式", "special_elements": ["身份互换", "身份揭露", "豪门恩怨", "真相"], "key_plot_points": ["身份互换", "生活对比", "身份揭露", "真相", "结局"]},
    "迪化文": {"structure_type": "迪化文", "base_structure": "三幕式", "special_elements": ["误解", "过度解读", "脑补", "反差"], "key_plot_points": ["普通行为", "被误解", "误解加深", "真相", "反差"]},
    "发疯文学": {"structure_type": "发疯文学", "base_structure": "三幕式", "special_elements": ["打破常规", "直接应对", "解气", "不按常理"], "key_plot_points": ["常规", "打破", "直接", "解气", "新常态"]},
    "虐文": {"structure_type": "虐文", "base_structure": "三幕式", "special_elements": ["情感痛苦", "曲折情节", "虐点", "虐心"], "key_plot_points": ["美好", "转折", "痛苦", "虐心", "结局"]},
    "CP塑造": {"structure_type": "CP塑造", "base_structure": "三幕式", "special_elements": ["CP互动", "情感发展", "关系变化", "感情线"], "key_plot_points": ["初遇", "互动", "发展", "考验", "圆满"]},
    # 背景职业
    "种田文": {"structure_type": "种田文", "base_structure": "升级流", "special_elements": ["种田", "经商", "发家致富", "建设"], "key_plot_points": ["开始种田", "收获", "扩大", "致富", "成功"]},
    "宫斗_宅斗": {"structure_type": "宫斗/宅斗", "base_structure": "草蛇灰线", "special_elements": ["权力斗争", "地位争夺", "人际关系", "算计"], "key_plot_points": ["进入", "斗争", "算计", "胜利", "地位"]},
    "末世文": {"structure_type": "末世文", "base_structure": "英雄之旅", "special_elements": ["末世环境", "生存危机", "资源争夺", "建立基地"], "key_plot_points": ["末世降临", "适应", "生存", "建立", "新秩序"]},
    "娱乐圈文": {"structure_type": "娱乐圈文", "base_structure": "升级流", "special_elements": ["演艺圈", "明星", "演戏", "综艺", "成名"], "key_plot_points": ["进入", "努力", "机会", "成名", "巅峰"]},
    "总裁文": {"structure_type": "总裁文", "base_structure": "三幕式", "special_elements": ["霸道总裁", "爱情", "现代背景", "商战"], "key_plot_points": ["相遇", "冲突", "心动", "考验", "圆满"]},
    "灵异文": {"structure_type": "灵异文", "base_structure": "悬疑", "special_elements": ["鬼怪", "灵异事件", "超自然", "解谜"], "key_plot_points": ["灵异事件", "调查", "真相", "解决", "结局"]},
    "赛博朋克": {"structure_type": "赛博朋克", "base_structure": "三幕式", "special_elements": ["未来科技", "社会矛盾", "虚拟现实", "反乌托邦"], "key_plot_points": ["未来世界", "矛盾", "反抗", "斗争", "改变"]},
    "商战文": {"structure_type": "商战文", "base_structure": "三幕式", "special_elements": ["商业竞争", "公司斗争", "商业策略", "成功"], "key_plot_points": ["进入", "竞争", "策略", "胜利", "成功"]},
    "冒险小说": {"structure_type": "冒险小说", "base_structure": "英雄之旅", "special_elements": ["探索", "未知", "危险", "冒险"], "key_plot_points": ["出发", "探索", "危险", "发现", "回归"]}
}

def generate_template(genre_name, config):
    """生成单个模板"""
    return {
        "structure_type": config["structure_type"],
        "description": f"{genre_name}类型小说大纲模板",
        "base_structure": config["base_structure"],
        "special_elements": config["special_elements"],
        "key_plot_points": config["key_plot_points"],
        "acts": [
            {
                "act": "第一幕：开端",
                "percentage": 25,
                "description": "建立背景和人物",
                "key_elements": config["special_elements"][:2] if len(config["special_elements"]) >= 2 else config["special_elements"],
                "plot_points": [config["key_plot_points"][0]] if len(config["key_plot_points"]) > 0 else []
            },
            {
                "act": "第二幕：发展",
                "percentage": 50,
                "description": "推进情节和冲突",
                "key_elements": config["special_elements"][1:3] if len(config["special_elements"]) >= 3 else config["special_elements"],
                "plot_points": config["key_plot_points"][1:-1] if len(config["key_plot_points"]) > 2 else config["key_plot_points"]
            },
            {
                "act": "第三幕：高潮与结局",
                "percentage": 25,
                "description": "高潮和收束",
                "key_elements": config["special_elements"][-2:] if len(config["special_elements"]) >= 2 else config["special_elements"],
                "plot_points": [config["key_plot_points"][-1]] if len(config["key_plot_points"]) > 0 else []
            }
        ],
        "chapter_distribution": {
            "total_chapters": 100,
            "act1_chapters": 25,
            "act2_chapters": 50,
            "act3_chapters": 25
        }
    }

if __name__ == "__main__":
    # 生成所有模板
    output_dir = Path(__file__).parent
    generated = 0
    
    for genre_name, config in GENRE_TEMPLATES.items():
        try:
            template = generate_template(genre_name, config)
            safe_name = genre_name.replace("/", "_")
            filename = f"{safe_name}_大纲模板.yaml"
            filepath = output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(template, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            
            print(f"已生成: {filename}")
            generated += 1
        except Exception as e:
            print(f"生成 {genre_name} 失败: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n总共生成了 {generated}/{len(GENRE_TEMPLATES)} 个类型大纲模板！")


