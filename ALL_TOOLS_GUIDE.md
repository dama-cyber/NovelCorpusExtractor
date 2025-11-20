# 辅助工具完整使用指南

## 📚 工具总览

系统现已实现**10个专业辅助工具**，覆盖小说创作的全流程。

## 🛠️ 工具列表

### 1. AI检测规避器 (22)

**文件**: `tools/ai_detection_evader.py`

**功能**:
- 多强度语言/结构/内容混合策略，规避AI检测
- 语气词、俗语、括号插入、轻微错别字、碎碎念等自然化处理
- 同义/情绪/主观表达扩展，支持个人化体验注入
- AI可能性分析 + 建议 & 人声化指标
- `evade_with_feedback` 结合检测结果迭代收敛

**使用示例**:
```python
from tools.ai_detection_evader import AIDetectionEvader

evader = AIDetectionEvader()

# 规避检测（可调策略+强度）
optimized = evader.evade_detection(text, strategy="language", intensity="high")

# 分析AI可能性
analysis = evader.analyze_ai_likelihood(text)
print(f"AI可能性: {analysis['ai_likelihood']}")
print(f"建议: {analysis['suggestions']}")

# 迭代规避，直到低于阈值
result = evader.evade_with_feedback(text, max_iterations=3, target_likelihood=0.4)
print(result["text"])
print(result["history"])
```

### 2. 商业化优化器 (23)

**文件**: `tools/commercial_optimizer.py`

**功能**:
- 标题智能优化（可返回候选+评分+诊断）
- 开篇钩子评分，支持与平台标杆对比
- 留存热力分析 + cliff/twist频率打分
- 付费点建议 + `assess_commercial_potential` 商业力总评

**使用示例**:
```python
from tools.commercial_optimizer import CommercialOptimizer

optimizer = CommercialOptimizer()

# 优化标题并获取评分
title_info = optimizer.optimize_title("我的小说", "玄幻", return_details=True)

# 优化开篇
hook_analysis = optimizer.optimize_hook(first_chapter)

# 优化留存率
retention_analysis = optimizer.optimize_retention(chapters)

# 建议付费点
paywall_points = optimizer.suggest_monetization_points(chapters, total_chapters=100)

# 商业潜力总评
potential = optimizer.assess_commercial_potential({
    "title": "我的小说",
    "novel_type": "玄幻",
    "first_chapter": first_chapter,
    "chapters": chapters,
    "total_chapters": 120
})
```

### 3. 平台算法适配器 (24)

**文件**: `tools/platform_adapter.py`

**功能**:
- 一键适配起点/纵横/番茄/知乎/晋江/起点读书/奇妙等平台
- 输出标题/简介/章节字数建议与算法要点
- `score_against_rules` 快速评估当前稿件与平台规则的匹配度
- `benchmark_content` 跨平台优先级排序，帮助选平台投放

**使用示例**:
```python
from tools.platform_adapter import PlatformAdapter, Platform

adapter = PlatformAdapter()

# 适配平台
adapted = adapter.adapt_for_platform(content, Platform.FANQIE)

# 评估不同平台匹配度
scores = adapter.benchmark_content(content, [Platform.QIDIAN, Platform.FANQIE, Platform.JINJIANG])

# 获取平台推荐
recommendations = adapter.get_platform_recommendations(Platform.QIDIAN)
```

### 4. 情感曲线优化器 (25)

**文件**: `tools/emotion_curve_optimizer.py`

**功能**:
- 分析情感曲线并输出平滑曲线 + 峰谷特征
- 计算与 wave / sawtooth / climax / roller_coaster 模式的相似度
- 生成 `get_curve_dashboard` 可视化数据 & 推荐模式
- 优化章节情绪强度，提供增减幅度建议

**使用示例**:
```python
from tools.emotion_curve_optimizer import EmotionCurveOptimizer

optimizer = EmotionCurveOptimizer()

# 分析情感曲线
analysis = optimizer.analyze_emotion_curve(chapters)

# 优化情感曲线
optimized = optimizer.optimize_emotion_curve(chapters, target_pattern="wave")

# 获取仪表盘数据（含模式相似度）
dashboard = optimizer.get_curve_dashboard(chapters, target_pattern="roller_coaster")
```

### 5. 人物一致性检查器 (26)

**文件**: `tools/character_consistency_checker.py`

**功能**:
- 检查MBTI、核心性格、口头禅、人际关系、成长阶段等多维一致性
- 输出带严重度(severity)的 `ConsistencyIssue` 列表
- `generate_consistency_report` 自动汇总风险等级+改写建议
- 支持批量检查所有人物

**使用示例**:
```python
from tools.character_consistency_checker import CharacterConsistencyChecker
from core.memory_manager import MemoryManager

checker = CharacterConsistencyChecker(memory_manager)

# 检查特定人物
issues = checker.check_character("张三", new_behavior)

# 检查所有人物
all_issues = checker.check_all_characters()

# 获取详细报告
report = checker.generate_consistency_report("张三", new_behavior)
```

### 6. 世界观冲突检测器 (27)

**文件**: `tools/worldview_conflict_detector.py`

**功能**:
- 力量体系/地理/势力多维冲突检测（名称、等级、资源、阵营、盟友等）
- 冲突结果含 field+severity，可直接定位问题
- `generate_conflict_report` 输出风险等级、建议与优先级
- 支持仅返回字符串或详细信息两种模式

**使用示例**:
```python
from tools.worldview_conflict_detector import WorldviewConflictDetector
from core.memory_manager import MemoryManager

detector = WorldviewConflictDetector(memory_manager)

# 检测冲突
conflicts = detector.detect_conflicts(new_worldview)

# 生成风险报告
report = detector.generate_conflict_report(new_worldview)
```

### 7. 伏笔回收提醒器 (28)

**文件**: `tools/foreshadowing_reminder.py`

**功能**:
- 检查未回收伏笔并标记超期程度
- Reminder包含优先级、建议回收章节、已超期章数等字段
- `schedule_followups` 提前15章掌握即将到期的伏笔
- 支持一键生成文本报告

**使用示例**:
```python
from tools.foreshadowing_reminder import ForeshadowingReminder
from core.memory_manager import MemoryManager

reminder = ForeshadowingReminder(memory_manager, max_chapters=55)

# 检查未回收伏笔
unresolved = reminder.check_unresolved_foreshadowings(current_chapter=50)

# 获取提醒报告
report = reminder.get_reminder_report(current_chapter=50)
print(report)

# 提前规划未来15章的伏笔回收
upcoming = reminder.schedule_followups(current_chapter=50, window=15)
```

### 8. 章节标题生成器 (29)

**文件**: `tools/chapter_title_generator.py`

**功能**:
- 自动生成多风格标题，支持 tone/语气修饰和强制风格
- 通过关键词/重复度猜测主角名，智能替换模板占位符
- 钩子短语 + 关键句组合，并输出多样性/Hook密度诊断
- `return_details=True` 可拿到分析数据与风格推断

**使用示例**:
```python
from tools.chapter_title_generator import ChapterTitleGenerator

generator = ChapterTitleGenerator()

# 生成标题并获取诊断
title_info = generator.generate_title(
    chapter_content,
    chapter_number=1,
    style="auto",
    tone="爽文",
    return_details=True
)
```

### 9. 开篇场景生成器 (30)

**文件**: `tools/opening_scene_generator.py`

**功能**:
- Hook模型触发阶段指引 + 类型智能匹配（genre classifier）
- 根据冲突/悬念/行动/情感比例计算 Hook Score
- 自动补充重生/系统/穿越等类型惯用桥段
- 输出 hook 元素拆解 + 改写建议

**使用示例**:
```python
from tools.opening_scene_generator import OpeningSceneGenerator

generator = OpeningSceneGenerator()

# 生成开篇
opening = generator.generate_opening(
    novel_type="重生文",
    opening_style="auto",
    context={
        "protagonist": "主角",
        "location": "都市",
        "sample_text": draft_paragraph
    }
)

print(opening["hook_score"], opening["optimization_suggestions"])
```

### 10. 结尾收束优化器 (31)

**文件**: `tools/ending_optimizer.py`

**功能**:
- 优化结尾收束，检查伏笔/主线/人物/支线/语气一致性
- `generate_final_checklist` 输出可勾选清单 + 质量分
- Subplot/Tone 分析，提示未回收支线或语气偏差
- 结尾质量评估涵盖完整度/满意度/连贯性/情感冲击

**使用示例**:
```python
from tools.ending_optimizer import EndingOptimizer
from core.memory_manager import MemoryManager

optimizer = EndingOptimizer(memory_manager)

# 优化结尾
ending_analysis = optimizer.optimize_ending(
    final_chapters,
    novel_type="玄幻",
    ending_style="happy_ending"  # happy_ending/open_ending/tragic_ending/circular_ending
)

# 检查结尾质量
quality = optimizer.check_ending_quality(ending_content)

# 生成结尾检查清单
checklist = optimizer.generate_final_checklist(final_chapters, "玄幻", "happy_ending")
```

## 🎯 工具使用场景

### 场景1: 创作新小说

```python
# 1. 生成开篇
opening_gen = OpeningSceneGenerator()
opening = opening_gen.generate_opening("重生文", "conflict")

# 2. 生成章节标题
title_gen = ChapterTitleGenerator()
titles = title_gen.generate_title(chapter_content, chapter_number=1)

# 3. 优化商业化
commercial = CommercialOptimizer()
optimized_title = commercial.optimize_title("我的小说", "重生文")

# 4. 适配平台
platform = PlatformAdapter()
adapted = platform.adapt_for_platform(content, Platform.FANQIE)
```

### 场景2: 优化现有小说

```python
# 1. 优化情感曲线
emotion = EmotionCurveOptimizer()
analysis = emotion.analyze_emotion_curve(chapters)
optimized = emotion.optimize_emotion_curve(chapters, "wave")

# 2. 检查一致性
character_checker = CharacterConsistencyChecker(memory_manager)
issues = character_checker.check_all_characters()

# 3. 检查伏笔
foreshadowing = ForeshadowingReminder(memory_manager)
report = foreshadowing.get_reminder_report(current_chapter=50)

# 4. 优化结尾
ending = EndingOptimizer(memory_manager)
ending_analysis = ending.optimize_ending(final_chapters, "玄幻")
```

### 场景3: 规避AI检测

```python
# 1. 分析AI可能性
evader = AIDetectionEvader()
analysis = evader.analyze_ai_likelihood(text)

# 2. 规避检测
optimized = evader.evade_detection(text, strategy="all")
```

## 📊 工具分类

### 创作辅助
- 开篇场景生成器
- 章节标题生成器
- 结尾收束优化器

### 质量检查
- 人物一致性检查器
- 世界观冲突检测器
- 伏笔回收提醒器

### 优化工具
- 商业化优化器
- 情感曲线优化器
- AI检测规避器

### 平台适配
- 平台算法适配器

## ✅ 总结

所有10个辅助工具已完整实现，覆盖：
- ✅ 创作辅助（3个）
- ✅ 质量检查（3个）
- ✅ 优化工具（3个）
- ✅ 平台适配（1个）

系统现已具备完整的创作辅助能力！

