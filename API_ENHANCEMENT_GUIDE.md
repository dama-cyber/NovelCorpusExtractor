# API增强功能指南

## 🚀 概述

系统现已支持**全面的网络API管理**，包括：

- ✅ **10+ API提供商支持**（OpenAI, Claude, Gemini, DeepSeek, Moonshot, 零一万物, 通义千问, 文心一言, 智谱AI等）
- ✅ **智能负载均衡**（自动选择最佳API）
- ✅ **故障转移**（自动重试和切换）
- ✅ **速率限制处理**（自动限流）
- ✅ **成本优化**（按成本选择API）
- ✅ **性能优化**（按速度选择API）
- ✅ **缓存机制**（减少重复请求）
- ✅ **批量处理**（并发控制）
- ✅ **统计监控**（API使用情况）

## 📋 支持的API提供商

| 提供商 | 代码 | 说明 | 成本参考 |
|--------|------|------|----------|
| OpenAI | `openai` | GPT-4, GPT-3.5等 | $0.03/1K tokens |
| Anthropic | `anthropic` | Claude系列 | $0.015/1K tokens |
| Google Gemini | `gemini` | Gemini Pro | 免费 |
| DeepSeek | `deepseek` | DeepSeek Chat | $0.0014/1K tokens |
| Moonshot | `moonshot` | Moonshot AI | $0.012/1K tokens |
| 零一万物 | `zeroone` | Yi系列 | $0.008/1K tokens |
| 通义千问 | `qwen` | Qwen系列 | $0.008/1K tokens |
| 文心一言 | `ernie` | ERNIE Bot | $0.012/1K tokens |
| 智谱AI | `glm` | GLM-4 | $0.1/1K tokens |
| 自定义 | `custom` | 自定义API | 可配置 |

## ⚙️ 配置方式

### 方式1: 单API模式（简单）

```yaml
# config.yaml
model:
  model: "openai"
  model_name: "gpt-4"
  api_key: "sk-..."
```

### 方式2: 多API池模式（推荐）

```yaml
# config.yaml
api_pool:
  enabled: true  # 启用API池
  apis:
    - name: "openai_primary"
      provider: "openai"
      api_key: "sk-..."
      model: "gpt-4"
      priority: 1
      rate_limit: 60
      cost_per_1k_tokens: 0.03
      enabled: true
    
    - name: "claude_backup"
      provider: "anthropic"
      api_key: "sk-ant-..."
      model: "claude-3-5-sonnet-20241022"
      priority: 2
      rate_limit: 50
      cost_per_1k_tokens: 0.015
      enabled: true
    
    - name: "gemini_free"
      provider: "gemini"
      api_key: "..."
      model: "gemini-pro"
      priority: 3
      rate_limit: 60
      cost_per_1k_tokens: 0.0
      enabled: true
```

### 方式3: 环境变量配置

```bash
# 设置多个API密钥
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="..."
export DEEPSEEK_API_KEY="..."
```

## 🎯 优化策略

### 1. 成本优化模式

```python
from core.api_optimizer import OptimizationStrategy

optimizer = APIOptimizer(api_pool)
optimizer.set_strategy(OptimizationStrategy(minimize_cost=True))

# 自动选择最便宜的API
api_name = await optimizer.select_optimal_api(prompt_length=1000)
```

### 2. 速度优化模式

```python
optimizer.set_strategy(OptimizationStrategy(maximize_speed=True))
```

### 3. 质量优化模式

```python
optimizer.set_strategy(OptimizationStrategy(maximize_quality=True))
```

### 4. 平衡模式（默认）

```python
optimizer.set_strategy(OptimizationStrategy(balance=True))
# 综合考虑成本、速度、质量
```

## 🔧 高级功能

### 1. 自动故障转移

系统会自动：
- 检测API失败
- 自动重试（指数退避）
- 切换到备用API
- 记录错误统计

### 2. 速率限制处理

```yaml
api_pool:
  apis:
    - name: "openai"
      rate_limit: 60  # 每分钟60次请求
      # 系统会自动限流
```

### 3. 智能缓存

```python
# 相同提示词会自动使用缓存（1小时TTL）
result = await client.send_request(
    prompt="分析这段文本",
    use_cache=True  # 默认启用
)
```

### 4. 批量处理

```python
# 自动并发控制，避免过载
prompts = ["提示1", "提示2", "提示3", ...]
results = await client.batch_request(
    prompts,
    max_concurrent=10  # 最大并发数
)
```

### 5. 流式响应

```python
async for chunk in client.stream_request("长文本生成"):
    print(chunk, end="", flush=True)
```

## 📊 监控和统计

### 查看API使用统计

```python
stats = client.get_stats()
print(json.dumps(stats, indent=2))
```

输出示例：
```json
{
  "openai_primary": {
    "provider": "openai",
    "total_requests": 100,
    "success_rate": 98.0,
    "total_tokens": 50000,
    "total_cost": 1.5,
    "avg_response_time": 1.2,
    "consecutive_errors": 0,
    "enabled": true
  }
}
```

### 获取优化建议

```python
report = optimizer.get_optimization_report()
print(report)
```

## 🎨 使用示例

### 示例1: 多API自动切换

```python
# 配置多个API后，系统自动选择最佳API
result = await client.send_request(
    prompt="分析小说片段",
    # 不指定provider，系统自动选择
)
```

### 示例2: 指定API提供商

```python
result = await client.send_request(
    prompt="分析小说片段",
    provider="anthropic"  # 强制使用Claude
)
```

### 示例3: 成本优化

```python
# 设置成本优化策略
optimizer.set_strategy(OptimizationStrategy(minimize_cost=True))

# 系统会自动选择最便宜的可用API
result = await client.send_request("长文本分析")
```

### 示例4: 自定义API

```yaml
api_pool:
  apis:
    - name: "custom_api"
      provider: "custom"
      api_key: "..."
      base_url: "https://api.example.com/v1/chat"
      metadata:
        headers:
          "X-Custom-Header": "value"
        format_request: "custom_format_func"
        parse_response: "custom_parse_func"
```

## ⚡ 性能优化

### 1. 并发控制

系统自动：
- 根据API数量调整并发
- 避免超过速率限制
- 智能任务调度

### 2. 连接池复用

- HTTP连接复用
- 减少连接开销
- 提升响应速度

### 3. 智能重试

- 指数退避策略
- 自动故障恢复
- 避免重复失败

## 🔒 安全建议

1. **API密钥管理**
   - 使用环境变量存储密钥
   - 不要提交密钥到版本控制
   - 定期轮换密钥

2. **访问控制**
   - 设置合理的速率限制
   - 监控异常使用
   - 及时禁用异常API

3. **成本控制**
   - 设置成本预算
   - 监控token消耗
   - 使用缓存减少请求

## 📈 最佳实践

1. **多API配置**
   - 配置2-3个备用API
   - 设置不同优先级
   - 启用成本优化

2. **监控使用**
   - 定期查看统计报告
   - 关注错误率
   - 优化API选择

3. **性能调优**
   - 根据场景选择策略
   - 调整并发数
   - 启用缓存

## 🆘 故障排查

### 问题1: API调用失败

**检查**:
- API密钥是否正确
- 网络连接是否正常
- 速率限制是否超限

**解决**:
- 系统会自动重试和切换
- 查看日志了解详情
- 检查API状态

### 问题2: 成本过高

**解决**:
- 启用成本优化模式
- 使用更便宜的API
- 启用缓存减少请求

### 问题3: 速度慢

**解决**:
- 启用速度优化模式
- 增加并发数
- 使用更快的API

---

**更多信息**: 查看 `core/api_manager.py` 和 `core/api_optimizer.py` 源码

