import React from 'react';

interface WorkflowSearchProps {
  searchQuery: string;
  onSearchQueryChange: (query: string) => void;
  isLoading: boolean;
  currentPage: number;
  totalPages: number;
  workflowsCount: number;
}

const WorkflowSearch: React.FC<WorkflowSearchProps> = ({
  searchQuery,
  onSearchQueryChange,
  isLoading,
  currentPage,
  totalPages,
  workflowsCount,
}) => {
  return (
    <>
      {/* Search Bar */}
      <div style={{ marginBottom: '20px' }}>
        <input
          type="text"
          placeholder="Search workflows..."
          value={searchQuery}
          onChange={(e) => onSearchQueryChange(e.target.value)}
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
            Showing page {currentPage} of {totalPages} ({workflowsCount} workflows)
            {searchQuery && ` - Search: "${searchQuery}"`}
          </p>
        )}
      </div>
    </>
  );
};

export default WorkflowSearch;
