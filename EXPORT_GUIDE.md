# 数据导出功能使用指南

## 概述

数据导出功能允许将小说语料提取的处理结果导出为多种格式，方便后续分析和使用。

## 支持的导出格式

### 1. JSON
- **描述**: 完整的结构化数据，包含所有处理结果
- **适用场景**: 程序化处理、数据交换
- **文件扩展名**: `.json`

### 2. CSV
- **描述**: 表格格式，适合文本块结果
- **适用场景**: Excel分析、数据统计
- **文件扩展名**: `.csv`
- **注意**: 仅支持文本块结果列表

### 3. Excel
- **描述**: 多工作表Excel文件
- **适用场景**: 复杂数据分析、多维度展示
- **文件扩展名**: `.xlsx`
- **工作表**: 
  - 文本块结果
  - 记忆体（世界观、人物、剧情、伏笔）

### 4. Markdown
- **描述**: Markdown格式文档
- **适用场景**: 文档编写、可读性展示
- **文件扩展名**: `.md`

### 5. HTML
- **描述**: HTML网页格式
- **适用场景**: 浏览器查看、分享展示
- **文件扩展名**: `.html`

## 使用方法

### CLI方式

#### 处理时导出

```bash
# 导出为JSON
python cli.py process --input novel.txt --type 玄幻 --export json

# 导出为所有格式
python cli.py process --input novel.txt --type 言情 --export all

# 指定导出目录
python cli.py process --input novel.txt --type 玄幻 --export excel --export-dir ./my_exports
```

#### 支持的导出格式

```bash
# JSON
python cli.py process --input novel.txt --export json

# CSV
python cli.py process --input novel.txt --export csv

# Excel
python cli.py process --input novel.txt --export excel

# Markdown
python cli.py process --input novel.txt --export markdown

# HTML
python cli.py process --input novel.txt --export html

# 所有格式
python cli.py process --input novel.txt --export all
```

### API方式

#### 导出端点

```http
POST /api/export
Content-Type: multipart/form-data

output_dir: /path/to/output
format: json
export_dir: /path/to/exports (可选)
```

#### 示例请求

```bash
# 使用curl
curl -X POST "http://localhost:8000/api/export" \
  -F "output_dir=./output" \
  -F "format=all"

# 使用Python
import requests

response = requests.post(
    "http://localhost:8000/api/export",
    data={
        "output_dir": "./output",
        "format": "json",
        "export_dir": "./exports"
    }
)

print(response.json())
```

#### 列出支持的格式

```http
GET /api/export/formats
```

```bash
curl http://localhost:8000/api/export/formats
```

### Python代码方式

```python
from main import NovelCorpusExtractor
from core.data_exporter import create_exporter

# 创建提取器并处理
extractor = NovelCorpusExtractor("config.yaml")
results = await extractor.process_novel("novel.txt", "玄幻")

# 创建导出器
exporter = create_exporter("./exports")

# 导出所有格式
exported_files = exporter.export_from_memory_manager(
    extractor.memory_manager,
    chunk_results=results.get('chunk_results'),
    outline=results.get('outline'),
    workflow_summary=results.get('workflow'),
    base_filename="my_novel"
)

print("导出完成:")
for fmt, path in exported_files.items():
    print(f"  {fmt}: {path}")
```

## 导出数据结构

### JSON格式

```json
{
  "chunkResults": [
    {
      "chunkId": "chunk_1",
      "title": "第一章",
      "summary": "文本摘要",
      "themes": ["主题1", "主题2"],
      "hookScore": 8.5
    }
  ],
  "outline": "剧情大纲内容",
  "workflow": {
    "creationFlow": {},
    "optimizationFlow": {},
    "detectionFlow": {}
  },
  "memories": [
    {
      "id": "worldview",
      "title": "世界观记忆体",
      "data": {}
    }
  ]
}
```

### CSV格式

CSV文件包含文本块结果的扁平化数据：

| chunkId | title | summary | themes | hookScore |
|---------|-------|---------|--------|-----------|
| chunk_1 | 第一章 | 文本摘要 | 主题1,主题2 | 8.5 |

### Excel格式

Excel文件包含多个工作表：
- **文本块结果**: 所有文本块的分析结果
- **记忆体**: 世界观、人物、剧情、伏笔等记忆体数据

### Markdown格式

Markdown文件包含：
- 标题和元数据
- 文本块分析结果（每个块一个章节）
- 剧情大纲
- 记忆体信息
- 工作流信息
- 创作输出

### HTML格式

HTML文件是Markdown的渲染版本，包含：
- 美观的样式
- 表格格式化
- 代码高亮
- 响应式布局

## 导出内容说明

### 文本块结果
- 每个文本块的ID、标题、摘要
- 主题标签
- 钩子分数
- 其他分析结果

### 记忆体
- **世界观记忆体**: 世界设定、力量体系、地理设定等
- **人物记忆体**: 角色信息、性格、关系等
- **剧情规划大纲**: 章节结构、关键情节点
- **伏笔追踪表**: 伏笔列表、回收状态

### 工作流信息
- 创作流程输出
- 优化流程输出
- 检测流程输出

### 创作输出
- 各种创作工具生成的内容
- AI检测规避计划
- 其他创作辅助信息

## 注意事项

### 依赖项

某些导出格式需要额外的依赖：

```bash
# Excel导出需要pandas和openpyxl
pip install pandas openpyxl

# HTML导出需要markdown库（可选，有基本转换）
pip install markdown
```

### 文件大小

- **大文件处理**: 对于大量文本块，CSV和Excel文件可能很大
- **内存使用**: Excel导出会占用较多内存
- **建议**: 对于大量数据，优先使用JSON或CSV格式

### 字符编码

- 所有导出文件使用UTF-8编码
- CSV文件使用UTF-8 BOM（Excel兼容）

### 文件命名

- 默认文件名格式: `export_{输出目录名}_{时间戳}.{扩展名}`
- 可以自定义基础文件名

## 故障排除

### Excel导出失败

**错误**: `pandas未安装，无法导出Excel格式`

**解决**:
```bash
pip install pandas openpyxl
```

### CSV导出为空

**原因**: 没有文本块结果数据

**解决**: 确保处理已完成并生成了文本块结果

### 导出目录权限错误

**错误**: `Permission denied`

**解决**: 检查导出目录的写入权限

### 内存不足

**错误**: 导出大文件时内存不足

**解决**: 
- 使用JSON或CSV格式（更节省内存）
- 分批导出数据
- 增加系统内存

## 最佳实践

1. **选择合适的格式**:
   - 数据分析: CSV或Excel
   - 程序处理: JSON
   - 文档展示: Markdown或HTML

2. **定期导出**: 处理完成后立即导出，避免数据丢失

3. **版本控制**: 为导出文件添加时间戳或版本号

4. **备份**: 重要数据导出后应备份

5. **清理**: 定期清理旧的导出文件，节省存储空间

## 示例场景

### 场景1: 数据分析

```bash
# 导出为CSV，用于Excel分析
python cli.py process --input novel.txt --export csv
```

### 场景2: 文档分享

```bash
# 导出为HTML，方便在浏览器中查看和分享
python cli.py process --input novel.txt --export html
```

### 场景3: 程序集成

```python
# 导出为JSON，供其他程序使用
exporter = create_exporter("./exports")
exporter.export_json(results, "novel_data")
```

### 场景4: 完整备份

```bash
# 导出所有格式，确保数据完整
python cli.py process --input novel.txt --export all
```

## 更多信息

- CLI使用指南: `CLI_GUIDE.md`
- API文档: 访问 `http://localhost:8000/docs` 查看Swagger文档
- 项目文档: `README.md`


