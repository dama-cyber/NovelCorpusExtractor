# NovelCorpusExtractor API客户端库

Python客户端库，用于调用NovelCorpusExtractor API服务。

## 安装

```bash
pip install requests aiohttp
```

## 快速开始

### 同步客户端

```python
from client import NovelCorpusClient

# 创建客户端
client = NovelCorpusClient(
    base_url="http://localhost:8000",
    timeout=300
)

# 检查健康状态
health = client.health_check()
print(f"服务器状态: {health.status}")

# 创建项目
project = client.create_project(
    name="我的小说项目",
    description="一个测试项目"
)
print(f"项目ID: {project.id}")

# 处理小说文件
result = client.process_novel(
    file_path="novel.txt",
    novel_type="玄幻",
    workflow_targets=["角色", "情节"]
)
print(f"处理完成，共 {len(result.chunk_results)} 个结果")

# 关闭客户端
client.close()
```

### 异步客户端

```python
import asyncio
from client import AsyncNovelCorpusClient

async def main():
    async with AsyncNovelCorpusClient(
        base_url="http://localhost:8000"
    ) as client:
        # 检查健康状态
        health = await client.health_check()
        print(f"服务器状态: {health.status}")
        
        # 创建项目
        project = await client.create_project(
            name="我的小说项目"
        )
        print(f"项目ID: {project.id}")

asyncio.run(main())
```

## API方法

### 健康检查

- `health_check()` - 检查服务器健康状态
- `get_config()` - 获取配置信息

### 项目管理

- `list_projects()` - 列出所有项目
- `get_project(project_id)` - 获取项目详情
- `create_project(name, description, template_id)` - 创建项目
- `update_project(project_id, name, description)` - 更新项目
- `delete_project(project_id)` - 删除项目

### 卡片管理

- `list_cards(project_id)` - 列出卡片
- `get_card(card_id)` - 获取卡片详情
- `create_card(name, card_type, content, project_id)` - 创建卡片

### 工作流管理

- `list_workflows()` - 列出可用工作流
- `start_workflow(workflow_name, project_id, initial_data)` - 启动工作流
- `get_workflow_progress(workflow_id)` - 获取工作流进度
- `next_workflow_stage(workflow_id)` - 进入下一阶段

### 处理小说

- `process_novel(file_path, sample_text, novel_type, ...)` - 处理小说文件或文本

### 命令系统

- `list_commands()` - 列出可用命令
- `execute_command(command, args)` - 执行斜杠命令

### 技能管理

- `list_skills()` - 列出所有技能

## 错误处理

客户端会自动处理重试和错误：

```python
from client import NovelCorpusClient
from core.exceptions import APIError, ValidationError

client = NovelCorpusClient()

try:
    project = client.create_project("测试项目")
except ValidationError as e:
    print(f"验证错误: {e}")
except APIError as e:
    print(f"API错误: {e}")
```

## 配置

客户端支持以下配置选项：

- `base_url`: API服务器地址（默认: http://localhost:8000）
- `api_key`: API密钥（可选）
- `timeout`: 请求超时时间，秒（默认: 300）
- `max_retries`: 最大重试次数（默认: 3）

## 示例

### 批量处理文件

```python
from client import NovelCorpusClient
from pathlib import Path

client = NovelCorpusClient()

# 创建项目
project = client.create_project("批量处理项目")

# 处理多个文件
files = Path("novels").glob("*.txt")
for file_path in files:
    try:
        result = client.process_novel(
            file_path=str(file_path),
            novel_type="通用"
        )
        print(f"处理完成: {file_path.name}")
    except Exception as e:
        print(f"处理失败 {file_path.name}: {e}")

client.close()
```

### 监控工作流进度

```python
from client import NovelCorpusClient
import time

client = NovelCorpusClient()

# 启动工作流
workflow = client.start_workflow(
    workflow_name="seven_step",
    project_id="project_123"
)

# 监控进度
while True:
    progress = client.get_workflow_progress(workflow.id)
    print(f"进度: {progress.progress_percentage:.1f}%")
    
    if progress.status == "completed":
        print("工作流完成！")
        break
    elif progress.status == "failed":
        print("工作流失败！")
        break
    
    time.sleep(2)

client.close()
```

## 许可证

与主项目相同。


