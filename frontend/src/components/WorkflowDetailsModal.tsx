import React from 'react';
import { WorkflowSummary } from '../types/workflow';

interface WorkflowDetailsModalProps {
  workflow: WorkflowSummary | null;
  onClose: () => void;
  onDownload: (filename: string) => void;
  onCopyJson: (filename: string) => void;
  onCopyMermaid: (filename: string) => void;
}

const WorkflowDetailsModal: React.FC<WorkflowDetailsModalProps> = ({
  workflow,
  onClose,
  onDownload,
  onCopyJson,
  onCopyMermaid,
}) => {
  if (!workflow) {
    return null;
  }

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
        maxWidth: '600px',
        width: '90%',
        maxHeight: '80vh',
        overflow: 'auto'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ fontSize: '24px', fontWeight: 'bold', margin: 0 }}>Workflow Details</h2>
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

        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ fontSize: '20px', marginBottom: '15px', color: '#3b82f6' }}>
            {workflow.name}
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
            <div>
              <p><strong>Filename:</strong> {workflow.filename}</p>
              <p><strong>Node Count:</strong> {workflow.node_count || 'N/A'}</p>
              <p><strong>Trigger Type:</strong> {workflow.trigger_type || 'N/A'}</p>
              <p><strong>Complexity:</strong> <span style={{ textTransform: 'capitalize' }}>{workflow.complexity || 'N/A'}</span></p>
            </div>
            <div>
              <p><strong>Active:</strong> {workflow.active ? '✅ Yes' : '❌ No'}</p>
              {workflow.integrations && workflow.integrations.length > 0 && (
                <div>
                  <strong>Services:</strong>
                  <div style={{ marginTop: '5px' }}>
                    {workflow.integrations.map((service: string, i: number) => (
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

          {workflow.description && (
            <div style={{ marginBottom: '20px' }}>
              <strong>Description:</strong>
              <p style={{ marginTop: '5px', color: '#6b7280' }}>{workflow.description}</p>
            </div>
          )}

          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            <button
              onClick={() => onDownload(workflow.filename)}
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
              onClick={() => onCopyJson(workflow.filename)}
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
              onClick={() => onCopyMermaid(workflow.filename)}
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
  );
};

export default WorkflowDetailsModal;
