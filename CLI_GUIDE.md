# CLI 工具使用指南

## 概述

CLI工具提供了完整的命令行界面，支持单文件处理、批量处理、配置管理等功能。

## 安装

确保已安装所有依赖：

```bash
pip install -r requirements.txt
```

## 基本用法

### 1. 处理单个文件

```bash
# 基本用法
python cli.py process --input novel.txt --type 玄幻

# 指定输出目录
python cli.py process --input novel.txt --type 言情 --output ./output

# 使用自定义配置文件
python cli.py --config my_config.yaml process --input novel.txt
```

**参数说明：**
- `--input, -i`: 输入文件路径（必需）
- `--type, -t`: 小说类型（默认：通用）
- `--output, -o`: 输出目录（可选，覆盖配置文件设置）
- `--config`: 配置文件路径（默认：config.yaml）
- `--verbose, -v`: 显示详细日志

### 2. 批量处理

```bash
# 批量处理多个文件
python cli.py batch --files novel1.txt novel2.txt novel3.txt --type 玄幻

# 指定并发数和输出目录
python cli.py batch --files *.txt --type 言情 --concurrent 5 --output ./batch_output
```

**参数说明：**
- `--files, -f`: 文件路径列表（必需，支持多个文件）
- `--type, -t`: 小说类型（默认：通用）
- `--concurrent, -c`: 最大并发数（默认：3）
- `--output, -o`: 输出目录（可选）

**批量处理特性：**
- 自动并发处理，提高效率
- 实时进度显示
- 自动保存每个任务的结果
- 生成批量处理摘要报告

### 3. 配置管理

#### 显示配置信息

```bash
python cli.py config --show
```

显示当前配置文件的详细信息，包括：
- API配置（单API或API池）
- 输出目录
- 分块参数
- 拓扑模式

#### 验证配置文件

```bash
python cli.py config --validate
```

验证配置文件的有效性，检查：
- 配置文件格式
- 必需的配置项
- API密钥配置
- 参数合理性

### 4. 状态查询

```bash
# 列出所有批量任务
python cli.py status

# 查询特定批量任务
python cli.py status --batch-id batch_20250101_120000
```

## 高级用法

### 使用详细日志

```bash
python cli.py --verbose process --input novel.txt --type 玄幻
```

### 处理不同小说类型

支持的小说类型包括：
- 通用
- 言情、玄幻、仙侠、都市、历史
- 重生文、系统文、爽文
- 悬疑、科幻、武侠
- 等等（36+种类型）

多个类型可以用逗号分隔：
```bash
python cli.py process --input novel.txt --type "玄幻,爽文,系统文"
```

### 批量处理示例

```bash
# 处理目录下所有txt文件
python cli.py batch --files *.txt --type 言情 --concurrent 3

# 处理特定文件列表
python cli.py batch \
  --files novel1.txt novel2.txt novel3.txt \
  --type 玄幻 \
  --concurrent 5 \
  --output ./results
```

## 输出说明

### 单文件处理输出

处理完成后，会在输出目录生成：
- `worldview.yaml`: 世界观记忆体
- `characters.yaml`: 人物记忆体
- `outline.yaml`: 剧情大纲
- `foreshadowing.yaml`: 伏笔追踪表
- `frankentexts/`: Frankentexts语料库

### 批量处理输出

批量处理会在输出目录生成：
- `{job_id}_result.json`: 每个任务的处理结果
- `{batch_id}_summary.json`: 批量处理摘要

摘要文件包含：
- 总任务数
- 成功/失败数量
- 进度百分比
- 成功率
- 每个任务的详细状态

## 错误处理

### 常见错误

1. **配置文件不存在**
   ```
   ❌ 配置文件不存在: config.yaml
   ```
   解决：创建配置文件或使用 `--config` 指定路径

2. **输入文件不存在**
   ```
   ❌ 输入文件不存在: novel.txt
   ```
   解决：检查文件路径是否正确

3. **配置文件无效**
   ```
   ❌ 配置文件无效: ...
   ```
   解决：使用 `python cli.py config --validate` 检查配置

### 中断处理

按 `Ctrl+C` 可以安全中断处理，已处理的数据会保存。

## 与API服务器配合使用

CLI工具可以独立使用，也可以与API服务器配合：

1. **独立使用**：直接处理文件，适合本地处理
2. **API模式**：启动API服务器，使用API客户端调用

```bash
# 启动API服务器
python api_server.py

# 使用API客户端
python -c "from client.api_client import NovelCorpusClient; ..."
```

## 性能优化建议

1. **批量处理**：使用批量处理功能处理多个文件，自动并发
2. **并发数**：根据系统资源调整 `--concurrent` 参数
3. **API池**：配置多个API以提高处理速度
4. **拓扑模式**：根据可用API数量自动选择最优模式

## 示例脚本

### 处理单个文件

```bash
#!/bin/bash
python cli.py process \
  --input ./novels/my_novel.txt \
  --type 玄幻 \
  --output ./output/my_novel
```

### 批量处理脚本

```bash
#!/bin/bash
# 处理目录下所有txt文件
files=$(ls *.txt | tr '\n' ' ')
python cli.py batch \
  --files $files \
  --type 言情 \
  --concurrent 3 \
  --output ./batch_results
```

## 注意事项

1. 确保配置文件正确设置API密钥
2. 批量处理时注意API调用频率限制
3. 大文件处理可能需要较长时间
4. 建议在处理前验证配置文件

## 更多帮助

```bash
# 查看所有命令
python cli.py --help

# 查看特定命令帮助
python cli.py process --help
python cli.py batch --help
python cli.py config --help
```


