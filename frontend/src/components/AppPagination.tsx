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
      marginBottom: '30px'
    }}>
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        style={{
          padding: '8px 16px',
          border: '1px solid #d1d5db',
          backgroundColor: currentPage === 1 ? '#f9fafb' : 'white',
          borderRadius: '6px',
          cursor: currentPage === 1 ? 'not-allowed' : 'pointer'
        }}
      >
        Previous
      </button>

      <span style={{ color: '#6b7280', margin: '0 20px' }}>
        Page {currentPage} of {totalPages}
      </span>

      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        style={{
          padding: '8px 16px',
          border: '1px solid #d1d5db',
          backgroundColor: currentPage === totalPages ? '#f9fafb' : 'white',
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
