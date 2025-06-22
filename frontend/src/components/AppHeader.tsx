import React from 'react';
import type { WorkflowStats, WorkflowSummary } from '../types/workflow'; // WorkflowSummary is not directly used by AppHeader props but good to keep if styles/logic might depend on it indirectly or for future.
import { ThemeSwitcher } from './ThemeSwitcher';

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
    <header 
      className="rounded-xl mb-8 shadow-lg border"
      style={{
        backgroundColor: 'hsl(var(--card))',
        borderColor: 'hsl(var(--border))',
        padding: '32px'
      }}
    >
      <div className="flex justify-between items-start mb-6">
        <div className="flex items-center">
          <img 
            src="/N8n-logo-new.svg" 
            alt="n8n" 
            style={{
              height: '48px',
              marginRight: '16px'
            }}
          />
          <div>
            <h1 className="font-heading text-n8n-orange mb-2" style={{
              fontSize: '28px',
              fontWeight: '700',
              lineHeight: '1.2'
            }}>
              Workflow Repository
            </h1>
            <p className="font-body text-muted-foreground" style={{
              fontSize: '14px',
              margin: '0'
            }}>
              Professional automation collection & management
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <ThemeSwitcher />
          <button
            onClick={onShowAddModal}
            className="bg-n8n-orange hover:bg-n8n-green font-heading px-6 py-3 rounded-lg transition-colors duration-200"
            style={{
              color: 'white',
              fontSize: '16px',
              fontWeight: '600',
              border: 'none',
              cursor: 'pointer'
            }}
          >
            + Add Workflow
          </button>
        </div>
      </div>

      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div 
            className="text-center p-6 rounded-lg border"
            style={{
              backgroundColor: 'hsl(var(--card))',
              borderColor: 'hsl(var(--border))'
            }}
          >
            <div className="font-heading text-n8n-orange text-3xl font-bold mb-1">
              {stats.total.toLocaleString()}
            </div>
            <div className="font-body text-xs text-muted-foreground uppercase tracking-wide">
              Total Workflows
            </div>
          </div>
          <div 
            className="text-center p-6 rounded-lg border"
            style={{
              backgroundColor: 'hsl(var(--card))',
              borderColor: 'hsl(var(--border))'
            }}
          >
            <div className="font-heading text-n8n-green text-3xl font-bold mb-1">
              {stats.recentlyAdded}
            </div>
            <div className="font-body text-xs text-muted-foreground uppercase tracking-wide">
              Recently Added
            </div>
          </div>
          <div 
            className="text-center p-6 rounded-lg border"
            style={{
              backgroundColor: 'hsl(var(--card))',
              borderColor: 'hsl(var(--border))'
            }}
          >
            <div className="font-heading text-n8n-blue text-3xl font-bold mb-1">
              {Math.round(totalPages * itemsPerPage * 0.3)}
            </div>
            <div className="font-body text-xs text-muted-foreground uppercase tracking-wide">
              Estimated Active
            </div>
          </div>
          <div 
            className="text-center p-6 rounded-lg border"
            style={{
              backgroundColor: 'hsl(var(--card))',
              borderColor: 'hsl(var(--border))'
            }}
          >
            <div className="font-heading text-n8n-blue text-3xl font-bold mb-1">
              {totalNodes.toLocaleString()}
            </div>
            <div className="font-body text-xs text-muted-foreground uppercase tracking-wide">
              Total Nodes
            </div>
          </div>
        </div>
      )}
    </header>
  );
};

export default AppHeader;
