# NovelCorpusExtractor · Web 控制台

一个使用 Vite + React + TypeScript 构建的轻量前端，完整映射 `NovelCorpusExtractor` 中 `agents/`、`core/`、`tools/` 的全部模块。支持上传小说原文、选择拓扑/模型池、勾选创作增强工具，并将 Reader / Scanner / Extractor / Analyst / Planner / Archivist / Stylist / Creative Workflow 的执行状态可视化，同时展示 10+ 创作工具输出与核心服务（TopologyManager、APIOptimizer、FrankentextsManager、MemoryManager 等）的实时配置。

## 功能概览

- 文件上传 + 示例文本输入，便于本地或粘贴式测试
- 拓扑模式（auto / linear / triangular / swarm）与 API 池切换
- 10+ 创作工具（含世界观冲突、反派建模占位）的多选控制，与 `tools/` 目录逐一对应
- 工作流进度视图 + 模块总览，覆盖 Reader / Scanner / Extractor / Analyst / Planner / Archivist / Stylist / Creative Workflow
- 核心服务看板，实时展示 TopologyManager / APIOptimizer / FrankentextsManager / MemoryManager / GenreEnhancer / CreativeWorkflowPipeline 的配置状态
- 记忆体、chunk 以及创作增强结果的可视化卡片
- DEV 环境下自动回退到 mock 数据，前后台可独立调试

## 快速开始

```bash
cd frontend
npm install
npm run dev
```

默认会在 `http://localhost:5173` 启动。构建发布可执行：

```bash
npm run build
npm run preview
```

## API 对接

前端期望后端提供 `POST /api/process` 接口（可由 FastAPI / Flask / 本地中转服务实现）。请求格式为 `multipart/form-data`：

| 字段             | 说明                          |
| ---------------- | ----------------------------- |
| `file`           | 小说原文文件（可选）          |
| `novel_type`     | 玄幻/都市/言情...             |
| `topology_mode`  | auto / linear / triangular... |
| `api_pool_mode`  | auto / single / triple / swarm |
| `sample_text`    | 粘贴文本片段（可选）          |
| `workflow_targets` | 需要运行的创作工具 id 列表（JSON 字符串） |
| `run_creative_flow` | 是否启动创作流程（布尔） |

响应示例可参考 `src/services/mockData.ts`，包含：

- `chunk_results`：每个 chunk 的摘要、hook 评分等
- `workflowStages`：各 Agent 模块的状态（Reader/Scanner/Extractor/...）
- `workflow`：创作工作流的三大分支 `creationFlow` / `optimizationFlow` / `detectionFlow`
- `memories`：YAML 记忆体预览
- `creative`：为旧版接口保留的向后兼容字段

### 环境变量

- `VITE_API_BASE`：指定后端地址（默认 `/api`，本地 dev 使用 Vite proxy）
- `VITE_API_PROXY`：仅 dev server 使用，用于将 `/api` 代理到真实后端，例如 `http://127.0.0.1:8000`

可在根目录创建 `.env` / `.env.development`：

```
VITE_API_BASE=/api
VITE_API_PROXY=http://localhost:8000
```

## 目录结构

```
frontend/
├── src/
│   ├── App.tsx                 # 主界面
│   ├── constants.ts            # 小说类型、拓扑、workflow 配置
│   ├── services/
│   │   ├── api.ts              # 与后端交互，DEV 下支持 mock
│   │   └── mockData.ts
│   ├── types.ts                # 共享类型
│   └── index.css               # 全局样式
├── vite.config.ts              # 含 React 插件与 /api 代理
├── package.json
└── README.md
```

## 后续扩展建议

- 将 `workflowStages` 切换为 SSE / WebSocket，展示实时进度
- 结合 `output/` 目录中的 YAML 记忆体，提供下载/编辑入口
- 增加 Frankentexts 向量检索结果的可视化（雷达图、Timeline 等）
- 对接身份系统或 API Key 表单，便于多用户共享

