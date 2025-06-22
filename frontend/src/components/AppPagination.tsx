import React from 'react';

interface AppPaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (newPage: number) => void;
}

const AppPagination: React.FC<AppPaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
}) => {
  if (totalPages <= 1) {
    return null; // Don't render pagination if only one page or no pages
  }

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      gap: '10px',
      marginBottom: '30px',
      margin: '0 auto 30px auto',
      maxWidth: 'calc((280px * 5) + (24px * 4))' // Match WorkflowGrid max width: 5 nodes + 4 gaps
    }}>
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        style={{
          padding: '8px 16px',
          border: '1px solid hsl(var(--border))',
          backgroundColor: currentPage === 1 ? 'hsl(var(--muted))' : 'hsl(var(--background))',
          color: 'hsl(var(--foreground))',
          borderRadius: '6px',
          cursor: currentPage === 1 ? 'not-allowed' : 'pointer'
        }}
      >
        Previous
      </button>

      <span style={{ color: 'hsl(var(--muted-foreground))', margin: '0 20px' }}>
        Page {currentPage} of {totalPages}
      </span>

      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        style={{
          padding: '8px 16px',
          border: '1px solid hsl(var(--border))',
          backgroundColor: currentPage === totalPages ? 'hsl(var(--muted))' : 'hsl(var(--background))',
          color: 'hsl(var(--foreground))',
          borderRadius: '6px',
          cursor: currentPage === totalPages ? 'not-allowed' : 'pointer'
        }}
      >
        Next
      </button>
    </div>
  );
};

export default AppPagination;
