import { useEffect, useMemo, useState } from 'react'
import type { ChangeEvent, FormEvent } from 'react'
import {
  AGENT_MODULES,
  API_POOL_OPTIONS,
  CORE_SERVICES,
  NOVEL_TYPES,
  TOPOLOGY_OPTIONS,
  WORKFLOW_TARGETS,
} from './constants'
import { processNovel, getConfig, exportData, getExportFormats, getWorkflowProgress, WorkflowStream, type ApiConfig, type ExportFormat, type WorkflowProgress } from './services/api'
import WorkflowDetailView from './WorkflowDetailView'
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
  const [apiConfig, setApiConfig] = useState<ApiConfig | null>(null)
  const [showApiConfig, setShowApiConfig] = useState(false)
  const [apiConfigLoading, setApiConfigLoading] = useState(false)
  const [exportFormats, setExportFormats] = useState<ExportFormat[]>([])
  const [exporting, setExporting] = useState(false)
  const [exportFormat, setExportFormat] = useState<string>('all')
  const [exportMessage, setExportMessage] = useState<string | null>(null)
  const [expandedChunks, setExpandedChunks] = useState<Set<string>>(new Set())
  const [expandedMemories, setExpandedMemories] = useState<Set<string>>(new Set())
  const [currentWorkflowId, setCurrentWorkflowId] = useState<string | null>(null)
  const [workflowProgress, setWorkflowProgress] = useState<WorkflowProgress | null>(null)
  const [workflowStream, setWorkflowStream] = useState<WorkflowStream | null>(null)
  const [showWorkflowDetail, setShowWorkflowDetail] = useState(false)

  // 加载 API 配置和导出格式
  useEffect(() => {
    loadApiConfig()
    loadExportFormats()
  }, [])

  // 清理SSE连接
  useEffect(() => {
    return () => {
      if (workflowStream) {
        workflowStream.close()
      }
    }
  }, [workflowStream])

  const loadExportFormats = async () => {
    try {
      const response = await getExportFormats()
      setExportFormats(response.formats)
    } catch (err) {
      console.error('加载导出格式失败:', err)
    }
  }

  const loadApiConfig = async () => {
    setApiConfigLoading(true)
    try {
      const config = await getConfig()
      setApiConfig(config)
    } catch (err) {
      console.error('加载 API 配置失败:', err)
    } finally {
      setApiConfigLoading(false)
    }
  }

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

  // 开始工作流进度SSE流
  const startStreaming = (workflowId: string) => {
    // 关闭之前的流
    if (workflowStream) {
      workflowStream.close()
    }

    // 创建新的SSE流
    const stream = new WorkflowStream(workflowId, {
      onProgress: (progress) => {
        setWorkflowProgress(progress)
        
        // 如果工作流已完成或失败，停止处理状态
        if (progress.status === 'completed' || progress.status === 'failed') {
          setProcessing(false)
          
          // 如果失败，显示错误信息
          if (progress.status === 'failed') {
            const errorMsg = (progress.progress as any)?.error || '工作流处理失败'
            setError(errorMsg)
          }
        }
      },
      onError: (error) => {
        console.error('SSE流错误:', error)
        setError(error.message)
        setProcessing(false)
      },
      onClose: () => {
        // 流关闭时的清理工作
        setProcessing(false)
      }
    })

    stream.connect()
    setWorkflowStream(stream)
  }

  // 停止工作流进度SSE流
  const stopStreaming = () => {
    if (workflowStream) {
      workflowStream.close()
      setWorkflowStream(null)
    }
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
    setWorkflowProgress(null)
    setCurrentWorkflowId(null)
    stopStreaming() // 停止之前的流

    let response: ProcessResponse | null = null
    try {
      response = await processNovel(payload)
      setResult(response)
      setWorkflowStages(normalizeStages(response))
      setWorkflowSummary(normalizeWorkflow(response.workflow))

      // 如果响应包含工作流ID，开始SSE流
      if (response.workflowId) {
        setCurrentWorkflowId(response.workflowId)
        startStreaming(response.workflowId)
        // 如果开始流，processing状态会保持为true直到工作流完成
      } else {
        // 如果响应已经包含完整结果（没有workflowId），则设置为false
        setProcessing(false)
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : '处理失败，请稍后再试'
      setError(message)
      stopStreaming()
      setProcessing(false)
    }
  }

  const handleExport = async () => {
    if (!result) return

    setExporting(true)
    setExportMessage(null)

    try {
      // 从结果中获取输出目录，如果没有则使用默认值
      const outputDir = result.outputDir || apiConfig?.output_dir || 'output'
      const response = await exportData(outputDir, exportFormat)
      
      setExportMessage(`✅ 导出成功！文件保存在: ${response.export_dir}\n${Object.entries(response.exported_files).map(([fmt, path]) => `${fmt.toUpperCase()}: ${path}`).join('\n')}`)
    } catch (err) {
      const message = err instanceof Error ? err.message : '导出失败，请稍后再试'
      setExportMessage(`❌ ${message}`)
    } finally {
      setExporting(false)
    }
  }

  return (
    <div className="app-shell">
      <header style={{ marginBottom: '2.5rem', textAlign: 'center' }}>
        <p className="pill" style={{ marginBottom: '1rem' }}>NovelCorpusExtractor · Web 控制台</p>
        <h1 style={{ marginBottom: '0.75rem', background: 'linear-gradient(135deg, var(--color-primary), var(--color-secondary))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
          一键触发多智能体小说语料提取
        </h1>
        <p style={{ color: 'var(--color-text-secondary)', maxWidth: '680px', margin: '0 auto', fontSize: '1rem', lineHeight: '1.6' }}>
          上传原始文本、选择小说类型与拓扑模式，即可运行 Reader / Analyst / Archivist / Creative
          Workflow。前端会实时展示工作流进度、记忆体产物以及 10 大创作工具的优化结果。
        </p>
        <button
          onClick={() => setShowApiConfig(!showApiConfig)}
          style={{
            marginTop: '1rem',
            padding: '0.5rem 1rem',
            background: 'var(--color-bg-secondary)',
            border: '1px solid var(--color-border)',
            borderRadius: '0.5rem',
            cursor: 'pointer',
            color: 'var(--color-text-primary)',
          }}
        >
          {showApiConfig ? '隐藏' : '显示'} API 配置
        </button>
      </header>

      {showApiConfig && (
        <section className="card" style={{ marginBottom: '1.5rem' }}>
          <h3>API 配置</h3>
          {apiConfigLoading ? (
            <p>加载中...</p>
          ) : apiConfig ? (
            <div className="grid" style={{ gap: '1rem' }}>
              <div>
                <p className="section-title">API 模式</p>
                <p style={{ margin: 0, color: 'var(--color-text-secondary)' }}>
                  {apiConfig.api_mode === 'api_only' ? '✅ 仅 API 模式（不支持本地模型）' : apiConfig.api_mode}
                </p>
              </div>
              <div>
                <p className="section-title">API 状态</p>
                <p style={{ margin: 0, color: 'var(--color-text-secondary)' }}>
                  {apiConfig.api_status === 'not_configured' ? (
                    <span style={{ color: 'var(--color-error)' }}>❌ 未配置 API 密钥</span>
                  ) : (
                    <span style={{ color: 'var(--color-success)' }}>✅ {apiConfig.api_status}</span>
                  )}
                </p>
              </div>
              {apiConfig.model && (
                <div>
                  <p className="section-title">模型配置</p>
                  <div style={{ display: 'grid', gap: '0.5rem' }}>
                    <p style={{ margin: 0, color: 'var(--color-text-secondary)' }}>
                      提供商: {apiConfig.model.provider || '未设置'}
                    </p>
                    <p style={{ margin: 0, color: 'var(--color-text-secondary)' }}>
                      模型: {apiConfig.model.model_name || '未设置'}
                    </p>
                    <p style={{ margin: 0, color: 'var(--color-text-secondary)' }}>
                      API 密钥: {apiConfig.model.api_key_configured ? '✅ 已配置' : '❌ 未配置'}
                    </p>
                    {apiConfig.model.base_url && (
                      <p style={{ margin: 0, color: 'var(--color-text-secondary)' }}>
                        自定义地址: {apiConfig.model.base_url}
                      </p>
                    )}
                  </div>
                </div>
              )}
              {apiConfig.api_pool && apiConfig.api_pool.enabled && (
                <div>
                  <p className="section-title">API 池配置</p>
                  <div style={{ display: 'grid', gap: '0.5rem' }}>
                    <p style={{ margin: 0, color: 'var(--color-text-secondary)' }}>
                      总 API 数: {apiConfig.api_pool.total_apis}
                    </p>
                    <p style={{ margin: 0, color: 'var(--color-text-secondary)' }}>
                      已启用: {apiConfig.api_pool.enabled_apis}
                    </p>
                    {apiConfig.api_pool.providers && apiConfig.api_pool.providers.length > 0 && (
                      <p style={{ margin: 0, color: 'var(--color-text-secondary)' }}>
                        提供商: {apiConfig.api_pool.providers.join(', ')}
                      </p>
                    )}
                  </div>
                </div>
              )}
              <div>
                <p className="section-title">配置说明</p>
                <p style={{ margin: 0, color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>
                  ⚠️ API 密钥需要在服务器端的 <code>config.yaml</code> 文件中配置，或通过环境变量设置。
                  前端无法直接修改 API 密钥，这是出于安全考虑。
                </p>
                <p style={{ margin: '0.5rem 0 0', color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>
                  支持的 API 提供商：OpenAI、Gemini、DeepSeek、Anthropic Claude、Moonshot、零一万物、通义千问、文心一言、智谱AI
                </p>
              </div>
              <button
                onClick={loadApiConfig}
                style={{
                  padding: '0.5rem 1rem',
                  background: 'var(--color-primary)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '0.5rem',
                  cursor: 'pointer',
                }}
              >
                刷新配置
              </button>
            </div>
          ) : (
            <p style={{ color: 'var(--color-text-secondary)' }}>无法加载配置</p>
          )}
        </section>
      )}

      <div className="grid two" style={{ marginBottom: '1.5rem' }}>
        <section className="card">
          <h3>输入配置</h3>
          <form className="grid" style={{ gap: '1rem' }} onSubmit={handleSubmit}>
            <label className="grid">
              <span>小说文件</span>
              <input
                type="file"
                accept=".txt,.md,.json"
                onChange={handleFileChange}
              />
              {fileName && <small>{fileName}</small>}
            </label>

            <label className="grid">
              <span>示例文本（可选）</span>
              <textarea
                rows={4}
                placeholder="可粘贴1-2段文本，帮助风格/题材检测"
                value={payload.sampleText ?? ''}
                onChange={(event) =>
                  setPayload((prev) => ({ ...prev, sampleText: event.target.value }))
                }
              />
            </label>

            <div className="grid two">
              <label className="grid">
                <span>小说类型</span>
                <select
                  value={payload.novelType}
                  onChange={(event) =>
                    setPayload((prev) => ({ ...prev, novelType: event.target.value }))
                  }
                >
                  {NOVEL_TYPES.map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
              </label>

              <label className="grid">
                <span>拓扑模式</span>
                <select
                  value={payload.topologyMode}
                  onChange={(event) =>
                    setPayload((prev) => ({ ...prev, topologyMode: event.target.value as any }))
                  }
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
              <span>API 池</span>
              <select
                value={payload.apiPoolMode}
                onChange={(event) =>
                  setPayload((prev) => ({ ...prev, apiPoolMode: event.target.value as any }))
                }
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
                {WORKFLOW_TARGETS.map((target) => {
                  const isSelected = payload.workflowTargets.includes(target.id)
                  return (
                    <label
                      key={target.id}
                      className={`tool-select-card ${isSelected ? 'selected' : ''} ${target.disabled ? 'disabled' : ''}`}
                    >
                      <input
                        type="checkbox"
                        checked={isSelected}
                        disabled={target.disabled}
                        onChange={() => handleTargetToggle(target.id, target.disabled)}
                      />
                      <span style={{ display: 'inline-flex', flexDirection: 'column', flex: 1 }}>
                        <span style={{ fontWeight: 500 }}>{target.label}</span>
                        <small style={{ color: 'var(--color-text-tertiary)', fontSize: '0.75rem', marginTop: '0.125rem' }}>
                          {target.module}
                        </small>
                      </span>
                    </label>
                  )
                })}
              </div>
            </div>

            <label
              className="tool-select-card"
              style={{
                cursor: 'pointer',
                background: payload.runCreativeFlow ? 'rgba(99, 102, 241, 0.08)' : 'var(--color-bg-secondary)',
                borderColor: payload.runCreativeFlow ? 'var(--color-primary)' : 'var(--color-border)',
              }}
            >
              <input
                type="checkbox"
                checked={payload.runCreativeFlow}
                onChange={(event) =>
                  setPayload((prev) => ({ ...prev, runCreativeFlow: event.target.checked }))
                }
              />
              <span style={{ fontWeight: 500 }}>启动 10 阶段创作增强工作流</span>
            </label>

            <button className="primary-button" type="submit" disabled={processing} style={{ width: '100%', marginTop: '0.5rem' }}>
              {processing ? (
                <>
                  <span style={{ display: 'inline-block', marginRight: '0.5rem' }}>⏳</span>
                  处理中...
                </>
              ) : (
                '开始提取'
              )}
            </button>
            {error && (
              <div
                style={{
                  marginTop: '1rem',
                  padding: '0.75rem',
                  background: 'rgba(239, 68, 68, 0.1)',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  borderRadius: '0.5rem',
                  color: 'var(--color-error)',
                }}
              >
                <strong style={{ display: 'block', marginBottom: '0.25rem' }}>❌ 错误</strong>
                <p style={{ margin: 0, fontSize: '0.875rem' }}>{error}</p>
                <button
                  onClick={() => setError(null)}
                  style={{
                    marginTop: '0.5rem',
                    padding: '0.25rem 0.5rem',
                    background: 'rgba(239, 68, 68, 0.2)',
                    border: '1px solid rgba(239, 68, 68, 0.3)',
                    borderRadius: '0.25rem',
                    cursor: 'pointer',
                    color: 'var(--color-error)',
                    fontSize: '0.75rem',
                  }}
                >
                  关闭
                </button>
              </div>
            )}
          </form>
        </section>

        <section className="card">
          <h3>工作流进度</h3>
          {processing && (
            <div className="empty-state" style={{ padding: '1rem' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ marginBottom: '1rem' }}>
                  <div style={{ 
                    display: 'inline-block',
                    width: '40px',
                    height: '40px',
                    border: '4px solid var(--color-border)',
                    borderTopColor: 'var(--color-primary)',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite',
                  }} />
                  <style>{`
                    @keyframes spin {
                      to { transform: rotate(360deg); }
                    }
                  `}</style>
                </div>
                <p style={{ margin: 0, color: 'var(--color-text-secondary)' }}>正在处理中，请稍候...</p>
                <p style={{ margin: '0.5rem 0 0', fontSize: '0.875rem', color: 'var(--color-text-tertiary)' }}>
                  这可能需要几分钟时间，取决于文件大小和选择的工具数量
                </p>
                {workflowProgress && (
                  <div style={{ marginTop: '1rem', padding: '0.75rem', background: 'var(--color-bg-secondary)', borderRadius: '0.5rem', textAlign: 'left' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                      <span style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>工作流ID:</span>
                      <code style={{ fontSize: '0.75rem', color: 'var(--color-text-tertiary)' }}>{workflowProgress.workflow_id.slice(0, 8)}...</code>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                      <span style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>状态:</span>
                      <span className={`tag tag--${workflowProgress.status}`} style={{ fontSize: '0.75rem' }}>
                        {workflowProgress.status === 'in_progress' ? '进行中' : 
                         workflowProgress.status === 'completed' ? '已完成' : 
                         workflowProgress.status === 'failed' ? '失败' : workflowProgress.status}
                      </span>
                    </div>
                    {workflowProgress.current_stage && (
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                        <span style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>当前阶段:</span>
                        <span style={{ fontSize: '0.875rem', color: 'var(--color-text-primary)' }}>{workflowProgress.current_stage}</span>
                      </div>
                    )}
                    {workflowProgress.progress && typeof workflowProgress.progress === 'object' && 'percentage' in workflowProgress.progress && (
                      <div style={{ marginTop: '0.75rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                          <span style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>进度:</span>
                          <span style={{ fontSize: '0.875rem', color: 'var(--color-text-primary)' }}>
                            {Math.round((workflowProgress.progress as any).percentage || 0)}%
                          </span>
                        </div>
                        <div style={{ 
                          width: '100%', 
                          height: '6px', 
                          background: 'var(--color-bg-tertiary)', 
                          borderRadius: '3px',
                          overflow: 'hidden'
                        }}>
                          <div style={{ 
                            width: `${(workflowProgress.progress as any).percentage || 0}%`, 
                            height: '100%', 
                            background: 'var(--color-primary)',
                            transition: 'width 0.3s ease'
                          }} />
                        </div>
                      </div>
                    )}
                    {workflowProgress.updated_at && (
                      <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: 'var(--color-text-tertiary)' }}>
                        最后更新: {new Date(workflowProgress.updated_at).toLocaleTimeString()}
                      </div>
                    )}
                    {currentWorkflowId && (
                      <button
                        onClick={() => setShowWorkflowDetail(true)}
                        style={{
                          marginTop: '0.75rem',
                          width: '100%',
                          padding: '0.5rem',
                          background: 'var(--color-primary)',
                          color: 'white',
                          border: 'none',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: '0.875rem',
                          cursor: 'pointer',
                          transition: 'all 0.2s ease'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.opacity = '0.9'
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.opacity = '1'
                        }}
                      >
                        查看详情
                      </button>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
          {!processing && workflowStages.length === 0 && (
            <div className="empty-state">
              <p>提交任务后将展示各 Agent 状态。</p>
            </div>
          )}
          <div className="grid" style={{ gap: '0.75rem' }}>
            {workflowStages.map((stage) => (
              <article
                key={stage.id}
                className={`workflow-stage ${stage.status}`}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem' }}>
                  <strong style={{ flex: 1 }}>{stage.label}</strong>
                  <span className={`tag tag--${stage.status}`}>{stage.status}</span>
                </div>
                {stage.detail && (
                  <p style={{ margin: '0.75rem 0 0', color: 'var(--color-text-secondary)', fontSize: '0.875rem', lineHeight: '1.5' }}>
                    {stage.detail}
                  </p>
                )}
              </article>
            ))}
          </div>
          <hr style={{ margin: '1.5rem 0', borderColor: 'rgba(148,163,184,0.3)' }} />
          <h4 style={{ margin: '0 0 0.6rem' }}>已启用的创作工具</h4>
          {creativeToolsEnabled ? (
            <ul style={{ margin: 0, paddingLeft: 0, listStyle: 'none', color: 'var(--color-text-secondary)' }}>
              {selectedTargetLabels.map((label) => (
                <li key={label} style={{ padding: '0.5rem 0', paddingLeft: '1.5rem', position: 'relative' }}>
                  <span style={{ position: 'absolute', left: 0, color: 'var(--color-primary)' }}>✓</span>
                  {label}
                </li>
              ))}
            </ul>
          ) : (
            <p style={{ color: 'var(--color-text-tertiary)', margin: 0 }}>未选择任何创作工具。</p>
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
        <p style={{ marginTop: '-0.2rem', color: 'var(--color-text-secondary)', fontSize: '0.9375rem' }}>
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
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{ margin: 0 }}>提取结果总览</h3>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <select
                  value={exportFormat}
                  onChange={(e) => setExportFormat(e.target.value)}
                  disabled={exporting}
                  style={{
                    padding: '0.5rem',
                    background: 'var(--color-bg-secondary)',
                    border: '1px solid var(--color-border)',
                    borderRadius: '0.5rem',
                    color: 'var(--color-text-primary)',
                    cursor: exporting ? 'not-allowed' : 'pointer',
                  }}
                >
                  {exportFormats.map((fmt) => (
                    <option key={fmt.name} value={fmt.name}>
                      {fmt.name.toUpperCase()} - {fmt.description}
                    </option>
                  ))}
                </select>
                <button
                  onClick={handleExport}
                  disabled={exporting}
                  style={{
                    padding: '0.5rem 1rem',
                    background: exporting ? 'var(--color-bg-secondary)' : 'var(--color-primary)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '0.5rem',
                    cursor: exporting ? 'not-allowed' : 'pointer',
                    opacity: exporting ? 0.6 : 1,
                  }}
                >
                  {exporting ? '导出中...' : '导出数据'}
                </button>
              </div>
            </div>
            {exportMessage && (
              <div
                style={{
                  padding: '0.75rem',
                  marginBottom: '1rem',
                  background: exportMessage.startsWith('✅') ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                  border: `1px solid ${exportMessage.startsWith('✅') ? 'rgba(34, 197, 94, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                  borderRadius: '0.5rem',
                  whiteSpace: 'pre-wrap',
                  fontSize: '0.875rem',
                  color: 'var(--color-text-primary)',
                }}
              >
                {exportMessage}
              </div>
            )}
            <div className="grid two">
              <div>
                <p className="section-title">文本块</p>
                <p style={{ margin: 0, fontSize: '2.5rem', fontWeight: 700, background: 'linear-gradient(135deg, var(--color-primary), var(--color-secondary))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
                  {result.chunkResults.length}
                </p>
                <small>chunk_results</small>
              </div>
              <div>
                <p className="section-title">最新时间戳</p>
                <p style={{ margin: 0, fontSize: '1.125rem', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                  {result.emittedAt
                    ? new Date(result.emittedAt).toLocaleString()
                    : '来自 mock 数据'}
                </p>
              </div>
            </div>
            {result.outline && (
              <details style={{ marginTop: '1rem' }}>
                <summary style={{ cursor: 'pointer', padding: '0.5rem', background: 'var(--color-bg-secondary)', borderRadius: '0.25rem', marginBottom: '0.5rem' }}>
                  <strong>大纲预览</strong>
                </summary>
                <pre style={{ whiteSpace: 'pre-wrap', padding: '1rem', background: 'var(--color-bg-secondary)', borderRadius: '0.5rem', overflow: 'auto', maxHeight: '400px' }}>
                  {result.outline}
                </pre>
              </details>
            )}
          </section>

          {result.memories && (
            <section className="card" style={{ marginBottom: '1.5rem' }}>
              <h3>记忆体预览</h3>
              <div className="grid two">
                {result.memories.map((memory) => {
                  const isExpanded = expandedMemories.has(memory.id)
                  return (
                    <article key={memory.id} className="memory-card">
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                        <strong>{memory.title}</strong>
                        <button
                          onClick={() => {
                            const newSet = new Set(expandedMemories)
                            if (isExpanded) {
                              newSet.delete(memory.id)
                            } else {
                              newSet.add(memory.id)
                            }
                            setExpandedMemories(newSet)
                          }}
                          style={{
                            padding: '0.25rem 0.5rem',
                            background: 'var(--color-bg-secondary)',
                            border: '1px solid var(--color-border)',
                            borderRadius: '0.25rem',
                            cursor: 'pointer',
                            color: 'var(--color-text-primary)',
                            fontSize: '0.75rem',
                          }}
                        >
                          {isExpanded ? '收起' : '展开'}
                        </button>
                      </div>
                      {isExpanded && (
                        <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
                          {memory.entries.map((entry, index) => (
                            <li key={`${memory.id}-${index}`} style={{ marginBottom: '0.5rem' }}>
                              <code style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>{entry}</code>
                            </li>
                          ))}
                        </ul>
                      )}
                      {!isExpanded && memory.entries.length > 0 && (
                        <p style={{ margin: 0, color: 'var(--color-text-tertiary)', fontSize: '0.875rem' }}>
                          {memory.entries.length} 个条目
                        </p>
                      )}
                    </article>
                  )
                })}
              </div>
            </section>
          )}

          <section className="card" style={{ marginBottom: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{ margin: 0 }}>Chunk 详情</h3>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button
                  onClick={() => {
                    if (expandedChunks.size === result.chunkResults.length) {
                      setExpandedChunks(new Set())
                    } else {
                      setExpandedChunks(new Set(result.chunkResults.map((c) => c.chunkId)))
                    }
                  }}
                  style={{
                    padding: '0.5rem 1rem',
                    background: 'var(--color-bg-secondary)',
                    border: '1px solid var(--color-border)',
                    borderRadius: '0.5rem',
                    cursor: 'pointer',
                    color: 'var(--color-text-primary)',
                    fontSize: '0.875rem',
                  }}
                >
                  {expandedChunks.size === result.chunkResults.length ? '全部收起' : '全部展开'}
                </button>
              </div>
            </div>
            <div className="grid">
              {result.chunkResults.map((chunk) => {
                const isExpanded = expandedChunks.has(chunk.chunkId)
                return (
                  <article key={chunk.chunkId} className="chunk-card">
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: '0.75rem',
                        gap: '1rem',
                      }}
                    >
                      <strong style={{ flex: 1 }}>{chunk.title ?? chunk.chunkId}</strong>
                      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                        {typeof chunk.hookScore === 'number' && (
                          <span className="tag" style={{ background: 'rgba(99, 102, 241, 0.1)', color: 'var(--color-primary)', borderColor: 'rgba(99, 102, 241, 0.3)' }}>
                            Hook {Math.round(chunk.hookScore * 100)}%
                          </span>
                        )}
                        <button
                          onClick={() => {
                            const newSet = new Set(expandedChunks)
                            if (isExpanded) {
                              newSet.delete(chunk.chunkId)
                            } else {
                              newSet.add(chunk.chunkId)
                            }
                            setExpandedChunks(newSet)
                          }}
                          style={{
                            padding: '0.25rem 0.5rem',
                            background: 'var(--color-bg-secondary)',
                            border: '1px solid var(--color-border)',
                            borderRadius: '0.25rem',
                            cursor: 'pointer',
                            color: 'var(--color-text-primary)',
                            fontSize: '0.75rem',
                          }}
                        >
                          {isExpanded ? '收起' : '展开'}
                        </button>
                      </div>
                    </div>
                    {isExpanded ? (
                      <>
                        <p style={{ marginTop: 0, marginBottom: '0.75rem', color: 'var(--color-text-secondary)', lineHeight: '1.6' }}>{chunk.summary}</p>
                        {chunk.themes && chunk.themes.length > 0 && (
                          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.5rem' }}>
                            {chunk.themes.map((theme) => (
                              <span key={theme} className="pill">
                                {theme}
                              </span>
                            ))}
                          </div>
                        )}
                        {chunk.tokens && (
                          <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--color-text-tertiary)' }}>
                            字数: {chunk.tokens} tokens
                          </p>
                        )}
                      </>
                    ) : (
                      <p style={{ margin: 0, color: 'var(--color-text-tertiary)', fontSize: '0.875rem', lineHeight: '1.4' }}>
                        {chunk.summary.length > 100 ? `${chunk.summary.substring(0, 100)}...` : chunk.summary}
                      </p>
                    )}
                  </article>
                )
              })}
            </div>
          </section>
        </>
      )}
      {showWorkflowDetail && currentWorkflowId && (
        <WorkflowDetailView
          workflowId={currentWorkflowId}
          onClose={() => setShowWorkflowDetail(false)}
        />
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
