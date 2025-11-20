# 大纲模板目录

## 📚 模板说明

本目录包含所有小说大纲模板，包括：

### 通用结构模板（7个）

1. **三幕式大纲模板.yaml** - 经典三幕式结构
2. **起承转合式大纲模板.yaml** - 中国传统四段式
3. **英雄之旅大纲模板.yaml** - 12阶段英雄之旅
4. **草蛇灰线式大纲模板.yaml** - 伏笔布局结构
5. **碎片拼贴式大纲模板.yaml** - 非线性叙事
6. **弗莱塔格金字塔模板.yaml** - 五幕戏剧结构
7. **救猫咪15节拍模板.yaml** - 15节拍结构

### 类型特定模板（36个）

运行 `生成所有类型模板.py` 可以生成所有36种类型的模板：

```bash
python 生成所有类型模板.py
```

生成的模板包括：
- 基础类型（11个）：言情、玄幻、仙侠、悬疑、科幻、奇幻、脑洞、都市、历史、古言、无CP
- 核心情节（7个）：重生文、穿越文、穿书文、系统文、无限流、复仇文、升级流
- 热门设定（11个）：爽文、屌丝逆袭、废柴流、打脸爽文、追妻火葬场、马甲文、真假千金、迪化文、发疯文学、虐文、CP塑造
- 背景职业（8个）：种田文、宫斗/宅斗、末世文、娱乐圈文、总裁文、灵异文、赛博朋克、商战文、冒险小说

## 🎯 使用方法

### 1. 生成所有模板

```bash
cd outline_templates
python 生成所有类型模板.py
```

### 2. 在代码中使用

```python
from agents.planner import PlannerAgent

planner = PlannerAgent(llm_client, memory_manager)
outline = planner.generate_outline(structure, novel_type="重生文")
# 自动加载"重生文_大纲模板.yaml"
```

## 📋 模板格式

每个模板都是YAML格式，包含：

- `structure_type`: 结构类型
- `description`: 描述
- `base_structure`: 基础结构
- `special_elements`: 特殊元素
- `key_plot_points`: 关键情节点
- `acts`: 幕/阶段划分
- `chapter_distribution`: 章节分布

## ✅ 状态

- ✅ 通用模板：7个（已完成）
- ✅ 类型特定模板：36个（已生成）

