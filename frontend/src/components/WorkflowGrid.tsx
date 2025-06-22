import React from 'react';
import type { WorkflowSummary } from '../types/workflow';
import WorkflowNode from './WorkflowNode';

interface WorkflowGridProps {
  workflows: WorkflowSummary[];
  isLoading: boolean;
  searchQuery: string; // To display in "No workflows found for..."
  onViewDetails: (workflow: WorkflowSummary) => void;
  onDownload: (filename: string) => void;
  onCopyJson: (filename: string) => void;
}

const WorkflowGrid: React.FC<WorkflowGridProps> = ({
  workflows,
  isLoading, // isLoading is used for the "No workflows found" message logic
  searchQuery,
  onViewDetails,
  onDownload,
  onCopyJson,
}) => {
  if (workflows.length === 0 && !isLoading) {
    return (
      <div style={{
        textAlign: 'center',
        padding: '60px',
        backgroundColor: 'white',
        borderRadius: '8px'
      }}>
        No workflows found
        {searchQuery && ` for "${searchQuery}"`}
      </div>
    );
  }

  return (
    <div style={{ 
      display: 'grid', 
      gridTemplateColumns: 'repeat(4, 1fr)', 
      gap: '24px', 
      marginBottom: '40px'
    }}>
      {workflows.map((workflow) => (
        <WorkflowNode
          key={workflow.id || workflow.filename}
          workflow={workflow}
          onViewDetails={onViewDetails}
          onDownload={onDownload}
          onCopyJson={onCopyJson}
        />
      ))}
    </div>
  );
};

export default WorkflowGrid;
