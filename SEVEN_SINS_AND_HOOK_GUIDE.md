# 七宗罪与Hook模型使用指南

## 📚 概述

系统现已集成两大理论框架：

1. **七宗罪反派人性刻画理论框架** - 用于分析和塑造反派角色
2. **基于Hook模型的网络小说写作策略** - 用于指导情节设计和节奏控制

## 🎭 七宗罪反派分析

### 支持的七种反派类型

1. **傲慢 (Pride)** - 过度以自我为中心，夸大自我价值
2. **嫉妒 (Envy)** - 对他人的成功心怀不满和怨恨
3. **愤怒 (Wrath)** - 难以遏制的暴怒、仇恨与冲动
4. **懒惰 (Sloth)** - 怠于尽责、贪图安逸
5. **贪婪 (Greed)** - 无止境的占有欲和欲壑难填
6. **暴食 (Gluttony)** - 无节制的纵欲和沉迷
7. **色欲 (Lust)** - 沉溺于不道德的情欲和肉欲

### 使用方法

#### 1. 分析反派角色

```python
from core.villain_analysis import VillainAnalyzer

analyzer = VillainAnalyzer()

# 分析反派
villain_desc = "一个傲慢自大的宗门天才，目中无人，看不起主角"
scores = analyzer.analyze_villain(villain_desc)
primary_sin = analyzer.get_primary_sin(villain_desc)

# 获取分析
if primary_sin:
    sin, score = primary_sin
    guidance = analyzer.generate_villain_guidance(sin)
    print(guidance)
```

#### 2. 创建反派角色

```python
from tools.villain_creator import VillainCreator
from core.villain_analysis import SevenDeadlySins

creator = VillainCreator()
villain = creator.create_villain(
    sin=SevenDeadlySins.PRIDE,
    name="魂天帝",
    story_context="玄幻小说，最终BOSS"
)
```

#### 3. 在分析中使用

系统会在分析文本时自动识别和分析反派角色：

```python
from agents.analyst import AnalystAgent

analyst = AnalystAgent(llm_client)
result = analyst.analyze_chunk(chunk, novel_type="玄幻")

# 结果中包含反派分析
villain_analysis = result.get("villain_analysis", {})
```

## 🎣 Hook模型写作指导

### 四个阶段

1. **触发 (Trigger)** - 引爆读者兴趣
2. **行动 (Action)** - 促使持续阅读
3. **奖励 (Reward)** - 制造不确定性的爽点
4. **投入 (Investment)** - 积累沉没成本与情感依赖

### 使用方法

#### 1. 分析章节

```python
from core.hook_model import HookModelGuide

guide = HookModelGuide()

# 分析章节的Hook应用
scores = guide.analyze_chapter(chapter_content, chapter_number=1)
print(scores)
# 输出: {HookStage.TRIGGER: 0.8, HookStage.ACTION: 0.6, ...}
```

#### 2. 获取阶段指导

```python
from core.hook_model import HookStage

# 获取触发阶段指导
guidance = guide.generate_stage_guidance(HookStage.TRIGGER)
print(guidance)
```

#### 3. 优化章节

```python
from tools.hook_optimizer import HookOptimizer

optimizer = HookOptimizer()
result = optimizer.optimize_chapter(chapter_content, chapter_number=1)

print(result["suggestions"])
print(result["stage_guidance"])
```

#### 4. 在分析中使用

系统会在分析章节时自动应用Hook模型：

```python
result = analyst.analyze_chunk(chunk, novel_type="玄幻")

# 结果中包含Hook分析
hook_analysis = result.get("hook_analysis", {})
```

## 🎯 实际应用

### 场景1: 创建傲慢型反派

```python
from tools.villain_creator import VillainCreator
from core.villain_analysis import SevenDeadlySins

creator = VillainCreator()
villain = creator.create_villain(
    sin=SevenDeadlySins.PRIDE,
    name="宗门天才",
    story_context="玄幻小说，主角的同门师兄"
)

# 获取创建提示词
prompt = creator.generate_villain_prompt(
    SevenDeadlySins.PRIDE,
    story_context
)
```

### 场景2: 优化开篇章节

```python
from tools.hook_optimizer import HookOptimizer
from core.hook_model import HookStage

optimizer = HookOptimizer()

# 优化第一章（触发阶段）
result = optimizer.optimize_chapter(chapter_1_content, chapter_number=1)

# 获取触发阶段指导
prompt = optimizer.generate_hook_prompt(
    HookStage.TRIGGER,
    context=chapter_1_content
)
```

### 场景3: 分析现有文本

```python
from agents.analyst import AnalystAgent

analyst = AnalystAgent(llm_client)

# 分析文本块
chunk = {
    "text": "主角被退婚羞辱，愤怒发誓要逆袭...",
    "chunk_id": "chapter_1_1"
}

result = analyst.analyze_chunk(chunk, novel_type="玄幻")

# 查看反派分析
if result.get("villain_analysis"):
    for name, analysis in result["villain_analysis"].items():
        print(f"反派: {name}")
        print(f"罪: {analysis['sin']}")
        print(f"匹配度: {analysis['score']}")

# 查看Hook分析
hook_scores = result.get("hook_analysis", {})
print("Hook模型得分:", hook_scores)
```

## 📊 理论框架详情

### 七宗罪框架结构

每个罪包含：
- **心理分析**: 心理动因和性格特征
- **文学象征意义**: 道德隐喻和社会批判
- **叙事功能**: 在情节中的作用
- **关键特征**: 典型性格特点
- **关键情节点**: 典型情节发展
- **典型案例**: 代表性反派角色

### Hook模型框架结构

每个阶段包含：
- **目标**: 该阶段要达到的目的
- **机制解析**: 如何实现目标
- **写作策略**: 具体写作技巧
- **关键提示语**: 可用的关键词和句式
- **注意事项**: 需要避免的问题

## ✅ 集成状态

- ✅ 七宗罪反派分析器 (`core/villain_analysis.py`)
- ✅ Hook模型指导器 (`core/hook_model.py`)
- ✅ 反派创建工具 (`tools/villain_creator.py`)
- ✅ Hook优化工具 (`tools/hook_optimizer.py`)
- ✅ AnalystAgent集成（自动分析反派和Hook应用）

## 📝 使用建议

1. **创建反派时**: 使用七宗罪框架确保反派有明确的人性弱点和动机
2. **写作章节时**: 根据章节位置应用相应的Hook阶段指导
3. **分析文本时**: 系统会自动识别反派类型和Hook应用情况
4. **优化内容时**: 使用工具获取具体的改进建议

---

**总结**: 两大理论框架已完整集成到系统中，可在创作和分析过程中自动应用，帮助提升作品质量。

