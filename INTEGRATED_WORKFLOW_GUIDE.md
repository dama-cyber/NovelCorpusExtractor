# 整合工作流使用指南

本文档说明如何使用整合工作流（拆书+七步创作方法论）进行小说创作。

## 📋 工作流概述

整合工作流将拆书提炼语料和七步创作方法论整合在一起，形成一个完整的创作流程：

```
拆书提炼语料 → 七步创作方法论 → 完成作品
```

## 🔄 完整流程

### 阶段 0：拆书提炼语料（可选）

**目标**：从优秀小说中提取高价值片段，构建可复用的语料库

**流程**：
1. **Reader** → 读取和分块小说文本
2. **Scanner** → 语义预检，过滤低价值块
3. **Analyst** → 深度分析文本块
4. **Extractor** → 提取高价值片段
5. **Archivist** → 归档到记忆体
6. **Planner** → 生成剧情大纲

**输出**：
- 语料库片段（`corpus_samples/*.txt`）

> **注意**：如果是从零开始创作，可以跳过此阶段。世界观记忆体、人物记忆体、剧情大纲和伏笔追踪表会在七步创作方法论的相应阶段自动创建。

### 阶段 1：Constitution（建立创作原则）

**功能**：
- 定义不可妥协的写作原则
- 制定风格指南
- 确定核心价值观
- 建立世界观一致性规则
- 建立角色一致性规则

**输出**：创作原则文档

---

### 阶段 2：Specify（定义故事需求）⭐ **自动创建世界观和人物记忆体**

**功能**：
- 定义故事概述
- 确定目标受众和目标平台
- 定义故事类型和风格
- 确定核心冲突和主题
- 描述主要角色
- 选择故事结构
- 定义成功标准
- 规划商业化策略

**自动创建**：
- ✅ **世界观记忆体**（`02_世界观记忆体.yaml`）
  - 世界背景
  - 力量体系
  - 规则设定
  - 重要地点
  - 组织势力
  - 历史背景

- ✅ **人物记忆体**（`03_人物记忆体.yaml`）
  - 角色姓名、性格、背景
  - 能力/技能
  - 外貌描述
  - 角色定位
  - 角色关系
  - 成长目标

**输出**：
- 故事需求规范（类似 PRD）
- 世界观记忆体文件
- 人物记忆体文件

---

### 阶段 3：Clarify（关键澄清）

**功能**：
- AI 识别规范中的歧义
- 生成最多 5 个关键问题
- 提供建议答案

**输出**：澄清问题和答案

---

### 阶段 4：Plan（创作计划）⭐ **自动创建剧情大纲和伏笔追踪表**

**功能**：
- 规划章节结构
- 设计角色弧线
- 构建世界观（如果需要补充）
- 规划情节时间线
- 布局伏笔
- 规划情绪曲线
- 规划 Hook 点
- 制定语料库使用策略

**自动创建**：
- ✅ **剧情规划大纲**（`04_剧情规划大纲.yaml`）
  - 总体结构（卷/幕的划分）
  - 每章的核心事件
  - 主要冲突和高潮
  - 人物成长弧线
  - 时间线
  - 关键情节点

- ✅ **伏笔追踪表**（`05_伏笔追踪表.yaml`）
  - 伏笔内容
  - 埋设章节
  - 回收章节
  - 伏笔类型
  - 关联角色
  - 重要性

**输出**：
- 详细创作计划
- 剧情规划大纲文件
- 伏笔追踪表文件

---

### 阶段 5：Tasks（任务分解）

**功能**：
- 将计划分解为可执行的写作任务
- 为每个任务设置优先级
- 定义任务依赖关系
- 估算工作量
- 定义验收标准
- 为每个章节任务生成 2-3 个候选标题
- 标注建议使用的语料库片段类型

**输出**：任务列表（JSON 格式）

---

### 阶段 6：Write（执行写作）⭐ **多个Agent协同工作**

**使用的Agent**：
- **Analyst**：分析任务需求
- **Extractor**：从语料库检索相关片段
- **Planner**：规划写作结构
- **Stylist**：优化文本风格

**功能**：
- 根据任务描述从语料库检索相关片段
- 使用 LLM 将语料库片段适配到当前任务
- 替换专有名词为当前故事中的角色和地点
- 保持情节逻辑连贯
- 确保风格与整体作品一致
- 使用记忆体确保设定一致性

**工作流程**：
```
任务描述
    ↓
[Analyst] 分析任务需求
    ↓
[Extractor] 从语料库检索相关片段（top_k=3）
    ↓
[Planner] 规划写作结构（参考剧情大纲）
    ↓
构建包含语料库片段和记忆体的提示词
    ↓
LLM 生成适配后的文本
    ↓
[Stylist] 优化文本风格
    ↓
输出最终文本
```

**使用的记忆体**：
- 世界观记忆体（确保世界观设定一致）
- 人物记忆体（确保角色行为符合设定）
- 剧情大纲（确保情节符合规划）
- 伏笔追踪表（确保伏笔正确埋设）

**输出**：
- 生成的文本内容
- 使用的语料库片段 ID
- 缝合统计信息

---

### 阶段 7：Analyze（全面验证）

**功能**：
- 验证情节一致性
- 验证时间线准确性
- 检查角色发展（使用角色一致性检查器）
- 验证创作原则遵循
- 检查规范符合度
- 检查伏笔处理（使用伏笔提醒器）
- 验证风格一致性
- 检查世界观一致性（使用世界观冲突检测器）
- 评估 AI 检测风险（使用 AI 检测规避器）

**输出**：
- 质量分析报告
- 问题列表（带严重程度和修复建议）
- 创作工具检测结果

## 📚 记忆体系统

### 记忆体文件说明

| 文件 | 创建阶段 | 说明 |
|------|---------|------|
| `02_世界观记忆体.yaml` | Specify | 世界观设定，包括世界背景、力量体系、规则设定等 |
| `03_人物记忆体.yaml` | Specify | 主要角色信息，包括性格、背景、能力、关系等 |
| `04_剧情规划大纲.yaml` | Plan | 详细的剧情大纲，包括章节结构、关键情节点等 |
| `05_伏笔追踪表.yaml` | Plan | 所有伏笔的埋设和回收计划 |

### 记忆体的使用

记忆体在以下阶段被使用：

1. **Plan 阶段**：参考世界观和人物记忆体制定创作计划
2. **Write 阶段**：确保写作内容与记忆体一致
3. **Analyze 阶段**：验证内容与记忆体的一致性

## 🎯 使用示例

### 完整流程示例

```python
from core.workflows import WorkflowFactory
from core.memory_manager import MemoryManager
from core.frankentexts import FrankentextsManager

# 1. 初始化
memory_manager = MemoryManager(output_dir="output")
frankentexts_manager = FrankentextsManager("corpus_samples")

# 2. 初始化Agent
from agents import ReaderAgent, AnalystAgent, ExtractorAgent, ArchivistAgent, PlannerAgent, StylistAgent

agents = {
    "reader": ReaderAgent(),
    "analyst": AnalystAgent(llm_client, memory_manager),
    "extractor": ExtractorAgent(llm_client, frankentexts_manager),
    "archivist": ArchivistAgent(memory_manager),
    "planner": PlannerAgent(llm_client, memory_manager),
    "stylist": StylistAgent(llm_client)
}

# 3. 创建整合工作流
workflow = WorkflowFactory.create_workflow(
    "integrated",
    project_id="my_novel",
    card_manager=card_manager,
    project_manager=project_manager,
    llm_client=llm_client,
    memory_manager=memory_manager,
    frankentexts_manager=frankentexts_manager,
    agents=agents
)

# 4. 执行工作流
stages = workflow.get_stages()

# 阶段 0：拆书（可选）
if input_file:
    disassemble_result = await workflow.expand_stage(stages[0])
    print(f"拆书完成：提取 {disassemble_result['results']['fragments_extracted']} 个片段")

# 阶段 1：建立创作原则
constitution = await workflow.expand_stage(stages[1])

# 阶段 2：定义故事需求（自动创建世界观和人物记忆体）
specification = await workflow.expand_stage(
    stages[2],
    parent_card_id=constitution['card_id']
)
print(f"已创建记忆体：{specification['memory_files_created']}")

# 阶段 3：关键澄清
clarifications = await workflow.expand_stage(
    stages[3],
    parent_card_id=specification['card_id']
)

# 阶段 4：创作计划（自动创建剧情大纲和伏笔追踪表）
plan = await workflow.expand_stage(
    stages[4],
    parent_card_id=clarifications['card_id']
)
print(f"已创建记忆体：{plan['memory_files_created']}")

# 阶段 5：任务分解
tasks = await workflow.expand_stage(
    stages[5],
    parent_card_id=plan['card_id']
)

# 阶段 6：执行写作（多个Agent协同）
while True:
    writing_result = await workflow.expand_stage(
        stages[6],
        parent_card_id=tasks['card_id']
    )
    print(f"任务完成：{writing_result['task']['description']}")
    print(f"使用了 {writing_result['corpus_fragment_count']} 个语料库片段")
    print(f"使用的Agent：{writing_result['agents_used']}")
    
    if not writing_result.get('has_more_tasks'):
        break

# 阶段 7：全面验证
analysis = await workflow.expand_stage(
    stages[7],
    parent_card_id=writing_result['card_id']
)
print(f"发现 {len(analysis['issues'])} 个问题")
```

## 🔑 关键优势

1. **完整的创作闭环**
   - 从语料提取到文本生成
   - 从规划到验证
   - 全流程自动化

2. **自动创建记忆体**
   - 在 Specify 阶段自动创建世界观和人物记忆体
   - 在 Plan 阶段自动创建剧情大纲和伏笔追踪表
   - 确保设定一致性

3. **多Agent协同**
   - 写作阶段多个Agent协同工作
   - 每个Agent发挥专业优势
   - 提高创作质量

4. **智能缝合机制**
   - 自动检索相关片段
   - 智能适配到当前故事
   - 保持风格一致性

5. **质量保证**
   - 多工具协同检测
   - 早期发现问题
   - 自动化修复建议

## 📝 总结

整合工作流实现了：

- **拆书提炼语料**：从优秀小说中提取可复用片段
- **七步创作方法论**：结构化的创作流程
- **自动创建记忆体**：确保设定一致性
- **多Agent协同**：提高创作质量
- **智能缝合**：将语料库片段适配到新故事

这个系统实现了从"提取优秀片段"到"生成新作品"的完整闭环，大大提高了创作效率和质量。

---

**最后更新**: 2025-01-XX
**版本**: 1.0.0


