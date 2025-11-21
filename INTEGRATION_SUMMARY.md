# NovelForge 功能融合总结

## 📋 文档索引

本文档是 NovelForge 功能融合方案的总结和索引。详细设计请参考：

1. **[NOVELFORGE_INTEGRATION_PLAN.md](./NOVELFORGE_INTEGRATION_PLAN.md)** - 核心功能融合方案
2. **[WORKFLOW_INTEGRATION_GUIDE.md](./WORKFLOW_INTEGRATION_GUIDE.md)** - 创作流程融合指南
3. **[NOVELWEAVE_INTEGRATION.md](./NOVELWEAVE_INTEGRATION.md)** - NovelWeave 优点融合方案 ⭐

## 🎯 融合目标

将 NovelForge 的七大核心功能完整融合到现有的 NovelCorpusExtractor 系统中，实现从"语料提取工具"向"智能创作平台"的全面升级。

## ✨ 核心功能概览

### 1. 动态输出模型（Dynamic Output Schema）
- **技术栈**：Pydantic v2
- **功能**：可视化界面定义创作元素结构，AI输出自动校验
- **价值**：确保AI生成内容符合预期格式，实现高度结构化

### 2. 自由上下文注入（Free Context Injection）
- **技术栈**：表达式解析器
- **功能**：通过简单指令将项目中的任何卡片、字段、集合注入到提示词
- **价值**：实现复杂的上下文检索，支持灵活创作逻辑

### 3. 知识图谱驱动（Knowledge Graph）
- **技术栈**：Neo4j
- **功能**：自动/手动提取人物关系，动态注入到生成过程
- **价值**：解决一致性问题，减少AI幻觉，确保角色行为符合设定

### 4. 灵感助手（Inspiration Assistant）
- **技术栈**：对话式AI
- **功能**：对话式创作助手，支持跨项目引用，一键应用对话成果
- **价值**：让创作过程更自然高效，支持细节讨论和修改

### 5. 灵感工作台（Inspiration Workspace）
- **技术栈**：自由卡片系统
- **功能**：独立头脑风暴空间，创建自由卡片，支持跨项目引用
- **价值**：打破项目边界，自由组合创意，方便灵感落地

### 6. 雪花式创作流程（Snowflake Workflow）
- **技术栈**：工作流引擎
- **功能**：从一句话梗概逐步扩展到正文的树形创作流程
- **价值**：提供结构化创作引导，确保创作完整性

### 7. 高度可配置与可扩展（Highly Configurable）
- **技术栈**：配置管理系统
- **功能**：深度自定义AI模型参数、提示词模板、卡片类型等
- **价值**：打造完全属于自己的创作工作流

## 📊 系统架构升级

### 新增核心模块

```
NovelCorpusExtractor/
├── core/
│   ├── card_manager.py          # 卡片管理系统 ⭐
│   ├── project_manager.py       # 项目管理系统 ⭐
│   ├── dynamic_schema.py        # 动态输出模型 ⭐
│   ├── context_injector.py      # 自由上下文注入 ⭐
│   ├── knowledge_graph.py       # 知识图谱驱动 ⭐
│   ├── inspiration_assistant.py # 灵感助手 ⭐
│   ├── inspiration_workspace.py # 灵感工作台 ⭐
│   ├── snowflake_workflow.py    # 雪花式创作流程 ⭐
│   └── config_manager.py        # 配置管理器（增强）
├── workflows/                    # 工作流系统 ⭐
│   ├── base.py
│   ├── factory.py
│   ├── snowflake_workflow.py
│   ├── hero_journey_workflow.py
│   ├── three_act_workflow.py
│   └── ...
├── schemas/                      # 动态Schema定义 ⭐
│   ├── character_schema.py
│   ├── scene_schema.py
│   └── custom_schemas/
├── projects/                     # 项目存储 ⭐
│   └── {project_id}/
│       ├── cards/
│       ├── config.yaml
│       └── knowledge_graph.db
└── inspiration/                  # 灵感工作台数据 ⭐
    ├── free_cards/
    └── conversations/
├── agent_skills/                 # Agent Skills 系统 ⭐
    ├── extension/                # 扩展技能（系统内置）
    ├── project/                  # 项目技能（.agent/skills/）
    └── personal/                 # 个人技能（~/.novelweave/skills/）
```

## 🔄 数据模型升级

### 卡片系统（Card System）

所有创作元素以"卡片"形式存在：
- **卡片类型**：角色、场景、大纲、章节、正文等
- **树形组织**：支持父子关系和引用关系
- **元数据**：创建时间、更新时间、关联关系等

### 项目系统（Project System）

- **项目**：独立的创作单元
- **跨项目引用**：支持在不同项目间引用卡片
- **项目模板**：可保存和复用项目结构

## 🛠️ 技术栈扩展

### 新增依赖

```txt
# 动态输出模型
pydantic>=2.0.0

# 知识图谱
neo4j>=5.0.0

# 其他工具
python-dateutil>=2.8.0
```

### 现有依赖保持不变

- FastAPI（Web框架）
- PyYAML（配置管理）
- asyncio（异步处理）
- 各种LLM客户端（OpenAI、Gemini、DeepSeek等）

## 📈 实施路线图

### 阶段一：基础架构（2-3周）
- [ ] 实现卡片管理系统
- [ ] 实现项目管理系统
- [ ] 实现基础API接口
- [ ] 前端基础框架搭建
- [ ] 数据迁移工具（将现有记忆体迁移到卡片系统）

### 阶段二：核心功能（3-4周）
- [ ] 实现动态输出模型（Pydantic）
- [ ] 实现自由上下文注入
- [ ] 集成Neo4j知识图谱
- [ ] 实现灵感助手基础功能
- [ ] 前端核心界面开发

### 阶段三：高级功能（2-3周）
- [ ] 完善灵感工作台
- [ ] 实现雪花式创作流程
- [ ] 实现其他创作流程（英雄之旅、三幕式等）
- [ ] 实现配置管理系统
- [ ] 前端界面完善

### 阶段四：优化和测试（1-2周）
- [ ] 性能优化
- [ ] 功能测试
- [ ] 用户体验优化
- [ ] 文档完善
- [ ] 部署准备

## 🔌 API接口扩展

### 新增API端点

#### 卡片管理
- `POST /api/cards` - 创建卡片
- `GET /api/cards/{card_id}` - 获取卡片
- `PUT /api/cards/{card_id}` - 更新卡片
- `DELETE /api/cards/{card_id}` - 删除卡片
- `GET /api/cards` - 列出卡片（支持过滤）

#### 项目管理
- `POST /api/projects` - 创建项目
- `GET /api/projects` - 列出所有项目
- `GET /api/projects/{project_id}` - 获取项目详情
- `PUT /api/projects/{project_id}` - 更新项目
- `DELETE /api/projects/{project_id}` - 删除项目

#### 动态Schema
- `POST /api/schemas` - 创建Schema
- `GET /api/schemas/{schema_id}` - 获取Schema
- `PUT /api/schemas/{schema_id}` - 更新Schema
- `GET /api/schemas` - 列出所有Schema

#### 上下文注入
- `POST /api/context/inject` - 注入上下文到提示词

#### 知识图谱
- `POST /api/kg/extract` - 从文本提取关系
- `GET /api/kg/character/{character_id}` - 获取角色上下文
- `POST /api/kg/relationship` - 创建关系
- `GET /api/kg/graph` - 获取图谱可视化数据

#### 灵感助手
- `POST /api/inspiration/chat` - 与助手对话
- `POST /api/inspiration/apply` - 应用对话成果到卡片
- `GET /api/inspiration/conversations` - 获取对话列表

#### 灵感工作台
- `POST /api/workspace/free-cards` - 创建自由卡片
- `GET /api/workspace/free-cards` - 列出自由卡片
- `POST /api/workspace/move-to-project` - 移动到项目
- `POST /api/workspace/copy-to-project` - 复制到项目

#### 工作流
- `POST /api/workflows/start` - 启动工作流
- `POST /api/workflows/{workflow_id}/next` - 进入下一阶段
- `GET /api/workflows/{workflow_id}/progress` - 获取进度
- `GET /api/workflows/list` - 列出所有可用工作流

#### 七步方法论
- `POST /api/seven-step/constitution` - 创建/编辑创作原则
- `POST /api/seven-step/specify` - 定义故事需求
- `POST /api/seven-step/clarify` - 生成澄清问题
- `POST /api/seven-step/plan` - 生成创作计划
- `POST /api/seven-step/tasks` - 管理任务列表
- `POST /api/seven-step/write` - 执行写作任务
- `POST /api/seven-step/analyze` - 验证质量

#### Agent Skills
- `GET /api/skills` - 列出所有技能
- `GET /api/skills/{skill_id}` - 获取技能详情
- `POST /api/skills/activate` - 激活相关技能
- `POST /api/skills` - 创建自定义技能
- `PUT /api/skills/{skill_id}` - 更新技能
- `DELETE /api/skills/{skill_id}` - 删除技能

#### 斜杠命令
- `POST /api/commands/execute` - 执行斜杠命令
- `GET /api/commands/list` - 列出所有可用命令
- `GET /api/commands/autocomplete` - 命令自动补全

## 🎨 前端界面设计

### 主要界面模块

1. **项目工作区**
   - 项目列表视图
   - 项目详情页
   - 卡片树形视图
   - 卡片编辑器

2. **Schema编辑器**
   - 可视化Schema设计器
   - 字段配置面板
   - 实时预览和验证

3. **上下文注入编辑器**
   - 表达式编辑器（支持语法高亮）
   - 实时预览
   - 上下文选择器

4. **知识图谱可视化**
   - 关系图谱（使用D3.js或类似库）
   - 节点详情面板
   - 关系编辑界面

5. **灵感助手界面**
   - 对话界面（类似ChatGPT）
   - 上下文卡片显示
   - 应用建议按钮

6. **灵感工作台**
   - 自由卡片列表
   - 跨项目引用管理
   - 移动/复制操作

7. **工作流界面**
   - 工作流选择器
   - 工作流进度视图
   - 阶段扩展界面
   - 树形结构展示

8. **七步方法论界面**
   - 阶段导航和进度显示
   - 创作原则编辑器
   - 故事需求规范编辑器
   - 澄清问题交互界面
   - 任务管理界面
   - 质量验证报告

9. **Agent Skills 界面**
   - 技能浏览器
   - 技能编辑器（Markdown）
   - 技能激活状态显示
   - 技能市场（可选）

10. **斜杠命令界面**
    - 命令输入框（支持自动补全）
    - 命令历史
    - 命令帮助文档

## 🔐 安全与权限

### 权限控制
- 项目级别的访问控制
- 跨项目引用的权限验证
- API接口的认证和授权

### 数据安全
- 卡片数据的加密存储（可选）
- 知识图谱的访问控制
- 对话记录的隐私保护

## 📝 向后兼容性

### 数据迁移
- 现有记忆体数据（YAML格式）迁移到卡片系统
- 保持现有API接口的兼容性
- 提供迁移工具和脚本

### 功能兼容
- 现有语料提取功能保持不变
- 现有Agent系统继续工作
- 现有工作流工具继续可用

## 🚀 性能考虑

### 优化策略
- 卡片数据的索引和缓存
- 知识图谱查询优化
- 上下文注入的表达式缓存
- 工作流状态的持久化

### 扩展性
- 支持大规模项目（1000+卡片）
- 知识图谱的分布式部署（可选）
- 工作流的并行执行

## 📚 文档计划

### 用户文档
- [ ] 快速开始指南
- [ ] 功能使用教程
- [ ] 工作流使用指南
- [ ] API参考文档

### 开发文档
- [ ] 架构设计文档
- [ ] 模块开发指南
- [ ] 扩展开发指南
- [ ] 测试指南

## ✅ 检查清单

### 功能完整性
- [x] 动态输出模型设计
- [x] 自由上下文注入设计
- [x] 知识图谱驱动设计
- [x] 灵感助手设计
- [x] 灵感工作台设计
- [x] 雪花式创作流程设计
- [x] 其他创作流程设计（英雄之旅、三幕式等）
- [x] 高度可配置系统设计
- [x] 七步方法论设计 ⭐
- [x] Agent Skills 系统设计 ⭐
- [x] 斜杠命令系统设计 ⭐

### 技术实现
- [ ] 卡片管理系统实现
- [ ] 项目管理系统实现
- [ ] 动态Schema系统实现
- [ ] 上下文注入系统实现
- [ ] Neo4j集成实现
- [ ] 灵感助手实现
- [ ] 灵感工作台实现
- [ ] 工作流引擎实现
- [ ] 七步方法论工作流实现 ⭐
- [ ] Agent Skills 系统实现 ⭐
- [ ] 斜杠命令系统实现 ⭐

### 前端开发
- [ ] 项目工作区界面
- [ ] Schema编辑器界面
- [ ] 上下文注入编辑器界面
- [ ] 知识图谱可视化界面
- [ ] 灵感助手界面
- [ ] 灵感工作台界面
- [ ] 工作流界面

## 🎓 学习资源

### 相关技术
- [Pydantic文档](https://docs.pydantic.dev/)
- [Neo4j文档](https://neo4j.com/docs/)
- [FastAPI文档](https://fastapi.tiangolo.com/)
- [雪花创作法](https://www.advancedfictionwriting.com/articles/snowflake-method/)
- [NovelWeave项目](https://github.com/wordflowlab/novelweave) ⭐
- [novel-writer方法论](https://github.com/wordflowlab/novel-writer) ⭐

### 创作理论
- 英雄之旅（Joseph Campbell）
- 三幕式结构（Syd Field）
- 救猫咪节拍表（Blake Snyder）
- 雪花创作法（Randy Ingermanson）

## 📞 支持与反馈

如有问题或建议，请参考：
- 项目Issue跟踪
- 开发文档
- 用户社区

---

**注意**：本文档是融合方案的总结和索引。详细的技术设计和实现方案请参考：
- [NOVELFORGE_INTEGRATION_PLAN.md](./NOVELFORGE_INTEGRATION_PLAN.md)
- [WORKFLOW_INTEGRATION_GUIDE.md](./WORKFLOW_INTEGRATION_GUIDE.md)
- [NOVELWEAVE_INTEGRATION.md](./NOVELWEAVE_INTEGRATION.md) ⭐

**最后更新**：2025-01-XX

