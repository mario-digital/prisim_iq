'use client';

import type { FC, ReactNode } from 'react';
import { Panel } from './Panel';
import { useLayoutStore } from '@/stores/layoutStore';
import { ExplainabilityPanel } from '@/components/visualizations';

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
      {children || <ExplainabilityPanel />}
    </Panel>
  );
};

