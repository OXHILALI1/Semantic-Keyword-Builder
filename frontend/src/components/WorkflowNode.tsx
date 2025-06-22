import React from 'react';
import type { WorkflowSummary } from '../types/workflow';

interface WorkflowNodeProps {
  workflow: WorkflowSummary;
  onViewDetails: (workflow: WorkflowSummary) => void;
  onDownload: (filename: string) => void;
  onCopyJson: (filename: string) => void;
}


// Get status color based on workflow properties
const getStatusColor = (workflow: WorkflowSummary): string => {
  if (workflow.active) return 'text-n8n-green';
  if (workflow.complexity === 'high') return 'text-n8n-red';
  return 'text-n8n-orange';
};

const WorkflowNode: React.FC<WorkflowNodeProps> = ({
  workflow,
  onViewDetails,
  onDownload,
  onCopyJson,
}) => {
  const statusColor = getStatusColor(workflow);

  return (
    <div
      className="group relative cursor-pointer transition-all duration-200 hover:shadow-lg"
      style={{
        backgroundColor: 'hsl(var(--card))',
        borderColor: 'hsl(var(--border))',
        border: '1px solid',
        borderRadius: '12px',
        padding: '24px',
        minHeight: '180px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
      }}
      onClick={() => onViewDetails(workflow)}
    >
      {/* Left Border Rectangle */}
      <div
        style={{
          position: 'absolute',
          left: '-6px',
          top: '50%',
          transform: 'translateY(-50%)',
          width: '12px',
          height: '24px',
          backgroundColor: 'light-dark(#ff6b35, hsl(var(--border)))',
          borderRadius: '3px',
          zIndex: 10
        }}
      />

      {/* Right Border Circle */}
      <div
        style={{
          position: 'absolute',
          right: '-8px',
          top: '50%',
          transform: 'translateY(-50%)',
          width: '16px',
          height: '16px',
          backgroundColor: 'light-dark(#ff6b35, hsl(var(--border)))',
          borderRadius: '50%',
          zIndex: 10
        }}
      />

      {/* Header Section */}
      <div className="flex items-start justify-between mb-4">
        <div style={{ flex: '1', minWidth: '0', paddingRight: '12px' }}>
          {/* Workflow Name */}
          <h3 style={{
            fontWeight: '600',
            fontSize: '16px',
            color: 'hsl(var(--foreground))',
            margin: '0 0 8px 0',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
            width: '100%'
          }}>
            {workflow.name}
          </h3>
          <div 
            className={`text-xs font-medium ${statusColor}`}
            style={{ marginTop: '4px' }}
          >
            {workflow.active ? 'Active' : 'Draft'}
          </div>
        </div>
        
        {/* Status Indicator Dot */}
        <div 
          className={`w-3 h-3 rounded-full ${workflow.active ? 'bg-n8n-green' : 'bg-muted-foreground/30'}`}
          style={{ marginTop: '4px', flexShrink: '0' }}
        />
      </div>

      {/* Workflow Details */}
      <div 
        className="font-body space-y-2 mb-4"
        style={{
          color: 'hsl(var(--muted-foreground))',
          fontSize: '12px'
        }}
      >
        <div className="flex justify-between">
          <span>Nodes:</span>
          <span style={{ fontWeight: '500' }}>{workflow.node_count || 'N/A'}</span>
        </div>
        <div className="flex justify-between">
          <span>Trigger:</span>
          <span style={{ fontWeight: '500' }}>{workflow.trigger_type || 'Manual'}</span>
        </div>
        <div className="flex justify-between">
          <span>Complexity:</span>
          <span 
            className={`capitalize ${
              workflow.complexity === 'high' ? 'text-n8n-red' :
              workflow.complexity === 'medium' ? 'text-n8n-orange' : 'text-n8n-green'
            }`}
            style={{ fontWeight: '500' }}
          >
            {workflow.complexity || 'Low'}
          </span>
        </div>
      </div>

      {/* Services Integration Tags */}
      {workflow.integrations && workflow.integrations.length > 0 && (
        <div className="mb-4">
          <div 
            style={{
              color: 'hsl(var(--muted-foreground))',
              fontSize: '12px',
              marginBottom: '8px'
            }}
          >
            Services:
          </div>
          <div className="flex flex-wrap gap-1">
            {workflow.integrations.slice(0, 3).map((service, index) => (
              <span
                key={index}
                style={{
                  display: 'inline-block',
                  padding: '4px 8px',
                  fontSize: '12px',
                  borderRadius: '6px',
                  backgroundColor: 'hsl(var(--primary) / 0.1)',
                  color: 'hsl(var(--primary))',
                  border: '1px solid hsl(var(--primary) / 0.2)'
                }}
              >
                {service}
              </span>
            ))}
            {workflow.integrations.length > 3 && (
              <span 
                style={{
                  display: 'inline-block',
                  padding: '4px 8px',
                  fontSize: '12px',
                  borderRadius: '6px',
                  backgroundColor: 'hsl(var(--muted))',
                  color: 'hsl(var(--muted-foreground))'
                }}
              >
                +{workflow.integrations.length - 3}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div 
        className="absolute bottom-4 right-4 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
      >
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDownload(workflow.filename);
          }}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            padding: '6px 12px',
            fontSize: '12px',
            backgroundColor: 'hsl(var(--secondary))',
            color: 'hsl(var(--secondary-foreground))',
            borderRadius: '6px',
            border: 'none',
            cursor: 'pointer',
            transition: 'background-color 0.2s'
          }}
          title="Download Workflow"
        >
          ↓
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onCopyJson(workflow.filename);
          }}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            padding: '6px 12px',
            fontSize: '12px',
            backgroundColor: 'hsl(var(--primary))',
            color: 'hsl(var(--primary-foreground))',
            borderRadius: '6px',
            border: 'none',
            cursor: 'pointer',
            transition: 'background-color 0.2s'
          }}
          title="Copy JSON"
        >
          ⧉
        </button>
      </div>
    </div>
  );
};

export default WorkflowNode;