# 使用指南

## 📚 目录

1. [快速开始](#快速开始)
2. [详细安装步骤](#详细安装步骤)
3. [配置说明](#配置说明)
4. [使用方法](#使用方法)
5. [输出文件说明](#输出文件说明)
6. [常见问题](#常见问题)
7. [高级用法](#高级用法)

---

## 🚀 快速开始

### 最简单的使用方式

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置API密钥（编辑config.yaml或设置环境变量）
export OPENAI_API_KEY="your-api-key-here"

# 3. 运行
python main.py --input your_novel.txt --type 玄幻
```

---

## 📦 详细安装步骤

### 步骤1: 环境要求

- Python 3.8 或更高版本
- pip 包管理器

### 步骤2: 下载项目

```bash
# 如果是从Git仓库克隆
git clone <repository_url>
cd NovelCorpusExtractor

# 或者直接解压下载的压缩包
unzip NovelCorpusExtractor.zip
cd NovelCorpusExtractor
```

### 步骤3: 安装依赖

```bash
# 安装所有依赖
pip install -r requirements.txt

# 如果只需要基本功能，可以只安装核心依赖
pip install PyYAML tqdm

# 如果需要使用OpenAI
pip install openai

# 如果需要使用Gemini
pip install google-generativeai

# 如果需要向量数据库功能（可选）
pip install chromadb
```

### 步骤4: 验证安装

```bash
# 检查Python版本
python --version  # 应该 >= 3.8

# 检查依赖是否安装成功
python -c "import yaml; import tqdm; print('依赖安装成功')"
```

---

## ⚙️ 配置说明

### 方式1: 配置文件（推荐）

编辑 `config.yaml` 文件：

```yaml
# 模型配置
model:
  model: "openai"  # 可选: openai / gemini / deepseek
  model_name: "gpt-4"  # 具体模型名称
  api_key: "sk-your-api-key-here"  # 你的API密钥
  base_url: ""  # 可选，自定义API地址（如使用代理）

# 拓扑配置
topology:
  mode: "auto"  # 可选: linear / triangular / swarm / auto
  # auto模式会根据可用API数量自动选择

# 处理配置
chunk_size: 1024  # 文本块大小（token数，约等于字符数/2）
chunk_overlap: 100  # 块重叠字符数

# 目录配置
output_dir: "output"  # 输出目录
corpus_dir: "corpus_samples"  # 语料库目录
```

### 方式2: 环境变量

```bash
# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-your-api-key-here"

# Windows (CMD)
set OPENAI_API_KEY=sk-your-api-key-here

# Linux/Mac
export OPENAI_API_KEY="sk-your-api-key-here"

# Gemini
export GEMINI_API_KEY="your-gemini-key"

# DeepSeek
export DEEPSEEK_API_KEY="your-deepseek-key"
```

### 方式3: 命令行参数

某些配置可以通过命令行参数覆盖：

```bash
python main.py --input novel.txt --output custom_output --type 玄幻
```

---

## 📖 使用方法

### 基本用法

```bash
python main.py --input <小说文件路径> --type <小说类型>
```

### 完整参数

```bash
python main.py \
  --config config.yaml \          # 配置文件路径（默认: config.yaml）
  --input path/to/novel.txt \     # 输入小说文件（必需）
  --output output \               # 输出目录（可选，覆盖配置文件）
  --type 玄幻                      # 小说类型（可选）
```

### 参数说明

| 参数 | 必需 | 说明 | 可选值 |
|------|------|------|--------|
| `--input` | ✅ | 输入小说文件路径 | 任何文本文件 |
| `--config` | ❌ | 配置文件路径 | 默认: `config.yaml` |
| `--output` | ❌ | 输出目录 | 默认: `output` |
| `--type` | ❌ | 小说类型 | `玄幻`/`都市`/`言情`/`悬疑`/`历史`/`科幻`/`武侠`/`通用` |

### 使用示例

#### 示例1: 处理玄幻小说

```bash
python main.py --input 修仙传.txt --type 玄幻
```

#### 示例2: 处理都市小说，自定义输出目录

```bash
python main.py \
  --input 都市逆袭.txt \
  --type 都市 \
  --output my_output
```

#### 示例3: 使用自定义配置文件

```bash
python main.py \
  --config my_config.yaml \
  --input novel.txt \
  --type 言情
```

#### 示例4: 处理英文小说

```bash
python main.py --input english_novel.txt --type 通用
```

---

## 📁 输出文件说明

处理完成后，系统会在输出目录生成以下文件：

### 记忆体文件（YAML格式）

```
output/
├── 02_世界观记忆体.yaml      # 世界观设定
│   ├── 基本设定
│   ├── 力量体系
│   ├── 地理设定
│   └── 势力设定
│
├── 03_人物记忆体.yaml        # 人物信息
│   ├── 主角信息
│   ├── 重要配角
│   └── 角色关系网
│
├── 04_剧情规划大纲.yaml      # 剧情大纲
│   ├── 大纲设定
│   ├── 核心剧情线
│   └── 章节大纲
│
└── 05_伏笔追踪表.yaml        # 伏笔追踪
    ├── 伏笔列表
    └── 回收状态
```

### 语料库文件（文本格式）

```
corpus_samples/
├── 06_玄幻预料库.txt         # 玄幻类语料片段
├── 07_都市预料库.txt         # 都市类语料片段
├── 08_言情预料库.txt         # 言情类语料片段
├── 09_悬疑预料库.txt         # 悬疑类语料片段
├── 10_历史预料库.txt         # 历史类语料片段
├── 11_科幻预料库.txt         # 科幻类语料片段
├── 12_武侠预料库.txt         # 武侠类语料片段
└── 13_对话预料库.txt         # 对话语料片段
```

### 日志文件

```
novel_extractor.log  # 处理日志
```

---

## ❓ 常见问题

### Q1: 如何获取API密钥？

**OpenAI:**
1. 访问 https://platform.openai.com/api-keys
2. 登录账户
3. 创建新的API密钥

**Gemini:**
1. 访问 https://makersuite.google.com/app/apikey
2. 登录Google账户
3. 创建API密钥

**DeepSeek:**
1. 访问 https://platform.deepseek.com/
2. 注册/登录
3. 获取API密钥

### Q2: 处理速度慢怎么办？

**优化建议:**
1. 使用更快的模型（如 `gpt-3.5-turbo` 而不是 `gpt-4`）
2. 增加 `chunk_size`（减少API调用次数）
3. 使用多个API密钥启用并行模式
4. 减少 `chunk_overlap`（降低处理量）

### Q3: Token消耗太大怎么办？

**降低成本:**
1. 使用更便宜的模型（`gpt-3.5-turbo`）
2. 增加 `chunk_size`（减少调用次数）
3. 只处理关键章节
4. 使用本地模型（如果支持）

### Q4: 文件编码错误怎么办？

系统会自动尝试UTF-8和GBK编码。如果仍然失败：
1. 手动转换文件编码为UTF-8
2. 使用文本编辑器（如VS Code）转换编码

### Q5: 如何处理超长小说？

**建议:**
1. 分章节处理
2. 增加 `chunk_size` 到 2048 或更大
3. 使用并行模式（多个API）
4. 考虑使用断点续传（未来功能）

### Q6: 输出文件格式是什么？

- 记忆体文件：YAML格式，可直接编辑
- 语料库文件：文本格式，包含片段和元数据

### Q7: 如何查看处理进度？

处理过程中会显示进度条：
```
处理中: 45%|████▌     | 45/100 [02:30<03:05]
```

### Q8: 支持哪些文件格式？

目前支持纯文本文件（.txt）。其他格式需要先转换为文本。

---

## 🔧 高级用法

### 1. 编程接口使用

```python
import asyncio
from main import NovelCorpusExtractor

async def main():
    # 初始化系统
    extractor = NovelCorpusExtractor("config.yaml")
    
    # 处理小说
    summary = await extractor.process_novel(
        input_file="novel.txt",
        novel_type="玄幻"
    )
    
    chunk_results = summary["chunk_results"]
    print(f"处理了 {len(chunk_results)} 个文本块")
    
    # 工作流输出
    workflow = summary.get("workflow", {})
    print(f"工作流阶段: {', '.join(workflow.keys())}")
    
    # 访问记忆体
    worldview = extractor.memory_manager.load_worldview()
    characters = extractor.memory_manager.load_characters()
    
    print(f"世界观设定: {len(worldview)} 项")
    print(f"人物信息: {len(characters)} 个")

# 运行
asyncio.run(main())
```

### 2. 自定义拓扑模式

```yaml
# config.yaml
topology:
  mode: "swarm"  # 强制使用蜂群模式
```

### 3. 调整分块参数

```yaml
# config.yaml
chunk_size: 2048      # 增大块大小，减少API调用
chunk_overlap: 200    # 增大重叠，保证连续性
```

### 4. 批量处理

```bash
# 创建批处理脚本 process_all.sh
#!/bin/bash
for file in novels/*.txt; do
    python main.py --input "$file" --type 玄幻 --output "output/$(basename $file .txt)"
done
```

### 5. 只提取特定类型片段

修改 `agents/extractor.py` 中的逻辑，只保存特定类型的片段。

---

## 📊 性能参考

### 处理速度（参考值）

| 小说长度 | 线性模式 | 三角模式 | 蜂群模式 |
|---------|---------|---------|---------|
| 10万字 | ~10分钟 | ~5分钟 | ~3分钟 |
| 50万字 | ~50分钟 | ~25分钟 | ~15分钟 |
| 100万字 | ~100分钟 | ~50分钟 | ~30分钟 |

*注：实际速度取决于API响应速度和网络状况*

### Token消耗（参考值）

| 小说长度 | 预估Token消耗 |
|---------|--------------|
| 10万字 | ~50K tokens |
| 50万字 | ~250K tokens |
| 100万字 | ~500K tokens |

*注：实际消耗取决于chunk_size和处理深度*

---

## 🆘 获取帮助

### 查看帮助信息

```bash
python main.py --help
```

### 查看日志

```bash
# 查看处理日志
cat novel_extractor.log

# 实时查看日志（Linux/Mac）
tail -f novel_extractor.log
```

### 报告问题

如果遇到问题，请提供：
1. 错误信息（从日志文件）
2. 配置文件（隐藏API密钥）
3. 输入文件信息（文件名、大小、编码）
4. Python版本和系统信息

---

## 📝 下一步

处理完成后，你可以：

1. **查看提取的记忆体**
   - 打开 `output/02_世界观记忆体.yaml` 查看世界观设定
   - 打开 `output/03_人物记忆体.yaml` 查看人物信息

2. **使用语料库**
   - 查看 `corpus_samples/` 目录中的语料片段
   - 这些片段可用于后续的文本生成

3. **继续创作**
   - 使用提取的记忆体作为创作参考
   - 使用语料库中的片段作为模板

---

**祝使用愉快！** 🎉

