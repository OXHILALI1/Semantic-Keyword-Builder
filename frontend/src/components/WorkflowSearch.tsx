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
    <div style={{ 
      margin: '0 auto',
      maxWidth: 'calc((280px * 5) + (24px * 4))', // Match WorkflowGrid max width: 5 nodes + 4 gaps
      marginBottom: '20px',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'flex-end' // Align to right side
    }}>
      {/* Search Bar */}
      <div style={{ marginBottom: '20px', width: '350px', marginRight: '24px' }}>
        <input
          type="text"
          placeholder="Search workflows..."
          value={searchQuery}
          onChange={(e) => onSearchQueryChange(e.target.value)}
          style={{
            width: '100%',
            padding: '12px 16px',
            fontSize: '16px',
            border: '1px solid hsl(var(--border))',
            borderRadius: '8px',
            backgroundColor: 'hsl(var(--background))',
            color: 'hsl(var(--foreground))'
          }}
        />
      </div>

      {/* Results info */}
      <div style={{ marginBottom: '20px', color: 'hsl(var(--muted-foreground))', width: '100%', textAlign: 'left' }}>
        {isLoading ? (
          <p>Loading...</p>
        ) : (
          <p>
            Showing page {currentPage} of {totalPages} ({workflowsCount} workflows)
            {searchQuery && ` - Search: "${searchQuery}"`}
          </p>
        )}
      </div>
    </div>
  );
};

export default WorkflowSearch;
