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
      className="mb-8"
      style={{
        background: 'transparent',
        padding: '24px 0',
        maxWidth: 'calc((280px * 5) + (24px * 4))', // Match WorkflowGrid max width: 5 nodes + 4 gaps
        margin: '0 auto' // Center align with WorkflowNodes
      }}
    >
      <div className="flex justify-between items-center">
        {/* Left side - Logo and Title */}
        <div className="flex items-center">
          {/* Injected SVG Logo */}
          <div style={{ marginRight: '16px' }}>
            <svg width="106" height="43" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 500 200">
              <g>
                <path fill="#EA4B71" d="m239,83c-11.183,0 -20.58,-7.649 -23.244,-18l-27.508,0c-5.866,0 -10.872,4.241 -11.836,10.027l-0.987,5.919c-0.936,5.619 -3.779,10.509 -7.799,14.054c4.02,3.545 6.863,8.435 7.799,14.054l0.987,5.919c0.964,5.786 5.97,10.027 11.836,10.027l3.508,0c2.664,-10.351 12.061,-18 23.244,-18c13.255,0 24,10.745 24,24c0,13.255 -10.745,24 -24,24c-11.183,0 -20.58,-7.649 -23.244,-18l-3.508,0c-11.732,0 -21.744,-8.482 -23.673,-20.054l-0.987,-5.919c-0.964,-5.786 -5.97,-10.027 -11.836,-10.027l-9.508,0c-2.664,10.351 -12.061,18 -23.244,18c-11.183,0 -20.58,-7.649 -23.244,-18l-13.512,0c-2.664,10.351 -12.061,18 -23.244,18c-13.2548,0 -24,-10.745 -24,-24c0,-13.255 10.7452,-24 24,-24c11.183,0 20.58,7.649 23.244,18l13.512,0c2.664,-10.351 12.061,-18 23.244,-18c11.183,0 20.58,7.649 23.244,18l9.508,0c5.866,0 10.872,-4.241 11.836,-10.027l0.987,-5.919c1.929,-11.572 11.941,-20.054 23.673,-20.054l27.508,0c2.664,-10.351 12.061,-18 23.244,-18c13.255,0 24,10.745 24,24c0,13.255 -10.745,24 -24,24zm0,-12c6.627,0 12,-5.373 12,-12c0,-6.627 -5.373,-12 -12,-12c-6.627,0 -12,5.373 -12,12c0,6.627 5.373,12 12,12zm-180,36c6.627,0 12,-5.373 12,-12c0,-6.627 -5.373,-12 -12,-12c-6.6274,0 -12,5.373 -12,12c0,6.627 5.3726,12 12,12zm72,-12c0,6.627 -5.373,12 -12,12c-6.627,0 -12,-5.373 -12,-12c0,-6.627 5.373,-12 12,-12c6.627,0 12,5.373 12,12zm96,36c0,6.627 -5.373,12 -12,12c-6.627,0 -12,-5.373 -12,-12c0,-6.627 5.373,-12 12,-12c6.627,0 12,5.373 12,12z"/>
                <path fill="currentColor" d="m407.017,86.887l0,-0.571c4.187,-2.097 8.374,-5.719 8.374,-12.867c0,-10.294 -8.469,-16.489 -20.173,-16.489c-11.99,0 -20.554,6.576 -20.554,16.679c0,6.863 3.996,10.58 8.374,12.677l0,0.571c-4.853,1.716 -10.658,6.863 -10.658,15.441c0,10.388 8.564,17.632 22.743,17.632c14.178,0 22.457,-7.244 22.457,-17.632c0,-8.578 -5.71,-13.63 -10.563,-15.441zm-11.894,-21.158c4.758,0 8.278,3.049 8.278,8.196c0,5.147 -3.616,8.197 -8.278,8.197c-4.663,0 -8.565,-3.05 -8.565,-8.197c0,-5.242 3.712,-8.196 8.565,-8.196zm0,45.081c-5.52,0 -9.992,-3.526 -9.992,-9.531c0,-5.432 3.711,-9.531 9.896,-9.531c6.091,0 9.802,4.003 9.802,9.722c0,5.814 -4.282,9.34 -9.706,9.34z"/>
                <path fill="currentColor" d="m432.26,119.007l12.18,0l0,-25.829c0,-8.483 5.139,-12.2 10.943,-12.2c5.71,0 10.182,3.813 10.182,11.628l0,26.401l12.18,0l0,-28.879c0,-12.486 -7.232,-19.729 -18.555,-19.729c-7.137,0 -11.134,2.859 -13.989,6.576l-0.761,0l-1.047,-5.623l-11.133,0l0,47.655z"/>
                <path fill="currentColor" d="m324.44,119.007l-12.18,0l0,-47.655l11.133,0l1.047,5.623l0.761,0c2.855,-3.717 6.852,-6.576 13.989,-6.576c11.323,0 18.555,7.243 18.555,19.729l0,28.879l-12.18,0l0,-26.401c0,-7.815 -4.472,-11.628 -10.182,-11.628c-5.804,0 -10.943,3.717 -10.943,12.2l0,25.829z"/>
              </g>
            </svg>
          </div>
          <div>
            <h1 className="font-heading" style={{
              fontSize: '24px',
              fontWeight: '700',
              lineHeight: '1.2',
              color: 'hsl(var(--foreground))',
              margin: '0'
            }}>
              Workflow Repository
            </h1>
            <p className="font-body" style={{
              fontSize: '13px',
              margin: '2px 0 0 0',
              color: 'hsl(var(--muted-foreground))'
            }}>
              Professional automation collection & management
            </p>
          </div>
        </div>

        {/* Center - Stats Badges */}
        {stats && (
          <div className="flex items-center" style={{ gap: '24px' }}>
            <div 
              className="inline-flex items-center rounded-full text-sm font-medium"
              style={{
                backgroundColor: 'hsl(var(--primary) / 0.1)',
                color: 'hsl(var(--primary))',
                border: '1px solid hsl(var(--primary) / 0.2)',
                padding: '8px 16px'
              }}
            >
              <span style={{ fontWeight: '600' }}>{stats.total.toLocaleString()}</span>
              <span style={{ marginLeft: '8px', opacity: '0.8' }}>workflows</span>
            </div>
            <div 
              className="inline-flex items-center rounded-full text-sm font-medium"
              style={{
                backgroundColor: 'hsl(var(--secondary) / 0.8)',
                color: 'hsl(var(--secondary-foreground))',
                border: '1px solid hsl(var(--secondary))',
                padding: '8px 16px'
              }}
            >
              <span style={{ fontWeight: '600' }}>{stats.recentlyAdded}</span>
              <span style={{ marginLeft: '8px', opacity: '0.8' }}>recent</span>
            </div>
            <div 
              className="inline-flex items-center rounded-full text-sm font-medium"
              style={{
                backgroundColor: 'hsl(var(--accent) / 0.1)',
                color: 'hsl(var(--accent-foreground))',
                border: '1px solid hsl(var(--accent) / 0.3)',
                padding: '8px 16px'
              }}
            >
              <span style={{ fontWeight: '600' }}>{totalNodes.toLocaleString()}</span>
              <span style={{ marginLeft: '8px', opacity: '0.8' }}>nodes</span>
            </div>
          </div>
        )}

        {/* Right side - Controls */}
        <div className="flex items-center" style={{ gap: '24px' }}>
          <ThemeSwitcher />
          <button
            onClick={onShowAddModal}
            className="font-heading transition-all duration-200"
            style={{
              color: '#ff6b35',
              fontSize: '14px',
              fontWeight: '600',
              border: '2px solid #ff6b35',
              backgroundColor: 'transparent',
              borderRadius: '8px',
              padding: '10px 20px',
              cursor: 'pointer'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'hsl(var(--card))';
              e.currentTarget.style.color = '#ff6b35';
              e.currentTarget.style.transform = 'translateY(-1px)';
              e.currentTarget.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.15)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
              e.currentTarget.style.color = '#ff6b35';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            + Add Workflow
          </button>
        </div>
      </div>
    </header>
  );
};

export default AppHeader;
