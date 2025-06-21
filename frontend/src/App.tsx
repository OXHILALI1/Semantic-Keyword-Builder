import { useState, useEffect } from 'react'

function App() {
  const [stats, setStats] = useState<any>(null)
  const [workflows, setWorkflows] = useState<any[]>([])
  const [showAddModal, setShowAddModal] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [analysis, setAnalysis] = useState<any>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isAdding, setIsAdding] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [isLoading, setIsLoading] = useState(false)
  const [selectedWorkflow, setSelectedWorkflow] = useState<any>(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = (page: number = 1, query: string = '') => {
    setIsLoading(true)
    
    // Fetch stats
    fetch('/api/workflow-stats')
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(err => console.error('Stats error:', err))

    // Fetch workflows with pagination and search
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: '20',
      q: query
    })

    fetch(`/api/workflows?${params}`)
      .then(res => res.json())
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
    .then(res => res.json())
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

  const viewWorkflowDetails = (workflow: any) => {
    setSelectedWorkflow(workflow)
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb', padding: '20px' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        
        {/* Header */}
        <header style={{ 
          backgroundColor: 'white', 
          padding: '30px', 
          borderRadius: '12px',
          marginBottom: '20px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '20px' }}>
            <div>
              <h1 style={{ 
                fontSize: '36px', 
                fontWeight: 'bold', 
                color: '#3b82f6',
                marginBottom: '10px'
              }}>
                ⚡ N8N Workflow Repository
              </h1>
              <p style={{ color: '#6b7280' }}>
                Professional workflow automation collection & management system
              </p>
            </div>
            <button 
              onClick={() => setShowAddModal(true)}
              style={{
                backgroundColor: '#3b82f6',
                color: 'white',
                padding: '12px 24px',
                borderRadius: '8px',
                border: 'none',
                fontSize: '16px',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              + Add Workflow
            </button>
          </div>
          
          {stats && (
            <div style={{ display: 'flex', gap: '40px', flexWrap: 'wrap' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#3b82f6' }}>
                  {stats.total?.toLocaleString() || 0}
                </div>
                <div style={{ fontSize: '12px', color: '#9ca3af', textTransform: 'uppercase' }}>
                  Total Workflows
                </div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#059669' }}>
                  {stats.recentlyAdded || 0}
                </div>
                <div style={{ fontSize: '12px', color: '#9ca3af', textTransform: 'uppercase' }}>
                  Recently Added
                </div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#dc2626' }}>
                  {Math.round(totalPages * 20 * 0.3)}
                </div>
                <div style={{ fontSize: '12px', color: '#9ca3af', textTransform: 'uppercase' }}>
                  Estimated Active
                </div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#7c3aed' }}>
                  {workflows.reduce((acc, w) => acc + (w.node_count || 0), 0).toLocaleString()}
                </div>
                <div style={{ fontSize: '12px', color: '#9ca3af', textTransform: 'uppercase' }}>
                  Total Nodes
                </div>
              </div>
            </div>
          )}
        </header>

        {/* Search Bar */}
        <div style={{ marginBottom: '20px' }}>
          <input
            type="text"
            placeholder="Search workflows..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '12px 16px',
              fontSize: '16px',
              border: '1px solid #d1d5db',
              borderRadius: '8px',
              backgroundColor: 'white'
            }}
          />
        </div>

        {/* Results info */}
        <div style={{ marginBottom: '20px', color: '#6b7280' }}>
          {isLoading ? (
            <p>Loading...</p>
          ) : (
            <p>
              Showing page {currentPage} of {totalPages} ({workflows.length} workflows)
              {searchQuery && ` - Search: "${searchQuery}"`}
            </p>
          )}
        </div>

        {/* Workflows Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '16px', marginBottom: '30px' }}>
          {workflows.map((workflow, i) => (
            <div key={i} style={{
              backgroundColor: 'white',
              padding: '20px',
              borderRadius: '8px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              border: '1px solid #e5e7eb',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)'
              e.currentTarget.style.transform = 'translateY(-2px)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)'
              e.currentTarget.style.transform = 'translateY(0)'
            }}
            onClick={() => viewWorkflowDetails(workflow)}
            >
              <h3 style={{ 
                fontSize: '16px', 
                fontWeight: '600', 
                marginBottom: '10px',
                lineHeight: '1.4'
              }}>
                {workflow.name}
              </h3>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '15px' }}>
                <div>Nodes: {workflow.node_count}</div>
                <div>Trigger: {workflow.trigger_type}</div>
                <div style={{ textTransform: 'capitalize' }}>Complexity: {workflow.complexity}</div>
                {workflow.integrations && workflow.integrations.length > 0 && (
                  <div style={{ marginTop: '5px' }}>
                    Services: {workflow.integrations.slice(0, 3).join(', ')}
                    {workflow.integrations.length > 3 && ` +${workflow.integrations.length - 3} more`}
                  </div>
                )}
              </div>
              
              <div style={{ display: 'flex', gap: '8px', marginTop: '10px' }}>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    downloadWorkflow(workflow.filename)
                  }}
                  style={{
                    padding: '6px 12px',
                    fontSize: '12px',
                    backgroundColor: '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  📥 Download
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    copyWorkflowJSON(workflow.filename)
                  }}
                  style={{
                    padding: '6px 12px',
                    fontSize: '12px',
                    backgroundColor: '#059669',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  📋 Copy JSON
                </button>
              </div>
            </div>
          ))}
        </div>

        {workflows.length === 0 && !isLoading && (
          <div style={{ 
            textAlign: 'center', 
            padding: '60px',
            backgroundColor: 'white',
            borderRadius: '8px'
          }}>
            No workflows found
            {searchQuery && ` for "${searchQuery}"`}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center',
            gap: '10px',
            marginBottom: '30px'
          }}>
            <button
              onClick={() => fetchData(currentPage - 1, searchQuery)}
              disabled={currentPage === 1}
              style={{
                padding: '8px 16px',
                border: '1px solid #d1d5db',
                backgroundColor: currentPage === 1 ? '#f9fafb' : 'white',
                borderRadius: '6px',
                cursor: currentPage === 1 ? 'not-allowed' : 'pointer'
              }}
            >
              Previous
            </button>
            
            <span style={{ color: '#6b7280', margin: '0 20px' }}>
              Page {currentPage} of {totalPages}
            </span>
            
            <button
              onClick={() => fetchData(currentPage + 1, searchQuery)}
              disabled={currentPage === totalPages}
              style={{
                padding: '8px 16px',
                border: '1px solid #d1d5db',
                backgroundColor: currentPage === totalPages ? '#f9fafb' : 'white',
                borderRadius: '6px',
                cursor: currentPage === totalPages ? 'not-allowed' : 'pointer'
              }}
            >
              Next
            </button>
          </div>
        )}

        {/* Workflow Details Modal */}
        {selectedWorkflow && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}>
            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              padding: '30px',
              maxWidth: '600px',
              width: '90%',
              maxHeight: '80vh',
              overflow: 'auto'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h2 style={{ fontSize: '24px', fontWeight: 'bold', margin: 0 }}>Workflow Details</h2>
                <button 
                  onClick={() => setSelectedWorkflow(null)}
                  style={{
                    background: 'none',
                    border: 'none',
                    fontSize: '24px',
                    cursor: 'pointer',
                    padding: '0',
                    color: '#6b7280'
                  }}
                >
                  ×
                </button>
              </div>

              <div style={{ marginBottom: '20px' }}>
                <h3 style={{ fontSize: '20px', marginBottom: '15px', color: '#3b82f6' }}>
                  {selectedWorkflow.name}
                </h3>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
                  <div>
                    <p><strong>Filename:</strong> {selectedWorkflow.filename}</p>
                    <p><strong>Node Count:</strong> {selectedWorkflow.node_count}</p>
                    <p><strong>Trigger Type:</strong> {selectedWorkflow.trigger_type}</p>
                    <p><strong>Complexity:</strong> <span style={{ textTransform: 'capitalize' }}>{selectedWorkflow.complexity}</span></p>
                  </div>
                  <div>
                    <p><strong>Active:</strong> {selectedWorkflow.active ? '✅ Yes' : '❌ No'}</p>
                    {selectedWorkflow.integrations && selectedWorkflow.integrations.length > 0 && (
                      <div>
                        <strong>Services:</strong>
                        <div style={{ marginTop: '5px' }}>
                          {selectedWorkflow.integrations.map((service: string, i: number) => (
                            <span key={i} style={{
                              display: 'inline-block',
                              backgroundColor: '#f3f4f6',
                              padding: '2px 8px',
                              margin: '2px',
                              borderRadius: '12px',
                              fontSize: '12px'
                            }}>
                              {service}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {selectedWorkflow.description && (
                  <div style={{ marginBottom: '20px' }}>
                    <strong>Description:</strong>
                    <p style={{ marginTop: '5px', color: '#6b7280' }}>{selectedWorkflow.description}</p>
                  </div>
                )}

                <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                  <button
                    onClick={() => downloadWorkflow(selectedWorkflow.filename)}
                    style={{
                      padding: '10px 20px',
                      backgroundColor: '#3b82f6',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer'
                    }}
                  >
                    📥 Download JSON
                  </button>
                  <button
                    onClick={() => copyWorkflowJSON(selectedWorkflow.filename)}
                    style={{
                      padding: '10px 20px',
                      backgroundColor: '#059669',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer'
                    }}
                  >
                    📋 Copy JSON
                  </button>
                  <button
                    onClick={() => copyWorkflowMermaid(selectedWorkflow.filename)}
                    style={{
                      padding: '10px 20px',
                      backgroundColor: '#7c3aed',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer'
                    }}
                  >
                    🎨 Copy Mermaid
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Add Workflow Modal */}
        {showAddModal && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}>
            <div style={{
              backgroundColor: 'white',
              borderRadius: '12px',
              padding: '30px',
              maxWidth: '500px',
              width: '90%',
              maxHeight: '80vh',
              overflow: 'auto'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h2 style={{ fontSize: '24px', fontWeight: 'bold', margin: 0 }}>Add New Workflow</h2>
                <button 
                  onClick={() => setShowAddModal(false)}
                  style={{
                    background: 'none',
                    border: 'none',
                    fontSize: '24px',
                    cursor: 'pointer',
                    padding: '0',
                    color: '#6b7280'
                  }}
                >
                  ×
                </button>
              </div>

              {!selectedFile ? (
                <div style={{
                  border: '2px dashed #d1d5db',
                  borderRadius: '8px',
                  padding: '40px',
                  textAlign: 'center',
                  cursor: 'pointer'
                }}
                onClick={() => {
                  const input = document.createElement('input')
                  input.type = 'file'
                  input.accept = '.json'
                  input.onchange = (e) => {
                    const file = (e.target as HTMLInputElement).files?.[0]
                    if (file) handleFileSelect(file)
                  }
                  input.click()
                }}
                onDragOver={(e) => {
                  e.preventDefault()
                  e.currentTarget.style.borderColor = '#3b82f6'
                  e.currentTarget.style.backgroundColor = '#f0f9ff'
                }}
                onDragLeave={(e) => {
                  e.preventDefault()
                  e.currentTarget.style.borderColor = '#d1d5db'
                  e.currentTarget.style.backgroundColor = 'transparent'
                }}
                onDrop={(e) => {
                  e.preventDefault()
                  e.currentTarget.style.borderColor = '#d1d5db'
                  e.currentTarget.style.backgroundColor = 'transparent'
                  
                  const files = e.dataTransfer.files
                  if (files.length > 0) {
                    const file = files[0]
                    if (file.type === 'application/json' || file.name.endsWith('.json')) {
                      handleFileSelect(file)
                    }
                  }
                }}
                >
                  <div style={{ fontSize: '48px', marginBottom: '10px' }}>📁</div>
                  <p style={{ fontSize: '18px', fontWeight: '600', marginBottom: '10px' }}>
                    Drop your workflow file here
                  </p>
                  <p style={{ color: '#6b7280' }}>
                    or click to browse (.json files only)
                  </p>
                </div>
              ) : (
                <div>
                  <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#f3f4f6', borderRadius: '8px' }}>
                    <h3 style={{ fontSize: '16px', marginBottom: '10px' }}>📄 {selectedFile.name}</h3>
                    <p style={{ color: '#6b7280', fontSize: '14px' }}>
                      {(selectedFile.size / 1024).toFixed(1)} KB
                    </p>
                  </div>

                  {isAnalyzing && (
                    <div style={{ textAlign: 'center', padding: '20px' }}>
                      <p>🔄 Analyzing workflow...</p>
                    </div>
                  )}

                  {analysis && (
                    <div style={{ marginBottom: '20px' }}>
                      <h3 style={{ fontSize: '18px', marginBottom: '15px' }}>Analysis Results:</h3>
                      <div style={{ backgroundColor: '#f0f9ff', padding: '15px', borderRadius: '8px', marginBottom: '15px' }}>
                        <p><strong>Suggested filename:</strong> {analysis.suggested_filename}</p>
                        <p><strong>Services:</strong> {analysis.services?.join(', ')}</p>
                        <p><strong>Node count:</strong> {analysis.node_count}</p>
                        <p><strong>Trigger:</strong> {analysis.trigger_type}</p>
                      </div>
                    </div>
                  )}

                  <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                    <button 
                      onClick={() => {
                        setSelectedFile(null)
                        setAnalysis(null)
                      }}
                      style={{
                        padding: '10px 20px',
                        border: '1px solid #d1d5db',
                        backgroundColor: 'white',
                        borderRadius: '6px',
                        cursor: 'pointer'
                      }}
                    >
                      Choose Different File
                    </button>
                    <button 
                      onClick={handleAddWorkflow}
                      disabled={isAdding || !analysis}
                      style={{
                        padding: '10px 20px',
                        backgroundColor: '#3b82f6',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: isAdding ? 'not-allowed' : 'pointer',
                        opacity: isAdding ? 0.6 : 1
                      }}
                    >
                      {isAdding ? 'Adding...' : 'Add Workflow'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
