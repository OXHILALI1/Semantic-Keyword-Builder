import { useState, useEffect } from 'react'
import { WorkflowSummary, WorkflowStats, WorkflowAnalysis, SearchResponseData } from './types/workflow'
import AppHeader from './components/AppHeader';
import WorkflowSearch from './components/WorkflowSearch';
import WorkflowGrid from './components/WorkflowGrid';
import AppPagination from './components/AppPagination';
import WorkflowDetailsModal from './components/WorkflowDetailsModal';
import AddWorkflowModal from './components/AddWorkflowModal';

function App() {
  const [stats, setStats] = useState<WorkflowStats | null>(null)
  const [workflows, setWorkflows] = useState<WorkflowSummary[]>([])
  const [showAddModal, setShowAddModal] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [analysis, setAnalysis] = useState<WorkflowAnalysis | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isAdding, setIsAdding] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [isLoading, setIsLoading] = useState(false)
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowSummary | null>(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = (page: number = 1, query: string = '') => {
    setIsLoading(true)
    
    // Fetch stats
    fetch('/api/workflow-stats')
      .then(res => res.json() as Promise<WorkflowStats>)
      .then(data => setStats(data))
      .catch(err => console.error('Stats error:', err))

    // Fetch workflows with pagination and search
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: '20',
      q: query
    })

    fetch(`/api/workflows?${params}`)
      .then(res => res.json() as Promise<SearchResponseData>)
      .then(data => {
        setWorkflows(data.workflows || [])
        setTotalPages(data.pages || 1)
        setCurrentPage(page)
        setIsLoading(false)
      })
      .catch(err => {
        console.error('Workflows error:', err)
        setIsLoading(false)
      })
  }

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchData(1, searchQuery)
    }, 500)
    return () => clearTimeout(timer)
  }, [searchQuery])

  const handleFileSelect = (file: File) => {
    setSelectedFile(file)
    setAnalysis(null)
    setIsAnalyzing(true)

    const formData = new FormData()
    formData.append('file', file)

    fetch('/api/analyze-workflow', {
      method: 'POST',
      body: formData
    })
    .then(res => res.json() as Promise<WorkflowAnalysis>)
    .then(data => {
      setAnalysis(data)
      setIsAnalyzing(false)
    })
    .catch(err => {
      console.error('Analysis error:', err)
      setIsAnalyzing(false)
    })
  }

  const handleAddWorkflow = () => {
    if (!selectedFile) return

    setIsAdding(true)
    const formData = new FormData()
    formData.append('file', selectedFile)

    fetch('/api/add-workflow', {
      method: 'POST',
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        setShowAddModal(false)
        setSelectedFile(null)
        setAnalysis(null)
        fetchData(currentPage, searchQuery) // Refresh data
      }
      setIsAdding(false)
    })
    .catch(err => {
      console.error('Add workflow error:', err)
      setIsAdding(false)
    })
  }

  const downloadWorkflow = (filename: string) => {
    window.open(`/api/workflows/${filename}/download`, '_blank')
  }

  const copyWorkflowJSON = async (filename: string) => {
    try {
      const response = await fetch(`/api/workflows/${filename}`)
      const data = await response.json()
      const jsonString = JSON.stringify(data.raw_json, null, 2)
      await navigator.clipboard.writeText(jsonString)
      console.log('JSON copied to clipboard')
    } catch (err) {
      console.error('Failed to copy JSON:', err)
    }
  }

  const copyWorkflowMermaid = async (filename: string) => {
    try {
      const response = await fetch(`/api/workflows/${filename}/diagram`)
      const data = await response.json()
      await navigator.clipboard.writeText(data.diagram)
      console.log('Mermaid diagram copied to clipboard')
    } catch (err) {
      console.error('Failed to copy Mermaid:', err)
    }
  }

  const viewWorkflowDetails = (workflow: WorkflowSummary) => {
    setSelectedWorkflow(workflow)
  }

  const clearFileSelectionHandler = () => {
    setSelectedFile(null);
    setAnalysis(null);
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb', padding: '20px' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        
        <AppHeader
          stats={stats}
          onShowAddModal={() => setShowAddModal(true)}
          totalPages={totalPages}
          itemsPerPage={20} // Assuming 20 items per page from fetchData constant
          totalNodes={workflows.reduce((acc, w) => acc + (w.node_count || 0), 0)}
        />

        <WorkflowSearch
          searchQuery={searchQuery}
          onSearchQueryChange={setSearchQuery}
          isLoading={isLoading}
          currentPage={currentPage}
          totalPages={totalPages}
          workflowsCount={workflows.length}
        />

        <WorkflowGrid
          workflows={workflows}
          isLoading={isLoading}
          searchQuery={searchQuery}
          onViewDetails={viewWorkflowDetails}
          onDownload={downloadWorkflow}
          onCopyJson={copyWorkflowJSON}
        />

        <AppPagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={(newPage) => fetchData(newPage, searchQuery)}
        />

        <WorkflowDetailsModal
          workflow={selectedWorkflow}
          onClose={() => setSelectedWorkflow(null)}
          onDownload={downloadWorkflow}
          onCopyJson={copyWorkflowJSON}
          onCopyMermaid={copyWorkflowMermaid}
        />

        <AddWorkflowModal
          show={showAddModal}
          onClose={() => setShowAddModal(false)}
          selectedFile={selectedFile}
          analysis={analysis}
          isAnalyzing={isAnalyzing}
          isAdding={isAdding}
          onFileSelect={handleFileSelect}
          onAddWorkflow={handleAddWorkflow}
          onClearFileSelection={clearFileSelectionHandler}
        />
      </div>
    </div>
  )
}

export default App
