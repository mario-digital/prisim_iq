'use client';

import type { FC } from 'react';
import { Database, Clock, Cpu } from 'lucide-react';
import { useStatusStore } from '@/stores/statusStore';

/**
 * Footer component displaying current session stats.
 * Shows: Current Segment, Model Status, Last Response Time.
 * Updates after each recommendation via statusStore.
 */
export const Footer: FC = () => {
  const { currentSegment, modelsReady, totalModels, lastResponseTime } = useStatusStore();

  return (
    <footer className="h-10 border-t border-border bg-card px-4 flex items-center justify-between">
      {/* Left: Segment */}
      <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
        <Database className="h-3.5 w-3.5" />
        <span>Segment:</span>
        <span className="font-medium text-foreground">
          {currentSegment || 'None'}
        </span>
      </div>

      {/* Center: Models Status */}
      <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
        <Cpu className="h-3.5 w-3.5" />
        <span>Models:</span>
        <span className="font-medium text-foreground">
          {modelsReady}/{totalModels} Ready
        </span>
      </div>

      {/* Right: Response Time */}
      <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
        <Clock className="h-3.5 w-3.5" />
        <span>Last Response:</span>
        <span className="font-medium text-foreground">
          {lastResponseTime !== null ? `${lastResponseTime.toFixed(1)}s` : '—'}
        </span>
      </div>
    </footer>
  );
};
