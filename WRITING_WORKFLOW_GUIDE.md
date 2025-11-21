# 完整写作流程指南

本文档详细说明 NovelCorpusExtractor 项目的完整写作流程，包括所有工作流、Agent 模块和创作工具的使用方法。

> **重要更新**：系统现已完全整合语料库提取、七步创作方法论和创作工具，形成一个完整的写作系统。详细整合方案请参考 [INTEGRATED_WRITING_SYSTEM.md](./INTEGRATED_WRITING_SYSTEM.md)

## 📋 目录

1. [系统概述](#系统概述)
2. [核心工作流](#核心工作流)
3. [Agent 模块](#agent-模块)
4. [创作工具](#创作工具)
5. [七步方法论工作流](#七步方法论工作流)
6. [语料库缝合机制](#语料库缝合机制) ⭐ **新增**
7. [创作工具与七步方法论映射](#创作工具与七步方法论映射) ⭐ **新增**
8. [使用流程](#使用流程)
9. [输出文件说明](#输出文件说明)

---

## 系统概述

NovelCorpusExtractor 是一个基于多智能体架构的小说语料提取和创作辅助系统。系统通过多个 Agent 协作，完成从文本分析到创作优化的全流程。

### 核心特性

- ✅ **多智能体协作**：Reader、Analyst、Archivist 等 Agent 协同工作
- ✅ **多种拓扑模式**：线性、三角、蜂群模式，根据 API 数量自动选择
- ✅ **创作工作流**：10 大创作工具，覆盖从开篇到结尾的全流程
- ✅ **七步方法论**：基于 qcbigma 的七步创作方法论
- ✅ **记忆体系统**：自动提取和管理世界观、人物、剧情等记忆体
- ✅ **仅 API 模式**：所有 LLM 功能通过外部 API 提供

---

## 核心工作流

### 1. 语料提取工作流

这是系统的主要工作流，用于从原始小说文本中提取结构化信息。

#### 流程步骤

```
输入文件/文本
    ↓
[Reader] 读取和分块
    ↓
[Analyst] 分析文本块
    ↓
[Archivist] 归档记忆体
    ↓
[Planner] 生成大纲
    ↓
[Creative Workflow] 创作优化
    ↓
输出记忆体和语料库
```

#### 详细说明

1. **Reader（读取者）**
   - 读取小说文件（支持 .txt、.md、.json）
   - 将文本分割成固定大小的块（默认 1024 tokens）
   - 处理文本编码和格式

2. **Analyst（分析者）**
   - 分析每个文本块的内容
   - 提取主题、情感、关键信息
   - 计算 Hook 评分

3. **Archivist（归档员）**
   - 将分析结果归档到记忆体
   - 更新世界观记忆体
   - 更新人物记忆体
   - 生成剧情大纲

4. **Planner（规划者）**
   - 分析整体结构
   - 生成剧情大纲
   - 识别伏笔和关键情节

5. **Creative Workflow（创作工作流）**
   - 运行 10 大创作工具
   - 优化开篇、标题、商业化等
   - 检测角色一致性、伏笔等

---

## Agent 模块

### 1. Reader（读取者）

**文件**: `agents/reader.py`

**功能**:
- 读取小说文件
- 文本分块处理
- 编码处理

**输入**: 文件路径
**输出**: 文本块列表

### 2. Analyst（分析者）

**文件**: `agents/analyst.py`

**功能**:
- 分析文本块内容
- 提取主题和情感
- 计算 Hook 评分

**输入**: 文本块
**输出**: 分析结果（主题、情感、Hook 评分等）

### 3. Archivist（归档员）

**文件**: `agents/archivist.py`

**功能**:
- 归档分析结果
- 更新记忆体文件
- 管理世界观和人物信息

**输入**: 分析结果
**输出**: 记忆体文件（YAML 格式）

### 4. Scanner（扫描者）

**文件**: `agents/scanner.py`

**功能**:
- 快速扫描文本
- 识别关键信息
- 初步分类

**输入**: 文本块
**输出**: 扫描结果

### 5. Extractor（深度提取者）

**文件**: `agents/extractor.py`

**功能**:
- 深度提取信息
- 提取人物关系
- 提取世界观设定

**输入**: 文本块
**输出**: 深度提取结果

### 6. Planner（规划者）

**文件**: `agents/planner.py`

**功能**:
- 分析故事结构
- 生成剧情大纲
- 规划章节结构

**输入**: 文本块列表
**输出**: 剧情大纲

### 7. Stylist（风格 Agent）

**文件**: `agents/stylist.py`

**功能**:
- 分析写作风格
- 提取风格特征
- 生成风格指南

**输入**: 文本块
**输出**: 风格分析结果

---

## 创作工具

创作工作流包含 10 大创作工具，分为三个流程：

### Creation Flow（创作流程）

1. **Opening Scene Generator（开篇场景生成器）**
   - 生成吸引人的开篇场景
   - 支持多种开篇风格
   - 文件: `tools/opening_scene_generator.py`

2. **Chapter Title Generator（章节标题生成器）**
   - 生成章节标题
   - 支持多种标题风格
   - 文件: `tools/chapter_title_generator.py`

3. **Commercial Optimizer（商业化优化器）**
   - 优化标题和简介的商业化程度
   - 提高吸引力
   - 文件: `tools/commercial_optimizer.py`

4. **Platform Adapter（平台适配器）**
   - 适配不同平台规则
   - 支持番茄小说、起点等平台
   - 文件: `tools/platform_adapter.py`

5. **Hook Optimizer（Hook 优化器）**
   - 优化章节 Hook
   - 提高读者留存
   - 文件: `tools/hook_optimizer.py`

### Optimization Flow（优化流程）

6. **Emotion Curve Optimizer（情感曲线优化器）**
   - 优化情感曲线
   - 控制节奏
   - 文件: `tools/emotion_curve_optimizer.py`

7. **Character Consistency Checker（角色一致性检查器）**
   - 检查角色行为一致性
   - 发现角色设定冲突
   - 文件: `tools/character_consistency_checker.py`

8. **Foreshadowing Reminder（伏笔提醒器）**
   - 追踪伏笔
   - 提醒回收伏笔
   - 文件: `tools/foreshadowing_reminder.py`

9. **Ending Optimizer（结尾优化器）**
   - 优化结尾
   - 生成多种结尾方案
   - 文件: `tools/ending_optimizer.py`

10. **Worldview Conflict Detector（世界观冲突检测器）**
    - 检测世界观设定冲突
    - 发现逻辑漏洞
    - 文件: `tools/worldview_conflict_detector.py`

### Detection Flow（检测流程）

11. **AI Detection Evader（AI 检测规避器）**
    - 降低 AI 检测概率
    - 提高文本自然度
    - 文件: `tools/ai_detection_evader.py`

---

## 七步方法论工作流

基于 qcbigma 的七步创作方法论，用于从零开始创作小说。现已完全整合创作工具和语料库缝合功能。

### 七个阶段

1. **Constitution（建立创作原则）**
   - 定义不可妥协的写作原则
   - 制定风格指南
   - 确定核心价值观
   - **整合工具**：世界观冲突检测器、角色一致性检查器

2. **Specify（定义故事需求）**
   - 定义故事概述
   - 确定目标受众和目标平台
   - 设定成功标准
   - **整合工具**：商业化优化器、平台适配器

3. **Clarify（关键澄清）**
   - AI 识别规范中的歧义
   - 生成最多 5 个关键问题
   - 提供建议答案
   - **整合工具**：Hook 优化器、开篇场景生成器

4. **Plan（创作计划）**
   - 将抽象需求转化为具体方案
   - 规划章节结构
   - 设计角色弧线
   - 规划情绪曲线和伏笔布局
   - **整合工具**：情绪曲线优化器、伏笔提醒器

5. **Tasks（任务分解）**
   - 将计划分解为可执行任务
   - 设置优先级
   - 定义验收标准
   - 为每个任务生成候选标题
   - **整合工具**：章节标题生成器

6. **Write（执行写作）** ⭐ **核心缝合阶段**
   - 基于任务列表进行写作
   - **自动从语料库检索相关片段**
   - **使用 LLM 将片段适配到当前任务**
   - 遵循创作原则
   - 符合故事规范
   - **整合工具**：语料库缝合、AI 检测规避器

7. **Analyze（全面验证）**
   - 验证情节一致性
   - 检查时间线准确性
   - 发现并修复问题
   - **整合工具**：所有检测工具（角色一致性、世界观冲突、伏笔、AI 检测等）

### 使用方式

```python
from core.workflows import WorkflowFactory
from core.card_manager import CardManager
from core.project_manager import ProjectManager
from core.frankentexts import FrankentextsManager
from core.creative_workflow import CreativeWorkflowPipeline

# 初始化语料库管理器
frankentexts_manager = FrankentextsManager("corpus_samples")

# 创建工作流
workflow = WorkflowFactory.create_workflow(
    "seven_step",
    project_id="my_project",
    card_manager=card_manager,
    project_manager=project_manager,
    llm_client=llm_client
)

# 设置语料库管理器（用于 Write 阶段的缝合）
workflow.frankentexts_manager = frankentexts_manager

# 设置创作工具（用于各阶段的辅助）
creative_pipeline = CreativeWorkflowPipeline(memory_manager)
workflow.character_checker = creative_pipeline.character_checker
workflow.worldview_detector = creative_pipeline.worldview_detector
workflow.ai_evader = creative_pipeline.ai_evader
workflow.foreshadowing_reminder = creative_pipeline.foreshadowing_reminder

# 执行七步流程
stages = workflow.get_stages()

# 1. Constitution
constitution = await workflow.expand_stage(stages[0])

# 2. Specify
specification = await workflow.expand_stage(stages[1], constitution['card_id'])

# 3. Clarify
clarifications = await workflow.expand_stage(stages[2], specification['card_id'])

# 4. Plan
plan = await workflow.expand_stage(stages[3], clarifications['card_id'])

# 5. Tasks
tasks = await workflow.expand_stage(stages[4], plan['card_id'])

# 6. Write（自动使用语料库缝合）
writing_result = await workflow.expand_stage(stages[5], tasks['card_id'])
print(f"使用了 {writing_result['corpus_fragment_count']} 个语料库片段")

# 7. Analyze（使用所有检测工具）
analysis = await workflow.expand_stage(stages[6], writing_result['card_id'])
print(f"发现 {len(analysis['issues'])} 个问题")
```

## 语料库缝合机制 ⭐

### 核心概念

语料库缝合是系统的核心功能，用于在 Write 阶段从语料库中检索相关片段，并将其智能适配到当前写作任务中。

### 工作流程

```
任务描述
    ↓
从语料库检索相关片段（根据任务描述和小说类型）
    ↓
LLM 将片段适配到当前任务
    - 替换专有名词
    - 调整情节逻辑
    - 保持风格一致
    ↓
生成适配后的文本
    ↓
AI 检测规避优化
    ↓
输出最终文本
```

### 语料库片段类型

语料库中的片段按以下维度分类：
- **场景类型**：战斗场景、对话场景、环境描写、心理描写等
- **情节类型**：开篇、转折、高潮、结尾等
- **小说类型**：玄幻、言情、悬疑等 36+ 种类型

### 模板化处理

语料库片段经过模板化处理：
- 专有名词替换为占位符（如 `{主角名}`、`{地点名}`）
- 保留结构和风格
- 便于适配到不同故事

### 使用示例

```python
# 在 Write 阶段，系统会自动：
# 1. 根据任务描述检索相关片段
fragments = frankentexts_manager.search_fragments(
    query="第一章开篇场景，重生文",
    genre="重生文",
    top_k=3
)

# 2. 将片段提供给 LLM 进行适配
# LLM 会：
# - 替换角色名和地点名
# - 调整情节逻辑
# - 保持风格一致

# 3. 输出适配后的文本
```

## 创作工具与七步方法论映射

| 七步阶段 | 映射的创作工具 | 作用 |
|---------|--------------|------|
| **Constitution** | 世界观冲突检测器<br>角色一致性检查器 | 建立一致性规则 |
| **Specify** | 商业化优化器<br>平台适配器 | 定义商业化目标和平台要求 |
| **Clarify** | Hook 优化器<br>开篇场景生成器 | 澄清关键情节点 |
| **Plan** | 情绪曲线优化器<br>伏笔提醒器 | 规划节奏和伏笔 |
| **Tasks** | 章节标题生成器 | 生成任务标题 |
| **Write** | **语料库缝合**<br>AI 检测规避器 | **核心缝合功能** |
| **Analyze** | 角色一致性检查器<br>世界观冲突检测器<br>伏笔提醒器<br>AI 检测规避器<br>情绪曲线优化器<br>结尾优化器 | 全面质量验证 |

详细映射说明请参考 [INTEGRATED_WRITING_SYSTEM.md](./INTEGRATED_WRITING_SYSTEM.md)

---

## 使用流程

### 方式一：Web 界面

1. **启动 API 服务器**
   ```bash
   python api_server.py
   ```

2. **启动前端**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **访问界面**
   - 打开浏览器访问 `http://localhost:5173`
   - 配置 API 设置（点击"显示 API 配置"）
   - 上传小说文件或粘贴文本
   - 选择小说类型和拓扑模式
   - 选择创作工具
   - 点击"开始提取"

### 方式二：命令行

```bash
python main.py --input novel.txt --type 玄幻 --output output/
```

### 方式三：Python API

```python
from main import NovelCorpusExtractor

extractor = NovelCorpusExtractor("config.yaml")
results = await extractor.process_novel("novel.txt", "玄幻")
```

---

## 输出文件说明

系统会在输出目录生成以下文件：

### 记忆体文件

1. **世界观记忆体** (`02_世界观记忆体.yaml`)
   - 世界观设定
   - 规则和逻辑
   - 地理和历史信息

2. **人物记忆体** (`03_人物记忆体.yaml`)
   - 人物信息
   - 角色关系
   - 性格特征

3. **剧情规划大纲** (`04_剧情规划大纲.yaml`)
   - 整体剧情结构
   - 章节规划
   - 关键情节

4. **伏笔追踪表** (`05_伏笔追踪表.yaml`)
   - 伏笔列表
   - 回收计划
   - 状态追踪

### 语料库文件

5. **类型语料库** (`06_玄幻预料库.txt` 等)
   - 按类型分类的语料
   - 可用于训练和参考

6. **对话语料库** (`13_对话预料库.txt`)
   - 提取的对话内容
   - 可用于风格学习

---

## 拓扑模式说明

### Linear（线性模式）

- **适用场景**: 单 API 环境，低算力
- **特点**: 顺序处理，稳定可靠
- **Agent 流程**: Reader → Analyst → Archivist

### Triangular（三角模式）

- **适用场景**: 3 个 API 可用
- **特点**: 初步并行，质检分离
- **Agent 流程**: Scanner → Extractor → Memory Keeper

### Swarm（蜂群模式）

- **适用场景**: 5+ API 可用
- **特点**: 全功能并行，效率最高
- **Agent 流程**: 所有 Agent 并行协作

### Auto（自动模式）

- **特点**: 根据可用 API 数量自动选择模式
- **推荐**: 大多数情况下使用此模式

---

## API 配置

### 单 API 模式

在 `config.yaml` 中配置：

```yaml
model:
  model: "openai"
  model_name: "gpt-4"
  api_key: "your-api-key"  # 或使用环境变量 OPENAI_API_KEY
```

### API 池模式

启用多 API 负载均衡：

```yaml
api_pool:
  enabled: true
  apis:
    - name: "openai_primary"
      provider: "openai"
      api_key: "your-key"
      model: "gpt-4"
      enabled: true
    - name: "gemini_primary"
      provider: "gemini"
      api_key: "your-key"
      model: "gemini-pro"
      enabled: true
```

### 环境变量

推荐使用环境变量管理 API 密钥：

```bash
export OPENAI_API_KEY="your-api-key"
export GEMINI_API_KEY="your-api-key"
```

---

## 常见问题

### Q: 如何配置 API 密钥？

A: 有两种方式：
1. 在 `config.yaml` 中直接配置（不推荐，可能泄露）
2. 使用环境变量（推荐）：`export OPENAI_API_KEY="your-key"`

### Q: 支持哪些 API 提供商？

A: 支持 OpenAI、Gemini、DeepSeek、Anthropic Claude、Moonshot、零一万物、通义千问、文心一言、智谱AI。

### Q: 如何选择拓扑模式？

A: 推荐使用 `auto` 模式，系统会根据可用 API 数量自动选择最佳模式。

### Q: 创作工具是必须的吗？

A: 不是。可以选择性地启用创作工具，根据需求选择需要的工具。

### Q: 输出文件在哪里？

A: 默认在 `output/` 目录，可以在 `config.yaml` 中配置 `output_dir`。

---

## 总结

NovelCorpusExtractor 提供了完整的小说创作辅助流程，从文本分析到创作优化，覆盖了小说创作的各个环节。通过多智能体协作和创作工具，可以大大提高创作效率和质量。

**关键要点**:
- ✅ 系统仅支持 API 模式，不支持本地模型
- ✅ 支持多种拓扑模式，自动适配 API 数量
- ✅ 提供 10 大创作工具，覆盖全流程
- ✅ 支持七步方法论工作流，从零开始创作
- ✅ 自动生成记忆体和语料库，便于后续使用

---

**最后更新**: 2025-01-XX
**版本**: 1.0.0

