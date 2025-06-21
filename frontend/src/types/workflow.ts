export interface Workflow {
  id: number
  filename: string
  name: string
  active: boolean
  description: string
  trigger_type: string
  complexity: string
  node_count: number
  integrations: string[]
  tags: string[]
  created_at?: string
  updated_at?: string
}

export interface WorkflowNode {
  id: string
  name: string
  type: string
  typeVersion: number
  position: [number, number]
  parameters: Record<string, unknown>
}

export interface WorkflowStats {
  total: number
  recentlyAdded: number
  lastUpdated: string
}

export interface AddWorkflowRequest {
  name?: string
  file: File
}

export interface AddWorkflowResponse {
  success: boolean
  message: string
  filename?: string
  workflow?: Workflow
}

export interface AnalyzeWorkflowResponse {
  suggestedName: string
  analysis: {
    nodeCount: number
    triggerType: string
    services: string[]
    complexity: 'simple' | 'medium' | 'complex'
    description: string
  }
}