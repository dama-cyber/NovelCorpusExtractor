import { useMemo, useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import {
  AGENT_MODULES,
  API_POOL_OPTIONS,
  CORE_SERVICES,
  NOVEL_TYPES,
  TOPOLOGY_OPTIONS,
  WORKFLOW_TARGETS,
} from './constants'
import { processNovel } from './services/api'
import type {
  ProcessPayload,
  ProcessResponse,
  WorkflowStageSnapshot,
  WorkflowSummary,
  WorkflowTargetMeta,
} from './types'

const selectableTargets = WORKFLOW_TARGETS.filter((target) => !target.disabled)
const defaultTargets = selectableTargets.slice(0, 4).map((item) => item.id)

const initialPayload: ProcessPayload = {
  novelType: NOVEL_TYPES[0],
  topologyMode: 'auto',
  apiPoolMode: 'auto',
  workflowTargets: defaultTargets,
  runCreativeFlow: true,
}

export default function App() {
  const [payload, setPayload] = useState<ProcessPayload>(initialPayload)
  const [fileName, setFileName] = useState<string>('')
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<ProcessResponse | null>(null)
  const [workflowStages, setWorkflowStages] = useState<WorkflowStageSnapshot[]>([])
  const [workflowSummary, setWorkflowSummary] = useState<WorkflowSummary | null>(null)

  const selectedTargetLabels = useMemo(
    () =>
      WORKFLOW_TARGETS.filter((target) => payload.workflowTargets.includes(target.id)).map(
        (target) => target.label
      ),
    [payload.workflowTargets]
  )

  const creativeToolsEnabled = payload.runCreativeFlow && payload.workflowTargets.length > 0

  const stageMap = useMemo(
    () =>
      workflowStages.reduce<Record<string, WorkflowStageSnapshot>>((acc, stage) => {
        acc[stage.id] = stage
        return acc
      }, {}),
    [workflowStages]
  )

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const inputFile = event.target.files?.[0]
    setPayload((prev) => ({ ...prev, file: inputFile ?? null }))
    setFileName(inputFile?.name ?? '')
  }

  const handleTargetToggle = (targetId: string, disabled?: boolean) => {
    if (disabled) return
    setPayload((prev) => {
      const nextTargets = prev.workflowTargets.includes(targetId)
        ? prev.workflowTargets.filter((id) => id !== targetId)
        : [...prev.workflowTargets, targetId]
      return { ...prev, workflowTargets: nextTargets }
    })
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!payload.file && !payload.sampleText) {
      setError('请上传小说文件或粘贴一段文本片段。')
      return
    }

    setProcessing(true)
    setError(null)
    setResult(null)
    setWorkflowStages([])
    setWorkflowSummary(null)

    try {
      const response = await processNovel(payload)
      setResult(response)
      setWorkflowStages(normalizeStages(response))
      setWorkflowSummary(normalizeWorkflow(response.workflow))
    } catch (err) {
      const message = err instanceof Error ? err.message : '处理失败，请稍后再试'
      setError(message)
    } finally {
      setProcessing(false)
    }
  }

  return (
    <div className="app-shell">
      <header style={{ marginBottom: '2rem' }}>
        <p className="pill">NovelCorpusExtractor · Web 控制台</p>
        <h1 style={{ marginBottom: '0.5rem' }}>一键触发多智能体小说语料提取</h1>
        <p style={{ color: '#475569', maxWidth: 620 }}>
          上传原始文本、选择小说类型与拓扑模式，即可运行 Reader / Analyst / Archivist / Creative
          Workflow。前端会实时展示工作流进度、记忆体产物以及 10 大创作工具的优化结果。
        </p>
      </header>

      <div className="grid two" style={{ marginBottom: '1.5rem' }}>
        <section className="card">
          <h3>输入配置</h3>
          <form className="grid" style={{ gap: '1rem' }} onSubmit={handleSubmit}>
            <label className="grid">
              <span style={{ fontWeight: 600 }}>小说文件</span>
              <input
                type="file"
                accept=".txt,.md,.json"
                onChange={handleFileChange}
                style={{ padding: '0.7rem', borderRadius: '12px', border: '1px solid #cbd5f5' }}
              />
              {fileName && <small style={{ color: '#475569' }}>{fileName}</small>}
            </label>

            <label className="grid">
              <span style={{ fontWeight: 600 }}>示例文本（可选）</span>
              <textarea
                rows={4}
                placeholder="可粘贴1-2段文本，帮助风格/题材检测"
                value={payload.sampleText ?? ''}
                onChange={(event) =>
                  setPayload((prev) => ({ ...prev, sampleText: event.target.value }))
                }
                style={{
                  borderRadius: '14px',
                  padding: '0.9rem',
                  border: '1px solid #cbd5f5',
                  resize: 'vertical',
                }}
              />
            </label>

            <div className="grid two">
              <label className="grid">
                <span style={{ fontWeight: 600 }}>小说类型</span>
                <select
                  value={payload.novelType}
                  onChange={(event) =>
                    setPayload((prev) => ({ ...prev, novelType: event.target.value }))
                  }
                  style={{ padding: '0.7rem', borderRadius: '12px', border: '1px solid #cbd5f5' }}
                >
                  {NOVEL_TYPES.map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
              </label>

              <label className="grid">
                <span style={{ fontWeight: 600 }}>拓扑模式</span>
                <select
                  value={payload.topologyMode}
                  onChange={(event) =>
                    setPayload((prev) => ({ ...prev, topologyMode: event.target.value as any }))
                  }
                  style={{ padding: '0.7rem', borderRadius: '12px', border: '1px solid #cbd5f5' }}
                >
                  {TOPOLOGY_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <label className="grid">
              <span style={{ fontWeight: 600 }}>API 池</span>
              <select
                value={payload.apiPoolMode}
                onChange={(event) =>
                  setPayload((prev) => ({ ...prev, apiPoolMode: event.target.value as any }))
                }
                style={{ padding: '0.7rem', borderRadius: '12px', border: '1px solid #cbd5f5' }}
              >
                {API_POOL_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>

            <div>
              <p className="section-title">创作工具选择</p>
              <div
                style={{
                  display: 'grid',
                  gap: '0.4rem',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
                }}
              >
                {WORKFLOW_TARGETS.map((target) => (
                  <label
                    key={target.id}
                    style={{
                      display: 'flex',
                      gap: '0.45rem',
                      alignItems: 'center',
                      background: payload.workflowTargets.includes(target.id)
                        ? 'rgba(59, 130, 246, 0.12)'
                        : '#f8fafc',
                      padding: '0.55rem 0.7rem',
                      borderRadius: '12px',
                      border: '1px solid rgba(148, 163, 184, 0.4)',
                      fontSize: '0.9rem',
                      opacity: target.disabled ? 0.6 : 1,
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={payload.workflowTargets.includes(target.id)}
                      disabled={target.disabled}
                      onChange={() => handleTargetToggle(target.id, target.disabled)}
                    />
                    <span style={{ display: 'inline-flex', flexDirection: 'column' }}>
                      <span>{target.label}</span>
                      <small style={{ color: '#64748b', fontSize: '0.75rem' }}>
                        {target.module}
                      </small>
                    </span>
                  </label>
                ))}
              </div>
            </div>

            <label
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.65rem',
                background: '#f8fafc',
                borderRadius: '14px',
                padding: '0.7rem 1rem',
                border: '1px solid rgba(148, 163, 184, 0.4)',
              }}
            >
              <input
                type="checkbox"
                checked={payload.runCreativeFlow}
                onChange={(event) =>
                  setPayload((prev) => ({ ...prev, runCreativeFlow: event.target.checked }))
                }
              />
              启动 10 阶段创作增强工作流
            </label>

            <button className="primary-button" type="submit" disabled={processing}>
              {processing ? '处理中...' : '开始提取'}
            </button>
            {error && <p style={{ color: '#dc2626', margin: 0 }}>{error}</p>}
          </form>
        </section>

        <section className="card">
          <h3>工作流进度</h3>
          {processing && (
            <p style={{ marginTop: 0, color: '#475569' }}>正在等待后端响应，请稍候...</p>
          )}
          {!processing && workflowStages.length === 0 && (
            <p style={{ marginTop: 0, color: '#94a3b8' }}>提交任务后将展示各 Agent 状态。</p>
          )}
          <div className="grid" style={{ gap: '0.75rem' }}>
            {workflowStages.map((stage) => (
              <article
                key={stage.id}
                style={{
                  border: '1px solid rgba(148,163,184,.35)',
                  borderRadius: '12px',
                  padding: '0.75rem 1rem',
                  background:
                    stage.status === 'completed'
                      ? 'rgba(34,197,94,0.08)'
                      : stage.status === 'failed'
                        ? 'rgba(248,113,113,0.12)'
                        : 'rgba(226,232,240,0.5)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <strong>{stage.label}</strong>
                  <span className="tag">{stage.status}</span>
                </div>
                {stage.detail && (
                  <p style={{ margin: '0.3rem 0 0', color: '#475569', fontSize: '0.9rem' }}>
                    {stage.detail}
                  </p>
                )}
              </article>
            ))}
          </div>
          <hr style={{ margin: '1.5rem 0', borderColor: 'rgba(148,163,184,0.3)' }} />
          <h4 style={{ margin: '0 0 0.6rem' }}>已启用的创作工具</h4>
          {creativeToolsEnabled ? (
            <ul style={{ margin: 0, paddingLeft: '1.2rem', color: '#475569' }}>
              {selectedTargetLabels.map((label) => (
                <li key={label}>{label}</li>
              ))}
            </ul>
          ) : (
            <p style={{ color: '#94a3b8', margin: 0 }}>未选择任何创作工具。</p>
          )}
        </section>
      </div>

      <section className="card" style={{ marginBottom: '1.5rem' }}>
        <h3>智能体模块映射</h3>
        <div className="modules-grid">
          {AGENT_MODULES.map((module) => {
            const stage = stageMap[module.id]
            const status = stage?.status ?? 'pending'
            return (
              <article key={module.id} className="module-card">
                <div className="module-card__header">
                  <strong>{module.label}</strong>
                  <span className={`tag tag--${status}`}>{statusLabel(status)}</span>
                </div>
                <p className="module-card__description">{module.description}</p>
                <small className="module-card__file">{module.file}</small>
                {stage?.detail && <p className="module-card__detail">{stage.detail}</p>}
              </article>
            )
          })}
        </div>
      </section>

      <section className="card" style={{ marginBottom: '1.5rem' }}>
        <h3>核心服务组件</h3>
        <div className="modules-grid">
          {CORE_SERVICES.map((service) => (
            <article key={service.id} className="module-card">
              <div className="module-card__header">
                <strong>{service.label}</strong>
                <span className="tag">{resolveCoreValue(service.id, payload)}</span>
              </div>
              <p className="module-card__description">{service.description}</p>
              <small className="module-card__file">{service.file}</small>
            </article>
          ))}
        </div>
      </section>

      <section className="card" style={{ marginBottom: '1.5rem' }}>
        <h3>创作工具映射</h3>
        <p style={{ marginTop: '-0.2rem', color: '#475569' }}>
          与后端 `tools/` 模块一一对应，开关状态由上方表单控制。
        </p>
        <div className="modules-grid">
          {WORKFLOW_TARGETS.map((target) => {
            const isActive = payload.workflowTargets.includes(target.id) && creativeToolsEnabled
            const status = target.disabled ? '即将上线' : isActive ? '已启用' : '未启用'
            const snippet = extractToolSnippet(target, workflowSummary, result?.creative)
            return (
              <article key={target.id} className="module-card">
                <div className="module-card__header">
                  <strong>{target.label}</strong>
                  <span className="tag">{status}</span>
                </div>
                <p className="module-card__description">{target.description}</p>
                <small className="module-card__file">{target.file}</small>
                {snippet && <p className="module-card__detail">{snippet}</p>}
              </article>
            )
          })}
        </div>
      </section>

      {result && (
        <>
          <section className="card" style={{ marginBottom: '1.5rem' }}>
            <h3>提取结果总览</h3>
            <div className="grid two">
              <div>
                <p className="section-title">文本块</p>
                <p style={{ margin: 0, fontSize: '2rem', fontWeight: 700 }}>
                  {result.chunkResults.length}
                </p>
                <small style={{ color: '#475569' }}>chunk_results</small>
              </div>
              <div>
                <p className="section-title">最新时间戳</p>
                <p style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600 }}>
                  {result.emittedAt
                    ? new Date(result.emittedAt).toLocaleString()
                    : '来自 mock 数据'}
                </p>
              </div>
            </div>
            {result.outline && (
              <pre
                style={{
                  marginTop: '1rem',
                  background: '#0f172a',
                  color: '#e2e8f0',
                  padding: '1rem',
                  borderRadius: '16px',
                  whiteSpace: 'pre-wrap',
                }}
              >
                {result.outline}
              </pre>
            )}
          </section>

          {result.memories && (
            <section className="card" style={{ marginBottom: '1.5rem' }}>
              <h3>记忆体预览</h3>
              <div className="grid two">
                {result.memories.map((memory) => (
                  <article
                    key={memory.id}
                    style={{
                      border: '1px solid rgba(148,163,184,0.4)',
                      borderRadius: '14px',
                      padding: '1rem',
                      background: '#f8fafc',
                    }}
                  >
                    <strong>{memory.title}</strong>
                    <ul style={{ paddingLeft: '1.1rem', color: '#475569' }}>
                      {memory.entries.map((entry, index) => (
                        <li key={`${memory.id}-${index}`}>{entry}</li>
                      ))}
                    </ul>
                  </article>
                ))}
              </div>
            </section>
          )}

          <section className="card" style={{ marginBottom: '1.5rem' }}>
            <h3>Chunk 详情</h3>
            <div className="grid">
              {result.chunkResults.map((chunk) => (
                <article
                  key={chunk.chunkId}
                  style={{
                    border: '1px solid rgba(148,163,184,0.35)',
                    borderRadius: '14px',
                    padding: '1rem',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginBottom: '0.4rem',
                    }}
                  >
                    <strong>{chunk.title ?? chunk.chunkId}</strong>
                    {typeof chunk.hookScore === 'number' && (
                      <span className="tag">Hook {Math.round(chunk.hookScore * 100)}%</span>
                    )}
                  </div>
                  <p style={{ marginTop: 0, color: '#475569' }}>{chunk.summary}</p>
                  {chunk.themes && (
                    <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                      {chunk.themes.map((theme) => (
                        <span key={theme} className="pill">
                          {theme}
                        </span>
                      ))}
                    </div>
                  )}
                </article>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  )
}

function statusLabel(status: string): string {
  switch (status) {
    case 'completed':
    case 'failed':
    case 'running':
      return status
    default:
      return 'pending'
  }
}

function resolveCoreValue(id: string, payload: ProcessPayload): string {
  switch (id) {
    case 'topology':
      return (
        TOPOLOGY_OPTIONS.find((option) => option.value === payload.topologyMode)?.label ??
        payload.topologyMode
      )
    case 'api':
      return (
        API_POOL_OPTIONS.find((option) => option.value === payload.apiPoolMode)?.label ??
        payload.apiPoolMode
      )
    case 'genre':
      return payload.novelType
    case 'memory':
      return '输出目录：output/'
    case 'workflow':
      return payload.runCreativeFlow ? '已启用' : '未启用'
    case 'frankentexts':
      return payload.sampleText ? '含示例文本' : '等待 chunk'
    default:
      return 'config.yaml'
  }
}

function normalizeWorkflow(raw: WorkflowSummary | undefined | null): WorkflowSummary | null {
  if (!raw) return null
  const creation = (raw as any).creationFlow ?? (raw as any).creation_flow
  const optimization = (raw as any).optimizationFlow ?? (raw as any).optimization_flow
  const detection = (raw as any).detectionFlow ?? (raw as any).detection_flow
  return {
    creationFlow: creation ?? undefined,
    optimizationFlow: optimization ?? undefined,
    detectionFlow: detection ?? undefined,
  }
}

function normalizeStages(response: ProcessResponse): WorkflowStageSnapshot[] {
  if (response.workflowStages) {
    return Object.values(response.workflowStages)
  }
  const workflow = response.workflow as Record<string, any> | undefined
  if (workflow && Object.values(workflow).every((value) => value?.status)) {
    return Object.values(workflow)
  }
  return []
}

function extractToolSnippet(
  target: WorkflowTargetMeta,
  workflowSummary: WorkflowSummary | null,
  legacyCreative?: ProcessResponse['creative']
): string | undefined {
  const creation = workflowSummary?.creationFlow as Record<string, any> | undefined
  const optimization = workflowSummary?.optimizationFlow as Record<string, any> | undefined
  const detection = workflowSummary?.detectionFlow as Record<string, any> | undefined

  switch (target.id) {
    case 'opening': {
      const opening = creation?.opening as Record<string, any> | undefined
      return opening?.full_opening ?? legacyCreative?.openingScene
    }
    case 'titles': {
      const titles =
        (creation?.chapterTitles as Record<string, any> | undefined)?.titles ??
        legacyCreative?.titles
      return Array.isArray(titles) ? titles.slice(0, 2).join(' / ') : undefined
    }
    case 'commercial': {
      const commercial = creation?.commercial as Record<string, any> | undefined
      return (commercial?.summary as string | undefined) ?? legacyCreative?.commercialCopy
    }
    case 'platform': {
      const platform = creation?.platformAdaptation as Record<string, any> | undefined
      if (platform?.target_platform) {
        return `平台：${platform.target_platform} · 得分 ${platform.score ?? '--'}`
      }
      const notes = legacyCreative?.platformNotes
      return notes?.[0]
    }
    case 'emotion': {
      const emotion = optimization?.emotionDashboard as Record<string, any> | undefined
      if (emotion?.summary) return emotion.summary as string
      if (emotion?.pattern) return `Pattern：${emotion.pattern}`
      return legacyCreative?.emotionBeats?.join(' → ')
    }
    case 'hook':
      return (
        (creation?.hookDiagnostics as string | undefined) ?? legacyCreative?.hookDiagnosis ?? undefined
      )
    case 'characters': {
      const issues = optimization?.characterIssues as Record<string, any> | undefined
      const alerts = Array.isArray(issues?.issues) ? issues.issues : legacyCreative?.characterAlerts
      return alerts?.[0]
    }
    case 'foreshadowing': {
      const reminder = optimization?.foreshadowingReport as Record<string, any> | undefined
      const reminders =
        Array.isArray(reminder?.reminders) && reminder.reminders.length > 0
          ? reminder.reminders
          : legacyCreative?.foreshadowingReminders
      return reminders?.[0]
    }
    case 'ending': {
      const ending = optimization?.endingAnalysis as Record<string, any> | undefined
      const pitches =
        (Array.isArray(ending?.pitches) && ending.pitches.length > 0
          ? ending.pitches
          : legacyCreative?.endingPitches) ?? []
      return pitches[0]
    }
    case 'worldview': {
      const worldview = optimization?.worldviewConflicts as Record<string, any> | undefined
      const conflicts = Array.isArray(worldview?.conflicts) ? worldview.conflicts : undefined
      return conflicts?.[0]
    }
    case 'aiEvasion': {
      if (detection?.evasion_preview) {
        return `${detection.ai_likelihood ?? 'AI Likelihood --'} · ${detection.evasion_preview}`
      }
      return legacyCreative?.aiEvasionPlan
    }
    case 'villain':
      return '功能预研中，敬请期待'
    default:
      return undefined
  }
}
