'use client';

import type { FC } from 'react';
import { Brand } from './Brand';
import { PipelineStatus } from './PipelineStatus';
import { SystemStatus } from './SystemStatus';
import { HoneywellToggle } from './HoneywellToggle';

/**
 * Main header component for PrismIQ application.
 * Contains: Brand, Pipeline Status, System Status, Honeywell Toggle.
 * Tab navigation is rendered separately below header (via TabNavigation).
 */
export const Header: FC = () => {
  return (
    <header className="h-14 border-b border-border bg-card px-4 flex items-center justify-between">
      {/* Left: Brand */}
      <Brand />

      {/* Center: Pipeline Status */}
      <div className="flex items-center">
        <PipelineStatus />
      </div>

      {/* Right: System Status + Honeywell Toggle */}
      <div className="flex items-center gap-3">
        <SystemStatus />
        <HoneywellToggle />
      </div>
    </header>
  );
};
