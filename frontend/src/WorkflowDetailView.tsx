import { useEffect, useState } from 'react'
import { getWorkflowDetails, type WorkflowDetails } from './services/api'
import type { WorkflowStageSnapshot } from './types'

interface WorkflowDetailViewProps {
  workflowId: string
  onClose: () => void
}

export default function WorkflowDetailView({ workflowId, onClose }: WorkflowDetailViewProps) {
  const [details, setDetails] = useState<WorkflowDetails | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadDetails()
  }, [workflowId])

  const loadDetails = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getWorkflowDetails(workflowId)
      setDetails(data)
    } catch (err) {
      const message = err instanceof Error ? err.message : '加载工作流详情失败'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return '未知'
    try {
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    } catch {
      return dateString
    }
  }

  const formatDuration = (ms?: number) => {
    if (!ms) return '未知'
    if (ms < 1000) return `${ms}ms`
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
    const minutes = Math.floor(ms / 60000)
    const seconds = Math.floor((ms % 60000) / 1000)
    return `${minutes}m ${seconds}s`
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'var(--color-success)'
      case 'failed':
        return 'var(--color-error)'
      case 'running':
      case 'in_progress':
        return 'var(--color-warning)'
      case 'pending':
        return 'var(--color-text-tertiary)'
      default:
        return 'var(--color-text-secondary)'
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'completed':
        return '已完成'
      case 'failed':
        return '失败'
      case 'running':
      case 'in_progress':
        return '进行中'
      case 'pending':
        return '等待中'
      default:
        return status
    }
  }

  // 解析阶段数据
  const parseStages = (stages?: Record<string, unknown>): WorkflowStageSnapshot[] => {
    if (!stages || typeof stages !== 'object') return []
    
    const stageArray: WorkflowStageSnapshot[] = []
    for (const [id, stageData] of Object.entries(stages)) {
      if (typeof stageData === 'object' && stageData !== null) {
        const stage = stageData as any
        stageArray.push({
          id,
          label: stage.label || id,
          status: (stage.status || 'pending') as 'pending' | 'running' | 'completed' | 'failed',
          detail: stage.detail,
          durationMs: stage.durationMs
        })
      }
    }
    return stageArray
  }

  const stages = details ? parseStages(details.stages as Record<string, unknown>) : []

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        padding: '1rem'
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: 'var(--color-bg-primary)',
          borderRadius: 'var(--radius-lg)',
          padding: '1.5rem',
          maxWidth: '800px',
          width: '100%',
          maxHeight: '90vh',
          overflow: 'auto',
          boxShadow: 'var(--shadow-xl)',
          border: '1px solid var(--color-border)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ margin: 0, fontSize: '1.5rem', color: 'var(--color-text-primary)' }}>
            工作流详情
          </h2>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '1.5rem',
              cursor: 'pointer',
              color: 'var(--color-text-secondary)',
              padding: '0.25rem 0.5rem',
              borderRadius: 'var(--radius-sm)',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'var(--color-bg-secondary)'
              e.currentTarget.style.color = 'var(--color-text-primary)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'none'
              e.currentTarget.style.color = 'var(--color-text-secondary)'
            }}
          >
            ×
          </button>
        </div>

        {loading && (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-text-secondary)' }}>
            加载中...
          </div>
        )}

        {error && (
          <div style={{
            padding: '1rem',
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: 'var(--radius-md)',
            color: 'var(--color-error)',
            marginBottom: '1rem'
          }}>
            {error}
          </div>
        )}

        {details && !loading && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* 基本信息 */}
            <div style={{
              padding: '1rem',
              background: 'var(--color-bg-secondary)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--color-border)'
            }}>
              <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.125rem', color: 'var(--color-text-primary)' }}>
                基本信息
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem' }}>
                <div>
                  <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>
                    工作流ID
                  </div>
                  <div style={{ fontSize: '0.875rem', color: 'var(--color-text-primary)', fontFamily: 'monospace' }}>
                    {details.workflow_id}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>
                    状态
                  </div>
                  <span
                    style={{
                      display: 'inline-block',
                      padding: '0.25rem 0.5rem',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: '0.875rem',
                      background: `${getStatusColor(details.status)}20`,
                      color: getStatusColor(details.status),
                      border: `1px solid ${getStatusColor(details.status)}40`
                    }}
                  >
                    {getStatusLabel(details.status)}
                  </span>
                </div>
                {details.current_stage && (
                  <div>
                    <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>
                      当前阶段
                    </div>
                    <div style={{ fontSize: '0.875rem', color: 'var(--color-text-primary)' }}>
                      {details.current_stage}
                    </div>
                  </div>
                )}
                {details.chunk_count !== undefined && (
                  <div>
                    <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>
                      文本块数量
                    </div>
                    <div style={{ fontSize: '0.875rem', color: 'var(--color-text-primary)' }}>
                      {details.chunk_count}
                    </div>
                  </div>
                )}
                <div>
                  <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>
                    创建时间
                  </div>
                  <div style={{ fontSize: '0.875rem', color: 'var(--color-text-primary)' }}>
                    {formatDate(details.created_at)}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginBottom: '0.25rem' }}>
                    更新时间
                  </div>
                  <div style={{ fontSize: '0.875rem', color: 'var(--color-text-primary)' }}>
                    {formatDate(details.updated_at)}
                  </div>
                </div>
              </div>
            </div>

            {/* 错误信息 */}
            {details.error && (
              <div style={{
                padding: '1rem',
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--color-error)'
              }}>
                <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1.125rem' }}>错误信息</h3>
                <pre style={{
                  margin: 0,
                  fontSize: '0.875rem',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word'
                }}>
                  {details.error}
                </pre>
              </div>
            )}

            {/* 工作流阶段 */}
            {stages.length > 0 && (
              <div>
                <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.125rem', color: 'var(--color-text-primary)' }}>
                  工作流阶段
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {stages.map((stage) => (
                    <div
                      key={stage.id}
                      className={`workflow-stage ${stage.status}`}
                      style={{
                        padding: '1rem',
                        borderRadius: 'var(--radius-md)',
                        border: '1px solid var(--color-border)'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                        <div>
                          <div style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: '0.25rem' }}>
                            {stage.label}
                          </div>
                          {stage.detail && (
                            <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginTop: '0.25rem' }}>
                              {stage.detail}
                            </div>
                          )}
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.25rem' }}>
                          <span
                            style={{
                              display: 'inline-block',
                              padding: '0.25rem 0.5rem',
                              borderRadius: 'var(--radius-sm)',
                              fontSize: '0.75rem',
                              background: `${getStatusColor(stage.status)}20`,
                              color: getStatusColor(stage.status),
                              border: `1px solid ${getStatusColor(stage.status)}40`
                            }}
                          >
                            {getStatusLabel(stage.status)}
                          </span>
                          {stage.durationMs && (
                            <span style={{ fontSize: '0.75rem', color: 'var(--color-text-tertiary)' }}>
                              {formatDuration(stage.durationMs)}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 进度信息 */}
            {details.progress && Object.keys(details.progress).length > 0 && (
              <div style={{
                padding: '1rem',
                background: 'var(--color-bg-secondary)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--color-border)'
              }}>
                <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.125rem', color: 'var(--color-text-primary)' }}>
                  进度详情
                </h3>
                <pre style={{
                  margin: 0,
                  fontSize: '0.875rem',
                  color: 'var(--color-text-secondary)',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  maxHeight: '200px',
                  overflow: 'auto'
                }}>
                  {JSON.stringify(details.progress, null, 2)}
                </pre>
              </div>
            )}

            {/* 输出目录 */}
            {details.output_dir && (
              <div style={{
                padding: '1rem',
                background: 'var(--color-bg-secondary)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--color-border)'
              }}>
                <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1.125rem', color: 'var(--color-text-primary)' }}>
                  输出目录
                </h3>
                <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', fontFamily: 'monospace' }}>
                  {details.output_dir}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

