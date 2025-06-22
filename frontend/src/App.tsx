import { useState, useEffect, useCallback } from 'react'
import type { WorkflowSummary, WorkflowStats, WorkflowAnalysis, SearchResponseData } from './types/workflow'
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
  }, []) // fetchData is not added here as it's defined below and memoized.
         // However, if fetchData were a prop or from context, it would be a dependency.
         // For this specific structure, this useEffect runs once on mount.
         // If `fetchData` itself were to change (e.g. if it had its own dependencies and was recreated),
         // and this effect needed to re-run, then `fetchData` would be a dependency here.
         // Given `fetchData`'s current empty dep array, it won't change.

  const fetchData = useCallback((page: number = 1, query: string = '') => {
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
  }, []); // State setters (setIsLoading, setStats, etc.) are stable

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchData(1, searchQuery)
    }, 500)
    return () => clearTimeout(timer)
  }, [searchQuery, fetchData]); // Add fetchData as it's used

  const handleFileSelect = useCallback((file: File) => {
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
  }, []); // Uses setters

  const handleAddWorkflow = useCallback(() => {
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
  }, [selectedFile, currentPage, searchQuery, fetchData]);

  const downloadWorkflow = useCallback((filename: string) => {
    window.open(`/api/workflows/${filename}/download`, '_blank')
  }, []);

  const copyWorkflowJSON = useCallback(async (filename: string) => {
    try {
      const response = await fetch(`/api/workflows/${filename}`)
      const data = await response.json()
      const jsonString = JSON.stringify(data.raw_json, null, 2)
      await navigator.clipboard.writeText(jsonString)
      console.log('JSON copied to clipboard')
    } catch (err) {
      console.error('Failed to copy JSON:', err)
    }
  }, []);

  const copyWorkflowMermaid = useCallback(async (filename: string) => {
    try {
      const response = await fetch(`/api/workflows/${filename}/diagram`)
      const data = await response.json()
      await navigator.clipboard.writeText(data.diagram)
      console.log('Mermaid diagram copied to clipboard')
    } catch (err) {
      console.error('Failed to copy Mermaid:', err)
    }
  }, []);

  const viewWorkflowDetails = useCallback((workflow: WorkflowSummary) => {
    setSelectedWorkflow(workflow)
  }, []);

  const clearFileSelectionHandler = useCallback(() => {
    setSelectedFile(null);
    setAnalysis(null);
  }, []);

  const handleShowAddModal = useCallback(() => setShowAddModal(true), []);
  const handleCloseDetailsModal = useCallback(() => setSelectedWorkflow(null), []);
  const handleCloseAddModal = useCallback(() => setShowAddModal(false), []);

  const handlePageChange = useCallback((newPage: number) => {
    fetchData(newPage, searchQuery);
  }, [fetchData, searchQuery]);


  return (
    <div className="min-h-screen" style={{ padding: '32px' }}>
      <div className="max-w-7xl mx-auto">
        
        <AppHeader
          stats={stats}
          onShowAddModal={handleShowAddModal}
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
          onPageChange={handlePageChange}
        />

        <WorkflowDetailsModal
          workflow={selectedWorkflow}
          onClose={handleCloseDetailsModal}
          onDownload={downloadWorkflow}
          onCopyJson={copyWorkflowJSON}
          onCopyMermaid={copyWorkflowMermaid}
        />

        <AddWorkflowModal
          show={showAddModal}
          onClose={handleCloseAddModal}
          selectedFile={selectedFile}
          analysis={analysis}
          isAnalyzing={isAnalyzing}
          isAdding={isAdding}
          onFileSelect={handleFileSelect}
          onAddWorkflow={handleAddWorkflow}
          onClearFileSelection={clearFileSelectionHandler}
        />

        {/* Footer */}
        <footer style={{
          textAlign: 'center', 
          padding: '40px 20px',
          color: 'hsl(var(--muted-foreground))',
          fontSize: '14px',
          borderTop: '1px solid hsl(var(--border))',
          marginTop: '60px'
        }}>
          <p style={{ margin: '0', lineHeight: '1.6' }}>
            Mess Me Up Longtime License. Do with this what you will. Revamped with Cursor, Claude Code, Jules, so much effing caffeine and a ton of patience. Oh and amazing foresight to take an awesome project and make it... um...awesomer. crushed it. Enjoy. I did. xoxo
          </p>
        </footer>
      </div>
    </div>
  )
}

export default App
