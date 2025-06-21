import React from 'react';
import { WorkflowAnalysis } from '../types/workflow';

interface AddWorkflowModalProps {
  show: boolean;
  onClose: () => void;
  selectedFile: File | null;
  analysis: WorkflowAnalysis | null;
  isAnalyzing: boolean;
  isAdding: boolean;
  onFileSelect: (file: File) => void;
  onAddWorkflow: () => void;
  onClearFileSelection: () => void;
}

const AddWorkflowModal: React.FC<AddWorkflowModalProps> = ({
  show,
  onClose,
  selectedFile,
  analysis,
  isAnalyzing,
  isAdding,
  onFileSelect,
  onAddWorkflow,
  onClearFileSelection,
}) => {
  if (!show) {
    return null;
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.currentTarget.style.borderColor = '#d1d5db';
    e.currentTarget.style.backgroundColor = 'transparent';

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.type === 'application/json' || file.name.endsWith('.json')) {
        onFileSelect(file);
      }
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.currentTarget.style.borderColor = '#3b82f6';
    e.currentTarget.style.backgroundColor = '#f0f9ff';
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.currentTarget.style.borderColor = '#d1d5db';
    e.currentTarget.style.backgroundColor = 'transparent';
  };

  const handleFilePickerClick = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) onFileSelect(file);
    };
    input.click();
  };

  return (
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
            onClick={onClose}
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
          onClick={handleFilePickerClick}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
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
                  <p><strong>Services:</strong> {analysis.services.join(', ')}</p>
                  <p><strong>Node count:</strong> {analysis.node_count}</p>
                  <p><strong>Trigger:</strong> {analysis.trigger_type}</p>
                </div>
              </div>
            )}

            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
              <button
                onClick={onClearFileSelection}
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
                onClick={onAddWorkflow}
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
  );
};

export default AddWorkflowModal;
