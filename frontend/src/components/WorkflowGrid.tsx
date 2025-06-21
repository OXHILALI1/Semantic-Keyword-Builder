import React from 'react';
import { WorkflowSummary } from '../types/workflow';
import WorkflowCard from './WorkflowCard';

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
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '16px', marginBottom: '30px' }}>
      {workflows.map((workflow) => ( // Changed key to workflow.id or workflow.filename for more stability if available and unique
        <WorkflowCard
          key={workflow.id || workflow.filename} // Assuming filename is unique, or id if available
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
