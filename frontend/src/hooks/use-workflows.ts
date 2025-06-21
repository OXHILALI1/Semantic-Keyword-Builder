import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import type { Workflow, WorkflowStats, AddWorkflowRequest, AddWorkflowResponse, AnalyzeWorkflowResponse } from '@/types/workflow'

const API_BASE = '/api'

export function useWorkflows() {
  return useQuery({
    queryKey: ['workflows'],
    queryFn: async (): Promise<Workflow[]> => {
      const response = await fetch(`${API_BASE}/workflows`)
      if (!response.ok) {
        throw new Error('Failed to fetch workflows')
      }
      const data = await response.json()
      return data.workflows || []
    },
  })
}

export function useWorkflowStats() {
  return useQuery({
    queryKey: ['workflow-stats'],
    queryFn: async (): Promise<WorkflowStats> => {
      const response = await fetch(`${API_BASE}/workflow-stats`)
      if (!response.ok) {
        throw new Error('Failed to fetch workflow stats')
      }
      return response.json()
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  })
}

export function useAnalyzeWorkflow() {
  return useMutation({
    mutationFn: async (file: File): Promise<AnalyzeWorkflowResponse> => {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(`${API_BASE}/analyze-workflow`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Failed to analyze workflow')
      }

      return response.json()
    },
  })
}

export function useAddWorkflow() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ name, file }: AddWorkflowRequest): Promise<AddWorkflowResponse> => {
      const formData = new FormData()
      formData.append('file', file)
      if (name) {
        formData.append('name', name)
      }

      const response = await fetch(`${API_BASE}/add-workflow`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Failed to add workflow')
      }

      return response.json()
    },
    onSuccess: () => {
      // Invalidate and refetch workflows and stats
      queryClient.invalidateQueries({ queryKey: ['workflows'] })
      queryClient.invalidateQueries({ queryKey: ['workflow-stats'] })
    },
  })
}