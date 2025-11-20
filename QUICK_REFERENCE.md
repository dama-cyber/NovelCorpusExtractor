# 快速参考指南

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API

编辑 `config.yaml` 或设置环境变量：

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 3. 运行系统

```bash
python main.py --input novel.txt --type "重生文,系统文"
```

## 📚 核心功能速查

### 类型标签（36+种）

**基础类型**: 言情、玄幻、仙侠、悬疑、科幻、奇幻、脑洞、都市、历史、古言、无CP

**核心情节**: 重生文、穿越文、穿书文、系统文、无限流、复仇文、升级流

**热门设定**: 爽文、屌丝逆袭、废柴流、打脸爽文、追妻火葬场、马甲文、真假千金、迪化文、发疯文学、虐文、CP塑造

**背景职业**: 种田文、宫斗/宅斗、末世文、娱乐圈文、总裁文、灵异文、赛博朋克、商战文、冒险小说

### 大纲模板（44个）

**通用模板**: 三幕式、起承转合、环形叙事、英雄之旅、草蛇灰线、碎片拼贴、弗莱塔格金字塔、救猫咪15节拍

**类型模板**: 36个类型特定模板（运行 `python outline_templates/生成所有类型模板.py` 生成）

### API支持（10+）

OpenAI, Anthropic (Claude), Google Gemini, DeepSeek, Moonshot, 零一万物, 通义千问, 文心一言, 智谱AI, 自定义API

### 辅助工具（10个）

1. AI检测规避器
2. 商业化优化器
3. 平台算法适配器
4. 情感曲线优化器
5. 人物一致性检查器
6. 世界观冲突检测器
7. 伏笔回收提醒器
8. 章节标题生成器
9. 开篇场景生成器
10. 结尾收束优化器

## 🎯 常用命令

```bash
# 基本使用
python main.py --input novel.txt --type 重生文

# 多类型
python main.py --input novel.txt --type "重生文,系统文,爽文"

# 指定输出目录
python main.py --input novel.txt --output my_output

# 指定配置文件
python main.py --input novel.txt --config custom_config.yaml
```

## 📖 详细文档

- `README.md` - 项目总览
- `USAGE_GUIDE.md` - 详细使用指南
- `QUICKSTART.md` - 快速开始
- `GENRE_GUIDE.md` - 类型标签指南
- `SEVEN_SINS_AND_HOOK_GUIDE.md` - 理论框架指南
- `ALL_TOOLS_GUIDE.md` - 辅助工具指南
- `API_ENHANCEMENT_GUIDE.md` - API增强指南

## 🔧 配置文件

主要配置在 `config.yaml`：

```yaml
# 单API模式
model:
  model: "openai"
  api_key: "sk-..."

# 多API池模式（推荐）
api_pool:
  enabled: true
  apis:
    - name: "openai"
      provider: "openai"
      api_key: "sk-..."
      priority: 1
```

## ✅ 项目状态

- **核心功能**: ✅ 100%完成
- **类型支持**: ✅ 100%完成
- **大纲模板**: ✅ 100%完成
- **理论框架**: ✅ 100%完成
- **辅助工具**: ✅ 100%完成
- **整体完成度**: ✅ 98%

---

**系统已完整可用，可以开始创作！**

