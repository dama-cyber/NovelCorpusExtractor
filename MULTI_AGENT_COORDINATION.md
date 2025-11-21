# 多Agent协同机制使用指南

## 概述

多Agent协同机制根据可用API数量（1-5个）智能分配Agent角色，实现高效的并行处理和协同工作。

## 支持的API数量配置

### 1个API - 单API串行模式

**策略名称**: 单API串行模式

**特点**:
- 所有Agent串行执行，共享单个API
- 稳定可靠，适合资源受限环境
- 执行顺序：Reader → Analyst → Planner → Writer → Critic

**Agent分配**:
- Reader (API 0, 优先级1)
- Analyst (API 0, 优先级2)
- Planner (API 0, 优先级3)
- Writer (API 0, 优先级4)
- Critic (API 0, 优先级5)

**适用场景**:
- 只有1个API可用
- 对速度要求不高
- 需要稳定可靠的执行

---

### 2个API - 双API并行模式

**策略名称**: 双API并行模式

**特点**:
- 核心Agent并行执行，辅助Agent串行
- Reader和Analyst可以并行工作
- 提高前期分析效率

**Agent分配**:
- Reader (API 0, 优先级1, 可并行)
- Analyst (API 1, 优先级1, 可并行)
- Planner (API 0, 优先级2)
- Writer (API 1, 优先级3)
- Critic (API 0, 优先级4)

**适用场景**:
- 有2个API可用
- 需要提高分析阶段效率
- 平衡速度和资源使用

---

### 3个API - 三API三角模式

**策略名称**: 三API三角模式

**特点**:
- 分析-规划-写作三角协同
- Reader、Analyst、Extractor并行执行
- Stylist可以并行优化
- Critic串行审查

**Agent分配**:
- Reader (API 0, 优先级1, 可并行)
- Analyst (API 1, 优先级1, 可并行)
- Extractor (API 2, 优先级1, 可并行)
- Planner (API 0, 优先级2)
- Writer (API 1, 优先级3)
- Stylist (API 2, 优先级3, 可并行)
- Critic (API 0, 优先级4)

**适用场景**:
- 有3个API可用
- 需要语料库检索功能
- 需要风格优化
- 平衡功能完整性和效率

---

### 4个API - 四API协同模式

**策略名称**: 四API协同模式

**特点**:
- 多阶段并行执行
- Reader、Analyst、Extractor、Planner可以并行
- Stylist可以并行优化
- Critic独立审查
- Archivist保存记录

**Agent分配**:
- Reader (API 0, 优先级1, 可并行)
- Analyst (API 1, 优先级1, 可并行)
- Extractor (API 2, 优先级1, 可并行)
- Planner (API 3, 优先级1, 可并行)
- Writer (API 0, 优先级2)
- Stylist (API 1, 优先级2, 可并行)
- Critic (API 2, 优先级3)
- Archivist (API 3, 优先级4)

**适用场景**:
- 有4个API可用
- 需要完整的创作流程
- 需要高质量输出
- 需要记录保存功能

---

### 5个API - 五API蜂群模式

**策略名称**: 五API蜂群模式

**特点**:
- 全功能并行执行
- 最大化并行度
- 所有核心Agent可以并行工作
- 最高效率

**Agent分配**:
- Reader (API 0, 优先级1, 可并行)
- Analyst (API 1, 优先级1, 可并行)
- Extractor (API 2, 优先级1, 可并行)
- Planner (API 3, 优先级1, 可并行)
- Writer (API 4, 优先级2)
- Stylist (API 0, 优先级2, 可并行)
- Critic (API 1, 优先级3, 可并行)
- Archivist (API 2, 优先级4)

**适用场景**:
- 有5个API可用
- 需要最高效率
- 大规模创作任务
- 对速度要求极高

---

## 使用方法

### 1. 配置API池

在 `config.yaml` 中配置多个API：

```yaml
api_pool:
  enabled: true
  apis:
    - name: "openai_primary"
      provider: "openai"
      api_key: "${OPENAI_API_KEY}"
      model: "gpt-4"
      enabled: true
      priority: 1
    - name: "gemini_primary"
      provider: "gemini"
      api_key: "${GEMINI_API_KEY}"
      model: "gemini-pro"
      enabled: true
      priority: 2
    - name: "deepseek_primary"
      provider: "deepseek"
      api_key: "${DEEPSEEK_API_KEY}"
      model: "deepseek-chat"
      enabled: true
      priority: 3
    # 可以继续添加更多API...
```

### 2. 初始化工作流

工作流会自动检测可用API数量并选择相应的协同策略：

```python
from core.workflows import WorkflowFactory
from core.enhanced_model_interface import create_enhanced_client_from_config

# 创建多API客户端
api_configs = [
    {"provider": "openai", "api_key": "...", "model": "gpt-4"},
    {"provider": "gemini", "api_key": "...", "model": "gemini-pro"},
    # ... 更多API配置
]

llm_client = create_enhanced_client_from_config(api_configs)

# 创建工作流（会自动使用多Agent协同）
workflow = WorkflowFactory.create_workflow(
    "seven_step",
    project_id="my_novel",
    card_manager=card_manager,
    project_manager=project_manager,
    llm_client=llm_client
)
```

### 3. 查看协同策略信息

```python
# 获取协同策略信息
strategy_info = workflow.agent_coordinator.get_strategy_info()
print(f"策略名称: {strategy_info['strategy_name']}")
print(f"可用API数量: {strategy_info['available_apis']}")
print(f"Agent分配:")
for assignment in strategy_info['assignments']:
    print(f"  - {assignment['role']}: API {assignment['api_name']}, 优先级{assignment['priority']}, 可并行={assignment['can_parallel']}")
```

### 4. 执行工作流

工作流会自动根据可用API数量使用相应的协同策略：

```python
# 执行写作阶段（会自动使用多Agent协同）
result = await workflow.expand_stage(write_stage)

# 结果中包含Agent协同信息
if 'agent_coordination' in result:
    print(f"使用的协同策略: {result['agent_coordination']['strategy_name']}")
    print(f"Agent执行结果: {result.get('agent_results', {})}")
```

---

## Agent角色说明

### Reader (阅读者)
- **职责**: 分析任务上下文，理解需求
- **使用阶段**: Write阶段
- **并行能力**: 是（2+ API）

### Analyst (分析者)
- **职责**: 深度分析任务需求，提取关键信息
- **使用阶段**: Write阶段、Analyze阶段
- **并行能力**: 是（2+ API）

### Extractor (提取者)
- **职责**: 从语料库检索相关片段
- **使用阶段**: Write阶段
- **并行能力**: 是（3+ API）

### Planner (规划者)
- **职责**: 规划写作结构和策略
- **使用阶段**: Write阶段
- **并行能力**: 是（4+ API）

### Writer (写作者)
- **职责**: 执行实际写作任务
- **使用阶段**: Write阶段
- **并行能力**: 否（必须串行）

### Stylist (风格师)
- **职责**: 优化文本风格和表达
- **使用阶段**: Write阶段
- **并行能力**: 是（3+ API）

### Critic (评论者)
- **职责**: 质量审查和优化建议
- **使用阶段**: Write阶段、Analyze阶段
- **并行能力**: 是（5 API）

### Archivist (档案员)
- **职责**: 保存记录和归档
- **使用阶段**: 所有阶段
- **并行能力**: 否（通常串行）

---

## 性能优化建议

### 1. API优先级设置
- 将性能最好的API设置为最高优先级（priority: 1）
- 将成本最低的API用于大量并行任务
- 将质量最高的API用于关键任务（如Writer、Critic）

### 2. 负载均衡
- 系统会自动根据API的可用性和性能进行负载均衡
- 监控API使用统计，调整优先级

### 3. 缓存策略
- 启用API缓存可以减少重复调用
- 对于相似的任务，可以复用之前的分析结果

### 4. 错误处理
- 系统会自动处理API失败，切换到备用API
- 连续错误超过5次的API会被暂时禁用

---

## 监控和调试

### 查看API统计

```python
# 获取API使用统计
stats = llm_client.get_stats()
for api_name, stat in stats.items():
    print(f"{api_name}:")
    print(f"  总请求数: {stat['total_requests']}")
    print(f"  成功率: {stat['success_rate']:.2f}%")
    print(f"  平均响应时间: {stat['avg_response_time']:.2f}s")
    print(f"  总Token数: {stat['total_tokens']}")
    print(f"  总成本: ${stat['total_cost']:.4f}")
```

### 查看Agent执行结果

```python
# 在Write阶段结果中查看Agent执行详情
result = await workflow.expand_stage(write_stage)
if 'agent_results' in result:
    for role, agent_result in result['agent_results'].items():
        print(f"{role}: {agent_result}")
```

---

## 常见问题

### Q: 如何知道当前使用了哪个协同策略？

A: 查看工作流的 `agent_coordinator.get_strategy_info()` 方法返回的信息。

### Q: 可以手动指定使用哪个API吗？

A: 可以，通过设置API的 `priority` 参数，系统会优先使用高优先级的API。

### Q: 如果某个API失败了怎么办？

A: 系统会自动切换到备用API，如果所有API都失败，会抛出异常。

### Q: 如何优化多Agent协同的性能？

A: 
1. 确保API配置正确，所有API都可用
2. 设置合理的API优先级
3. 监控API使用统计，调整配置
4. 使用缓存减少重复调用

---

## 最佳实践

1. **API配置**: 至少配置2-3个API以获得最佳性能
2. **优先级设置**: 将最可靠的API设置为最高优先级
3. **监控**: 定期查看API使用统计，优化配置
4. **错误处理**: 确保有备用API，避免单点故障
5. **成本控制**: 使用成本较低的API进行大量并行任务

---

## 更新日志

- **v1.0.0** (2024): 初始版本，支持1-5个API的协同机制
  - 实现5种协同策略
  - 支持8种Agent角色
  - 自动负载均衡和错误处理


