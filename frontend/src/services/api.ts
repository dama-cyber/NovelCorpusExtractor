import { mockProcessNovel } from './mockData'
import type { ProcessPayload, ProcessResponse } from '../types'

const API_BASE = import.meta.env.VITE_API_BASE ?? '/api'

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

