# API 模式使用指南

## 概述

本项目**仅支持 API 模式**，不支持本地模型。所有 LLM 功能都通过外部 API 服务提供。

## 支持的 API 提供商

### 单 API 模式

在 `config.yaml` 中配置单个 API：

```yaml
model:
  model: "openai"  # openai / gemini / deepseek
  model_name: "gpt-4"
  api_key: "your-api-key"  # 或使用环境变量
  base_url: ""  # 可选，用于兼容 OpenAI API 格式的其他服务
```

### 多 API 池模式（推荐）

启用多 API 池可以实现负载均衡和故障转移：

```yaml
api_pool:
  enabled: true
  apis:
    - name: "openai_primary"
      provider: "openai"
      api_key: "${OPENAI_API_KEY}"  # 或直接填写
      model: "gpt-4"
      priority: 1
      enabled: true
    # ... 更多 API 配置
```

## 环境变量配置

推荐使用环境变量来管理 API 密钥：

### Windows (PowerShell)
```powershell
$env:OPENAI_API_KEY = "your-api-key"
$env:GEMINI_API_KEY = "your-api-key"
$env:DEEPSEEK_API_KEY = "your-api-key"
```

### Linux/Mac
```bash
export OPENAI_API_KEY="your-api-key"
export GEMINI_API_KEY="your-api-key"
export DEEPSEEK_API_KEY="your-api-key"
```

## API 配置检查

### 健康检查

启动 API 服务器后，访问健康检查端点：

```bash
curl http://localhost:8000/api/health
```

响应示例：
```json
{
  "status": "healthy",
  "llm_client": "available",
  "extractor": "available",
  "api_mode": "api_only"
}
```

### 配置信息

查看当前配置：

```bash
curl http://localhost:8000/api/config
```

## 常见问题

### 1. API 密钥未配置

**错误信息**：`LLM 客户端未初始化，请检查 API 配置`

**解决方法**：
- 检查 `config.yaml` 中的 `api_key` 配置
- 或设置相应的环境变量（如 `OPENAI_API_KEY`）
- 确保 API 密钥有效且有足够的配额

### 2. API 调用失败

**错误信息**：`API 调用失败: ...`

**可能原因**：
- API 密钥无效或过期
- 网络连接问题
- API 服务暂时不可用
- 配额已用完

**解决方法**：
- 验证 API 密钥
- 检查网络连接
- 查看 API 服务商的状态页面
- 检查账户配额

### 3. 多 API 池配置

如果使用多 API 池模式，确保：
- 至少有一个 API 配置为 `enabled: true`
- 每个 API 都有有效的 `api_key`
- `provider` 字段正确（openai, gemini, deepseek 等）

## API 端点

### 工作流相关

- `POST /api/workflows/start` - 启动工作流
- `GET /api/workflows/list` - 列出可用工作流
- `GET /api/workflows/{workflow_id}/progress` - 获取工作流进度

### 项目管理

- `POST /api/projects` - 创建项目
- `GET /api/projects` - 列出所有项目
- `GET /api/projects/{project_id}` - 获取项目详情

### 卡片管理

- `POST /api/cards` - 创建卡片
- `GET /api/cards/{card_id}` - 获取卡片

### 技能管理

- `GET /api/skills` - 列出所有技能

### 命令系统

- `POST /api/commands/execute` - 执行斜杠命令
- `GET /api/commands/list` - 列出可用命令

### 系统状态

- `GET /api/health` - 健康检查
- `GET /api/config` - 获取配置信息

## 注意事项

1. **仅使用 API**：本项目不支持本地模型，所有 LLM 功能都通过 API 提供
2. **API 密钥安全**：不要将 API 密钥提交到版本控制系统
3. **成本控制**：使用 API 会产生费用，请注意监控使用量
4. **网络要求**：需要稳定的网络连接才能使用 API 功能
5. **速率限制**：注意 API 提供商的速率限制，避免超出配额

## 故障排除

### 检查 API 连接

```python
# 测试 API 连接
from main import NovelCorpusExtractor

extractor = NovelCorpusExtractor("config.yaml")
# 如果初始化失败，会抛出异常，说明 API 配置有问题
```

### 查看日志

检查日志文件 `api_server.log` 或 `novel_extractor.log` 获取详细错误信息。

### 验证 API 密钥

使用 API 提供商的官方工具或文档验证 API 密钥是否有效。

---

**最后更新**: 2025-01-XX


