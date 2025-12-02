'use client';

import type { FC, ReactNode } from 'react';
import { Panel } from './Panel';
import { useLayoutStore } from '@/stores/layoutStore';

interface LeftPanelProps {
  children?: ReactNode;
}

export const LeftPanel: FC<LeftPanelProps> = ({ children }) => {
  const { leftPanelCollapsed, toggleLeftPanel } = useLayoutStore();

  return (
    <Panel
      collapsed={leftPanelCollapsed}
      onToggle={toggleLeftPanel}
      side="left"
      title="Market Context"
    >
      {children || (
        <div className="p-4 text-sm text-muted-foreground">
          Left panel content will be implemented in Story 4.2
        </div>
      )}
    </Panel>
  );
};

