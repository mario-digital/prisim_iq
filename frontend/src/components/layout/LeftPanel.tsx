'use client';

import type { FC, ReactNode } from 'react';
import { Panel } from './Panel';
import { useLayoutStore } from '@/stores/layoutStore';
import { ContextPanel } from '@/components/context';

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
      {children || <ContextPanel />}
    </Panel>
  );
};

