'use client';

import type { FC } from 'react';

interface ToolCallIndicatorProps {
  toolName: string;
}

/**
 * Human-readable labels for tool calls.
 */
const TOOL_LABELS: Record<string, string> = {
  optimize_price: '💰 Calculating optimal price...',
  explain_decision: '🔍 Analyzing decision factors...',
  sensitivity_analysis: '📊 Running sensitivity analysis...',
  get_segment: '📦 Identifying customer segment...',
  get_evidence: '📋 Fetching evidence data...',
};

/**
 * Displays an animated indicator when the AI agent invokes a backend tool.
 * Shows during tool execution and collapses when complete.
 */
export const ToolCallIndicator: FC<ToolCallIndicatorProps> = ({ toolName }) => {
  const label = TOOL_LABELS[toolName] || `🔧 Calling ${toolName}...`;

  return (
    <div className="flex items-center gap-2 text-sm text-muted-foreground py-2 px-3 bg-muted/50 rounded-lg animate-in fade-in slide-in-from-left-2 duration-300">
      {/* Spinning loader */}
      <div
        className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full tool-spinner"
        role="status"
        aria-label="Tool executing"
      />
      <span>{label}</span>
    </div>
  );
};

