'use client';

import type { FC, ReactNode } from 'react';
import { Panel } from './Panel';
import { useLayoutStore } from '@/stores/layoutStore';

interface RightPanelProps {
  children?: ReactNode;
}

export const RightPanel: FC<RightPanelProps> = ({ children }) => {
  const { rightPanelCollapsed, toggleRightPanel } = useLayoutStore();

  return (
    <Panel
      collapsed={rightPanelCollapsed}
      onToggle={toggleRightPanel}
      side="right"
      title="Explainability"
    >
      {children || (
        <div className="p-4 text-sm text-muted-foreground">
          Right panel content will be implemented in Story 4.4
        </div>
      )}
    </Panel>
  );
};

