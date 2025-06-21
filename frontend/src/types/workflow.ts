export interface WorkflowSummary {
  id?: number | null;
  filename: string;
  name: string;
  active: boolean;
  description?: string;
  trigger_type?: string;
  complexity?: string;
  node_count?: number;
  integrations?: string[];
  tags?: string[];
  created_at?: string | null;
  updated_at?: string | null;
}

export interface WorkflowNode {
  id: string;
  name: string;
  type: string;
  typeVersion: number;
  position: [number, number];
  parameters: Record<string, unknown>;
}

// Updated WorkflowStats as per the prompt
export interface WorkflowStats {
  total: number;
  recentlyAdded: number;
  lastUpdated: string;
  next_available_number: number;
  total_existing: number;
  last_number: number;
}

export interface AddWorkflowRequest {
  name?: string;
  file: File;
}

// Updated AddWorkflowResponse to use WorkflowSummary
export interface AddWorkflowResponse {
  success: boolean;
  message: string;
  filename?: string;
  workflow?: WorkflowSummary;
}

// New WorkflowAnalysis interface as per the prompt
export interface WorkflowAnalysis {
  success: boolean;
  original_filename: string;
  suggested_filename: string;
  workflow_name: string;
  services: string[];
  purpose: string;
  trigger_type: string;
  node_count: number;
  next_number: number;
  analysis: Record<string, any>; // Or a more specific type if the structure of 'analysis' object is known and consistent
  error?: string | null;
}

// New SearchResponseData interface as per the prompt
export interface SearchResponseData {
  workflows: WorkflowSummary[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
  query: string;
  filters: Record<string, any>; // Adjust if filters structure is known
}

// Existing AnalyzeWorkflowResponse from the original file.
// This is kept in case it's used by other parts of the application.
// The subtask specifically asks for the new `WorkflowAnalysis` for the `/api/analyze-workflow` endpoint.
export interface AnalyzeWorkflowResponse {
  suggestedName: string;
  analysis: {
    nodeCount: number;
    triggerType: string;
    services: string[];
    complexity: 'simple' | 'medium' | 'complex';
    description: string;
  };
}