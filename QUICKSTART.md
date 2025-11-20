# 快速开始指南

## 5分钟快速上手

### 步骤1: 安装依赖

```bash
pip install -r requirements.txt
```

### 步骤2: 配置API密钥

编辑 `config.yaml` 文件，设置你的API密钥：

```yaml
model:
  model: "openai"
  model_name: "gpt-4"
  api_key: "sk-your-api-key-here"
```

或者设置环境变量：

```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

### 步骤3: 准备小说文件

将你要分析的小说保存为文本文件，例如 `novel.txt`。

### 步骤4: 运行提取

```bash
python main.py --input novel.txt --type 玄幻
```

### 步骤5: 查看结果

处理完成后，在 `output/` 目录查看生成的文件：

- `02_世界观记忆体.yaml` - 世界观设定
- `03_人物记忆体.yaml` - 人物信息
- `04_剧情规划大纲.yaml` - 剧情大纲
- `05_伏笔追踪表.yaml` - 伏笔追踪

在 `corpus_samples/` 目录查看提取的语料片段。

## 常见问题

### Q: 支持哪些模型？

A: 目前支持 OpenAI GPT系列、Google Gemini、DeepSeek。可以在 `config.yaml` 中切换。

### Q: 处理速度如何？

A: 取决于小说长度和选择的拓扑模式：
- 线性模式：较慢但稳定
- 三角模式：中等速度
- 蜂群模式：最快但需要多个API

### Q: Token消耗大吗？

A: 处理长篇小说会消耗较多Token。建议：
- 使用较小的模型（如gpt-3.5-turbo）降低成本
- 调整 `chunk_size` 参数控制处理粒度

### Q: 如何添加自定义提示词？

A: 在 `prompts/` 目录添加新的提示词模板文件，然后在代码中引用。

## 下一步

- 阅读 [README.md](README.md) 了解详细功能
- 查阅 [USAGE_GUIDE.md](USAGE_GUIDE.md) 获取进阶配置与实践
- 参考 `example_usage.py` 学习编程接口

