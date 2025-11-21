# 开源小说语料提取系统

一个基于多智能体协同架构的长篇小说语料提取系统，支持从优秀小说中提取世界观、人物、剧情、伏笔等结构化信息，并构建可复用的Frankentexts语料库。

## 功能特性

### 核心功能

1. **多智能体协同架构**
   - Reader: 智能文本分块
   - Analyst: 深度信息提取
   - Archivist: 结构化归档
   - Scanner: 粗粒度分类
   - Extractor: 强化解析
   - Planner: 剧情大纲生成
   - Stylist: 语言风格分析

2. **多Agent协同机制** ⭐⭐
   - 支持1-5个API的智能协同策略
   - 自动根据API数量选择最优协同模式
   - 8种Agent角色智能分配（Reader、Analyst、Extractor、Planner、Writer、Stylist、Critic、Archivist）
   - 并行执行优化，最大化效率
   - 详细使用指南请参考 [MULTI_AGENT_COORDINATION.md](./MULTI_AGENT_COORDINATION.md)

3. **三种拓扑处理模式**
   - 线性串行模式：单API环境，顺序处理
   - 三角协同模式：3个API，生产者-消费者-监督者架构
   - 专家蜂群模式：5+ API，全功能并行处理

3. **多模型后端适配（仅 API 模式）**
   - ⚠️ **重要**：本项目仅支持 API 模式，不支持本地模型
   - OpenAI GPT系列
   - Google Gemini
   - DeepSeek
   - Anthropic Claude
   - 支持多 API 池负载均衡
   - 支持自定义API接口
   - 详细配置请参考 [API_ONLY_GUIDE.md](./API_ONLY_GUIDE.md)

4. **Frankentexts语料库**
   - 高价值片段提取
   - 模板化处理
   - 向量检索支持
   - 分类存储管理

5. **记忆体结构管理**
   - 世界观记忆体（YAML格式）
   - 人物记忆体（MBTI性格、语言风格等）
   - 剧情规划大纲
   - 伏笔追踪表

### 🆕 NovelForge 智能创作功能（规划中）

> **注意**：以下功能正在规划中，详细方案请参考 [INTEGRATION_SUMMARY.md](./INTEGRATION_SUMMARY.md)

6. **动态输出模型** ⭐
   - 基于 Pydantic 的可视化 Schema 定义
   - AI 输出自动校验，确保格式精确
   - 支持自定义创作元素结构

7. **自由上下文注入** ⭐
   - 表达式语言驱动的上下文系统
   - 支持复杂查询：`@current.character.enemies`、`@volume(1).scenes`
   - 一行表达式实现复杂上下文检索

8. **知识图谱驱动** ⭐
   - Neo4j 集成的关系管理
   - 自动提取人物关系和动态信息
   - 动态注入到生成过程，减少 AI 幻觉

9. **灵感助手** ⭐
   - 对话式创作助手
   - 支持跨项目引用
   - 一键应用对话成果到卡片

10. **灵感工作台** ⭐
    - 独立头脑风暴空间
    - 自由卡片系统
    - 跨项目引用和创意整合

11. **雪花式创作流程** ⭐
    - 从一句话梗概到正文的完整流程
    - 树形结构组织创作内容
    - 支持多种创作流程（英雄之旅、三幕式等）

12. **高度可配置系统** ⭐
    - 深度自定义 AI 模型参数
    - 可配置提示词模板
    - 灵活的卡片类型和内容结构

### 🆕 qcbigma 优秀特性

> **注意**：以下功能基于 qcbigma 方法论的设计

13. **七步方法论** ⭐
    - 从创作原则到质量验证的完整流程
    - 结构化创作引导
    - 早期发现和解决歧义

14. **Agent Skills 系统** ⭐
    - 模块化 AI 知识系统
    - 三层技能体系（扩展/项目/个人）
    - 智能自动激活相关技能

15. **斜杠命令系统** ⭐
    - 快速访问常用功能
    - 统一的命令接口
    - 支持命令自动补全

## 技术栈

- **语言**: Python 3.8+
- **核心依赖**: PyYAML、tqdm、rich
- **模型 API**: OpenAI GPT 系列、Google Gemini、DeepSeek（可扩展）
- **向量数据库**: Chroma（可选）
- **并行与调度**: asyncio + 自适应拓扑管理器

## 安装

### 1. 克隆或下载项目

```bash
git clone <repository_url>
cd NovelCorpusExtractor
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置

⚠️ **重要提示**：本项目仅支持 API 模式，不支持本地模型。请确保配置了有效的 API 密钥。

编辑 `config.yaml` 文件，设置：

- 模型类型和API密钥
- 拓扑模式（或使用auto自动检测）
- 输出目录等参数

```yaml
model:
  model: "openai"
  model_name: "gpt-4"
  api_key: "your-api-key-here"  # 或设置环境变量 OPENAI_API_KEY

topology:
  mode: "auto"  # 自动检测可用API数量
```

**验证配置**（可选但推荐）：

```bash
python validate_config.py
```

这将检查配置文件的完整性和有效性，并提示任何错误或警告。

## 使用方法

### Web API 服务器（推荐用于前端集成）

启动API服务器：

**Windows:**
```bash
start_api.bat
```

**Linux/Mac:**
```bash
chmod +x start_api.sh
./start_api.sh
```

**或直接使用Python:**
```bash
python api_server.py
```

服务器默认运行在 `http://localhost:8000`

API接口：
- `POST /api/process` - 处理小说文件或文本
- `GET /api/health` - 健康检查
- `GET /api/config` - 获取配置信息

详细部署说明请参考 [DEPLOYMENT.md](DEPLOYMENT.md)

### 命令行用法（基本用法）

```bash
python main.py --input novel.txt --type 玄幻
```

### 完整参数

```bash
python main.py \
  --config config.yaml \
  --input path/to/novel.txt \
  --output output \
  --type 玄幻
```

### 参数说明

- `--config`: 配置文件路径（默认: config.yaml）
- `--input`: 输入小说文件路径（必需）
- `--output`: 输出目录（默认: output）
- `--type`: 小说类型（可选: 玄幻/都市/言情/悬疑/历史/科幻/武侠/通用，完整36+类型列表详见 \`GENRE_GUIDE.md\`）

## 输出文件

系统会在输出目录生成以下文件：

```
output/
├── 02_世界观记忆体.yaml      # 世界观设定
├── 03_人物记忆体.yaml        # 人物信息
├── 04_剧情规划大纲.yaml      # 剧情大纲
└── 05_伏笔追踪表.yaml        # 伏笔追踪

corpus_samples/
├── 06_玄幻预料库.txt         # 玄幻类语料
├── 07_都市预料库.txt         # 都市类语料
├── 08_言情预料库.txt         # 言情类语料
├── 09_悬疑预料库.txt         # 悬疑类语料
├── 10_历史预料库.txt         # 历史类语料
├── 11_科幻预料库.txt         # 科幻类语料
├── 12_武侠预料库.txt         # 武侠类语料
└── 13_对话预料库.txt         # 对话语料
```

## 拓扑模式说明

### 线性串行模式（Linear）

- **适用场景**: 单API环境，低算力
- **特点**: 顺序处理，稳定可靠
- **Agent流程**: Reader → Analyst → Archivist

### 三角协同模式（Triangular）

- **适用场景**: 3个API可用
- **特点**: 初步并行，质检分离
- **Agent流程**: Scanner → Extractor → Memory Keeper

### 专家蜂群模式（Swarm）

- **适用场景**: 5+ API可用
- **特点**: 全功能并行，效率最高
- **Agent流程**: 所有Agent并行协作

## 项目结构

```
NovelCorpusExtractor/
├── main.py                 # 主程序入口
├── config.yaml             # 配置文件
├── requirements.txt        # 依赖列表
├── README.md              # 说明文档
├── agents/                # Agent模块
│   ├── reader.py          # 读取者
│   ├── analyst.py         # 分析者
│   ├── archivist.py       # 归档员
│   ├── scanner.py         # 扫描者
│   ├── extractor.py       # 深度提取者
│   ├── planner.py         # 规划者
│   └── stylist.py         # 风格Agent
├── core/                  # 核心工具
│   ├── model_interface.py # 模型接口
│   ├── memory_manager.py  # 记忆体管理
│   ├── frankentexts.py    # Frankentexts管理
│   └── topology_manager.py # 拓扑管理
├── prompts/               # 提示词模板
├── outline_templates/     # 大纲模板
├── corpus_samples/        # 语料库示例
└── output/                # 输出目录
```

## 设计亮点

1. **模块化架构**：高内聚低耦合的 Agent 设计，可按需替换或扩展
2. **自适应拓扑**：根据可用 API 数量自动切换线性/三角/蜂群模式
3. **一致性保障**：多轮校验与记忆体检查，自动发现设定冲突
4. **Frankentexts 复用**：支持模板化处理、高价值片段沉淀与检索
5. **类型安全**：完备的类型注解和配置校验，降低运行时错误

## 📚 相关文档

### NovelForge 功能融合方案

- **[INTEGRATION_SUMMARY.md](./INTEGRATION_SUMMARY.md)** - 融合方案总结和索引
- **[NOVELFORGE_INTEGRATION_PLAN.md](./NOVELFORGE_INTEGRATION_PLAN.md)** - 核心功能详细设计
- **[WORKFLOW_INTEGRATION_GUIDE.md](./WORKFLOW_INTEGRATION_GUIDE.md)** - 创作流程融合指南
- **[NOVELWEAVE_INTEGRATION.md](./NOVELWEAVE_INTEGRATION.md)** - qcbigma 方法论融合方案 ⭐

### 整合工作流和优化

- **[INTEGRATED_WORKFLOW_GUIDE.md](./INTEGRATED_WORKFLOW_GUIDE.md)** - 整合工作流使用指南
- **[WORKFLOW_OPTIMIZATION_RECOMMENDATIONS.md](./WORKFLOW_OPTIMIZATION_RECOMMENDATIONS.md)** - 创作流程优化建议 ⭐
- **[MULTI_AGENT_COORDINATION.md](./MULTI_AGENT_COORDINATION.md)** - 多Agent协同机制使用指南 ⭐⭐（支持1-5个API的智能协同）

这些文档详细说明了如何将 NovelForge 的智能创作功能融合到现有系统中，包括：
- 动态输出模型（Pydantic）
- 自由上下文注入
- 知识图谱驱动（Neo4j）
- 灵感助手和工作台
- 雪花式创作流程
- 高度可配置系统

## 适用场景

- 小说创作和打磨
- 大规模语料库构建
- IP 改编和设定核查
- 文本分析/学术研究
- 设定一致性与伏笔追踪

## 未来规划

- 扩展更多模型后端与 API 适配
- 提供可视化 GUI 与 Web API
- 支持批量任务与调度编排
- 丰富类型模板与剧情套路库
- 深入优化性能与 Token 成本

## 开发指南

### 添加新模型支持

在 `core/model_interface.py` 中实现新的 `LLMClient` 子类：

```python
class NewModelClient(LLMClient):
    def send_prompt(self, prompt: str, **kwargs) -> str:
        # 实现模型调用逻辑
        pass
```

然后在 `ModelFactory` 中注册。

### 自定义Agent

继承基础Agent类，实现特定功能：

```python
from agents.analyst import AnalystAgent

class CustomAgent(AnalystAgent):
    def analyze_chunk(self, chunk: Dict) -> Dict:
        # 自定义分析逻辑
        pass
```

## 工具和脚本

### 配置验证工具

验证配置文件的有效性：

```bash
python validate_config.py [config.yaml]
```

### 依赖安装脚本

**Windows:**
```bash
install.bat
# 或
find_and_install.ps1
```

**Linux/Mac:**
```bash
chmod +x start_api.sh
./start_api.sh
```

## 注意事项

1. **API密钥安全**: 建议使用环境变量存储API密钥，不要提交到版本控制
2. **Token消耗**: 处理长篇小说会消耗大量Token，注意成本控制
3. **处理时间**: 根据小说长度和拓扑模式，处理时间从几分钟到数小时不等
4. **内存占用**: 处理超长文本时注意内存使用
5. **文件大小限制**: API服务器默认限制上传文件大小为50MB，可通过环境变量 `MAX_FILE_SIZE` 调整
6. **日志管理**: 日志文件可能会增长，建议定期清理或使用日志轮转工具

## 许可证

本项目采用开源许可证（具体许可证类型待定）

## 贡献

欢迎提交Issue和Pull Request！

## 更新日志

### v1.1.0 (2025-01-XX)
- ✨ 新增配置验证工具 (`validate_config.py`)
- 🔒 改进API服务器安全性（CORS配置、文件大小限制）
- 🛡️ 增强错误处理和临时文件清理
- 📝 改进日志配置（支持日志级别、文件大小警告）
- ✅ 添加配置文件验证逻辑
- 🧹 改进临时文件管理（使用 `shutil.rmtree` 确保清理）

### v1.0.0 (2025-11-20)
- 初始版本发布
- 支持三种拓扑模式
- 多模型后端适配
- Frankentexts语料库
- 记忆体结构管理

