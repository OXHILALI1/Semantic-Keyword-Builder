import React from 'react';
import { WorkflowStats, WorkflowSummary } from '../types/workflow'; // WorkflowSummary is not directly used by AppHeader props but good to keep if styles/logic might depend on it indirectly or for future.

interface AppHeaderProps {
  stats: WorkflowStats | null;
  onShowAddModal: () => void;
  totalPages: number;
  itemsPerPage: number; // Typically a constant like 20, passed from App.tsx
  totalNodes: number; // Pre-calculated: workflows.reduce(...) in App.tsx
}

const AppHeader: React.FC<AppHeaderProps> = ({
  stats,
  onShowAddModal,
  totalPages,
  itemsPerPage,
  totalNodes
}) => {
  return (
    <header style={{
      backgroundColor: 'white',
      padding: '30px',
      borderRadius: '12px',
      marginBottom: '20px',
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '20px' }}>
        <div>
          <h1 style={{
            fontSize: '36px',
            fontWeight: 'bold',
            color: '#3b82f6',
            marginBottom: '10px'
          }}>
            ⚡ N8N Workflow Repository
          </h1>
          <p style={{ color: '#6b7280' }}>
            Professional workflow automation collection & management system
          </p>
        </div>
        <button
          onClick={onShowAddModal}
          style={{
            backgroundColor: '#3b82f6',
            color: 'white',
            padding: '12px 24px',
            borderRadius: '8px',
            border: 'none',
            fontSize: '16px',
            fontWeight: '600',
            cursor: 'pointer'
          }}
        >
          + Add Workflow
        </button>
      </div>

      {stats && (
        <div style={{ display: 'flex', gap: '40px', flexWrap: 'wrap' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#3b82f6' }}>
              {stats.total.toLocaleString()}
            </div>
            <div style={{ fontSize: '12px', color: '#9ca3af', textTransform: 'uppercase' }}>
              Total Workflows
            </div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#059669' }}>
              {stats.recentlyAdded}
            </div>
            <div style={{ fontSize: '12px', color: '#9ca3af', textTransform: 'uppercase' }}>
              Recently Added
            </div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#dc2626' }}>
              {/* This calculation was Math.round(totalPages * 20 * 0.3)
                  Using itemsPerPage prop now.
              */}
              {Math.round(totalPages * itemsPerPage * 0.3)}
            </div>
            <div style={{ fontSize: '12px', color: '#9ca3af', textTransform: 'uppercase' }}>
              Estimated Active
            </div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#7c3aed' }}>
              {totalNodes.toLocaleString()}
            </div>
            <div style={{ fontSize: '12px', color: '#9ca3af', textTransform: 'uppercase' }}>
              Total Nodes
            </div>
          </div>
        </div>
      )}
    </header>
  );
};

export default AppHeader;
