import { mockProcessNovel } from './mockData'
import type { ProcessPayload, ProcessResponse } from '../types'

const API_BASE = import.meta.env.VITE_API_BASE ?? '/api'

export interface ApiConfig {
  topology_mode?: string
  output_dir?: string
  corpus_dir?: string
  api_mode?: string
  api_status?: string
  model?: {
    provider?: string
    model_name?: string
    api_key_configured?: boolean
    base_url?: string
  }
  api_pool?: {
    enabled?: boolean
    total_apis?: number
    enabled_apis?: number
    providers?: string[]
  }
}

export async function processNovel(payload: ProcessPayload): Promise<ProcessResponse> {
  const formData = new FormData()
  if (payload.file) {
    formData.append('file', payload.file, payload.file.name)
  }

  formData.append('novel_type', payload.novelType)
  formData.append('topology_mode', payload.topologyMode)
  formData.append('api_pool_mode', payload.apiPoolMode)
  formData.append('workflow_targets', JSON.stringify(payload.workflowTargets))
  formData.append('run_creative_flow', String(payload.runCreativeFlow))

  if (payload.sampleText) {
    formData.append('sample_text', payload.sampleText)
  }

  try {
    const response = await fetch(`${API_BASE}/process`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const message = await response.text()
      throw new Error(message || `处理失败，状态码 ${response.status}`)
    }

    return (await response.json()) as ProcessResponse
  } catch (error) {
    if (import.meta.env.DEV) {
      console.warn('API 请求失败，回退到 mock 数据。错误：', error)
      return mockProcessNovel(payload)
    }
    throw error
  }
}

export async function getConfig(): Promise<ApiConfig> {
  try {
    const response = await fetch(`${API_BASE}/config`)
    if (!response.ok) {
      throw new Error(`获取配置失败，状态码 ${response.status}`)
    }
    return (await response.json()) as ApiConfig
  } catch (error) {
    console.error('获取配置失败:', error)
    throw error
  }
}

export async function updateConfig(config: Partial<ApiConfig>): Promise<{ status: string; message: string }> {
  try {
    const response = await fetch(`${API_BASE}/config`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    })
    if (!response.ok) {
      const message = await response.text()
      throw new Error(message || `更新配置失败，状态码 ${response.status}`)
    }
    return (await response.json()) as { status: string; message: string }
  } catch (error) {
    console.error('更新配置失败:', error)
    throw error
  }
}

export interface ExportResponse {
  status: string
  export_dir: string
  exported_files: Record<string, string>
}

export async function exportData(
  outputDir: string,
  format: string = 'all',
  exportDir?: string
): Promise<ExportResponse> {
  const formData = new FormData()
  formData.append('output_dir', outputDir)
  formData.append('format', format)
  if (exportDir) {
    formData.append('export_dir', exportDir)
  }

  try {
    const response = await fetch(`${API_BASE}/export`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const message = await response.text()
      throw new Error(message || `导出失败，状态码 ${response.status}`)
    }

    return (await response.json()) as ExportResponse
  } catch (error) {
    console.error('导出失败:', error)
    throw error
  }
}

export interface ExportFormat {
  name: string
  description: string
  supports: string[]
}

export async function getExportFormats(): Promise<{ formats: ExportFormat[] }> {
  try {
    const response = await fetch(`${API_BASE}/export/formats`)
    if (!response.ok) {
      throw new Error(`获取导出格式失败，状态码 ${response.status}`)
    }
    return (await response.json()) as { formats: ExportFormat[] }
  } catch (error) {
    console.error('获取导出格式失败:', error)
    throw error
  }
}

export interface WorkflowProgress {
  workflow_id: string
  status: string
  progress: Record<string, unknown>
  current_stage?: string
  updated_at?: string
}

export interface WorkflowDetails {
  workflow_id: string
  status: string
  progress: Record<string, unknown>
  current_stage?: string
  stages?: Record<string, unknown>
  created_at?: string
  updated_at?: string
  chunk_count?: number
  error?: string
  workflow_summary?: Record<string, unknown>
  output_dir?: string
}

export async function getWorkflowProgress(workflowId: string): Promise<WorkflowProgress> {
  try {
    const response = await fetch(`${API_BASE}/workflows/${workflowId}/progress`)
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error(`工作流不存在: ${workflowId}`)
      }
      throw new Error(`获取工作流进度失败，状态码 ${response.status}`)
    }
    return (await response.json()) as WorkflowProgress
  } catch (error) {
    console.error('获取工作流进度失败:', error)
    throw error
  }
}

export async function getWorkflowDetails(workflowId: string): Promise<WorkflowDetails> {
  try {
    const response = await fetch(`${API_BASE}/workflows/${workflowId}/details`)
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error(`工作流不存在: ${workflowId}`)
      }
      throw new Error(`获取工作流详情失败，状态码 ${response.status}`)
    }
    return (await response.json()) as WorkflowDetails
  } catch (error) {
    console.error('获取工作流详情失败:', error)
    throw error
  }
}

export type WorkflowProgressCallback = (progress: WorkflowProgress) => void
export type WorkflowErrorCallback = (error: Error) => void
export type WorkflowCloseCallback = () => void

export interface WorkflowStreamOptions {
  onProgress?: WorkflowProgressCallback
  onError?: WorkflowErrorCallback
  onClose?: WorkflowCloseCallback
}

export class WorkflowStream {
  private eventSource: EventSource | null = null
  private workflowId: string
  private options: WorkflowStreamOptions

  constructor(workflowId: string, options: WorkflowStreamOptions = {}) {
    this.workflowId = workflowId
    this.options = options
  }

  connect(): void {
    if (this.eventSource) {
      this.close()
    }

    const url = `${API_BASE}/workflows/${this.workflowId}/stream`
    this.eventSource = new EventSource(url)

    this.eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        // 检查是否有错误
        if (data.error) {
          const error = new Error(data.error)
          if (this.options.onError) {
            this.options.onError(error)
          }
          this.close()
          return
        }

        // 处理进度更新
        const progress = data as WorkflowProgress
        if (this.options.onProgress) {
          this.options.onProgress(progress)
        }

        // 如果工作流已完成或失败，关闭连接
        if (progress.status === 'completed' || progress.status === 'failed') {
          if (this.options.onClose) {
            this.options.onClose()
          }
          this.close()
        }
      } catch (error) {
        console.error('解析SSE数据失败:', error)
        if (this.options.onError && error instanceof Error) {
          this.options.onError(error)
        }
      }
    }

    this.eventSource.addEventListener('close', () => {
      if (this.options.onClose) {
        this.options.onClose()
      }
      this.close()
    })

    this.eventSource.onerror = (error) => {
      console.error('SSE连接错误:', error)
      if (this.options.onError) {
        this.options.onError(new Error('SSE连接失败'))
      }
      this.close()
    }
  }

  close(): void {
    if (this.eventSource) {
      this.eventSource.close()
      this.eventSource = null
    }
  }

  isConnected(): boolean {
    return this.eventSource !== null && this.eventSource.readyState === EventSource.OPEN
  }
}

