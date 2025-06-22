import React from 'react';
import type { WorkflowSummary } from '../types/workflow';

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
    <div 
      className="p-6 rounded-lg shadow-sm border cursor-pointer transition-shadow hover:shadow-md"
      style={{
        backgroundColor: 'hsl(var(--card))',
        borderColor: 'hsl(var(--border))',
        minHeight: '200px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between'
      }}
      onClick={() => onViewDetails(workflow)}
    >
      <div>
        <h3 className="font-heading text-card-foreground text-lg font-semibold mb-3 leading-tight">
          {workflow.name}
        </h3>
        <div className="font-body text-xs text-muted-foreground mb-4 space-y-1">
          <div>Nodes: {workflow.node_count || 'N/A'}</div>
          <div>Trigger: {workflow.trigger_type || 'N/A'}</div>
          <div className="capitalize">Complexity: {workflow.complexity || 'N/A'}</div>
          {workflow.integrations && workflow.integrations.length > 0 && (
            <div className="mt-2">
              <span className="text-turbo-teal font-medium">Services:</span>{' '}
              {workflow.integrations.slice(0, 3).join(', ')}
              {workflow.integrations.length > 3 && (
                <span className="text-apache-rose"> +{workflow.integrations.length - 3} more</span>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="flex gap-2 mt-4 justify-start">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDownload(workflow.filename);
          }}
          className="bg-turbo-teal font-body text-xs px-4 py-2 rounded-md border-none cursor-pointer hover:bg-apache-rose transition-colors"
          style={{
            color: 'var(--balaclava-black)',
          }}
        >
          📥 Download
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onCopyJson(workflow.filename);
          }}
          className="bg-apache-rose font-body text-xs px-4 py-2 rounded-md border-none cursor-pointer hover:bg-turbo-teal transition-colors"
          style={{
            color: 'var(--cracker)',
          }}
        >
          📋 Copy JSON
        </button>
      </div>
    </div>
  );
};

export default WorkflowCard;
