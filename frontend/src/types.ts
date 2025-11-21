export type TopologyMode = 'auto' | 'linear' | 'triangular' | 'swarm'
export type ApiPoolMode = 'auto' | 'single' | 'triple' | 'swarm'

export interface ProcessPayload {
  file?: File | null
  novelType: string
  topologyMode: TopologyMode
  apiPoolMode: ApiPoolMode
  sampleText?: string
  workflowTargets: string[]
  runCreativeFlow: boolean
}

export interface ChunkResult {
  chunkId: string
  title?: string
  summary: string
  tokens?: number
  themes?: string[]
  hookScore?: number
}

export interface MemoryBlock {
  id: string
  title: string
  entries: string[]
}

export type WorkflowStatus = 'pending' | 'running' | 'completed' | 'failed'

export interface WorkflowStageSnapshot {
  id: string
  label: string
  status: WorkflowStatus
  detail?: string
  durationMs?: number
}

export interface WorkflowSummary {
  creationFlow?: Record<string, unknown>
  optimizationFlow?: Record<string, unknown>
  detectionFlow?: Record<string, unknown>
}

export interface CreativeOutputs {
  openingScene?: string
  titles?: string[]
  commercialCopy?: string
  platformNotes?: string[]
  emotionBeats?: string[]
  hookDiagnosis?: string
  characterAlerts?: string[]
  foreshadowingReminders?: string[]
  endingPitches?: string[]
  aiEvasionPlan?: string
}

export interface ProcessResponse {
  workflowId?: string  // 工作流ID，用于查询进度
  chunkResults: ChunkResult[]
  workflowStages?: Record<string, WorkflowStageSnapshot>
  workflow?: WorkflowSummary
  outline?: string
  memories?: MemoryBlock[]
  creative?: CreativeOutputs
  emittedAt?: string
  outputDir?: string
}

export type WorkflowFlow = 'creation' | 'optimization' | 'detection'

export interface WorkflowTargetMeta {
  id: string
  label: string
  description: string
  module: string
  file: string
  flow: WorkflowFlow
  outputKey: string
  disabled?: boolean
}

export interface AgentModuleMeta {
  id: string
  label: string
  description: string
  file: string
}

export interface CoreServiceMeta {
  id: string
  label: string
  description: string
  file: string
  valueKey?: string
}

