import React from 'react';
import { WorkflowSummary } from '../types/workflow';

interface WorkflowCardProps {
  workflow: WorkflowSummary;
  onViewDetails: (workflow: WorkflowSummary) => void;
  onDownload: (filename: string) => void;
  onCopyJson: (filename: string) => void;
}

const WorkflowCard: React.FC<WorkflowCardProps> = ({
  workflow,
  onViewDetails,
  onDownload,
  onCopyJson,
}) => {
  return (
    <div style={{
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
    onClick={() => onViewDetails(workflow)}
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
        <div>Nodes: {workflow.node_count || 'N/A'}</div>
        <div>Trigger: {workflow.trigger_type || 'N/A'}</div>
        <div style={{ textTransform: 'capitalize' }}>Complexity: {workflow.complexity || 'N/A'}</div>
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
            e.stopPropagation(); // Prevent card's onClick from firing
            onDownload(workflow.filename);
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
            e.stopPropagation(); // Prevent card's onClick from firing
            onCopyJson(workflow.filename);
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
  );
};

export default WorkflowCard;
