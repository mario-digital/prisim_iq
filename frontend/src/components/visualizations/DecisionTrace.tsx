'use client';

import { useState, type FC } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import type { DecisionStep } from './types';

interface DecisionTraceProps {
  steps: DecisionStep[];
}

/**
 * Collapsible accordion showing the decision pipeline steps.
 * Each step shows timing, status, inputs, and outputs.
 */
export const DecisionTrace: FC<DecisionTraceProps> = ({ steps }) => {
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());

  const toggleStep = (stepId: string) => {
    setExpandedSteps((prev) => {
      const next = new Set(prev);
      if (next.has(stepId)) {
        next.delete(stepId);
      } else {
        next.add(stepId);
      }
      return next;
    });
  };

  const getStatusColor = (status: DecisionStep['status']): string => {
    switch (status) {
      case 'success':
        return 'bg-emerald-500';
      case 'warning':
        return 'bg-amber-500';
      case 'error':
        return 'bg-red-500';
      default: {
        // Exhaustive check - this should never be reached if types are correct
        const _exhaustiveCheck: never = status;
        console.warn(`[DecisionTrace] Unexpected status value: ${_exhaustiveCheck}`);
        return 'bg-gray-500';
      }
    }
  };

  const getStatusIcon = (status: DecisionStep['status']): string => {
    switch (status) {
      case 'success':
        return '✓';
      case 'warning':
        return '!';
      case 'error':
        return '✗';
      default: {
        // Exhaustive check - this should never be reached if types are correct
        const _exhaustiveCheck: never = status;
        console.warn(`[DecisionTrace] Unexpected status value: ${_exhaustiveCheck}`);
        return '?';
      }
    }
  };

  const totalDuration = steps.reduce((sum, step) => sum + step.durationMs, 0);

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium">Decision Trace</CardTitle>
          <span className="text-xs text-muted-foreground">
            Total: {totalDuration.toFixed(0)}ms
          </span>
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        {steps.length === 0 ? (
          <div className="text-sm text-muted-foreground text-center py-4">
            No decision trace available
          </div>
        ) : (
          steps.map((step, index) => {
            const isExpanded = expandedSteps.has(step.id);

            return (
              <div
                key={step.id}
                className="border rounded-lg overflow-hidden"
              >
                {/* Step header - clickable */}
                <button
                  type="button"
                  onClick={() => toggleStep(step.id)}
                  aria-expanded={isExpanded}
                  aria-label={`${isExpanded ? 'Collapse' : 'Expand'} step ${index + 1}: ${step.name}`}
                  className={cn(
                    'w-full flex items-center gap-3 p-3 text-left',
                    'hover:bg-muted/50 transition-colors',
                    isExpanded && 'bg-muted/30'
                  )}
                >
                  {/* Step number and status */}
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground w-4">
                      {index + 1}.
                    </span>
                    <div
                      className={cn(
                        'w-5 h-5 rounded-full flex items-center justify-center text-white text-xs font-medium',
                        getStatusColor(step.status)
                      )}
                    >
                      {getStatusIcon(step.status)}
                    </div>
                  </div>

                  {/* Step name and description */}
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium truncate">
                      {step.name.replace(/_/g, ' ')}
                    </div>
                    <div className="text-xs text-muted-foreground truncate">
                      {step.description}
                    </div>
                  </div>

                  {/* Duration */}
                  <span className="text-xs text-muted-foreground shrink-0">
                    {step.durationMs.toFixed(0)}ms
                  </span>

                  {/* Expand indicator */}
                  <span
                    className={cn(
                      'text-muted-foreground transition-transform',
                      isExpanded && 'rotate-180'
                    )}
                  >
                    ▼
                  </span>
                </button>

                {/* Expanded content */}
                {isExpanded && (
                  <div className="p-3 pt-0 border-t bg-muted/20">
                    <div className="grid grid-cols-2 gap-4 mt-3">
                      {/* Inputs */}
                      <div>
                        <h4 className="text-xs font-medium text-muted-foreground mb-2">
                          Inputs
                        </h4>
                        <div className="space-y-1">
                          {Object.entries(step.inputs).map(([key, value]) => (
                            <div key={key} className="text-xs">
                              <span className="text-muted-foreground">
                                {key.replace(/_/g, ' ')}:
                              </span>{' '}
                              <span className="font-mono">
                                {formatValue(value)}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Outputs */}
                      <div>
                        <h4 className="text-xs font-medium text-muted-foreground mb-2">
                          Outputs
                        </h4>
                        <div className="space-y-1">
                          {Object.entries(step.outputs).map(([key, value]) => (
                            <div key={key} className="text-xs">
                              <span className="text-muted-foreground">
                                {key.replace(/_/g, ' ')}:
                              </span>{' '}
                              <span className="font-mono">
                                {formatValue(value)}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </CardContent>
    </Card>
  );
};

/**
 * Format a value for display in the trace.
 */
function formatValue(value: unknown): string {
  if (value === null || value === undefined) {
    return 'null';
  }
  if (typeof value === 'number') {
    return Number.isInteger(value) ? value.toString() : value.toFixed(2);
  }
  if (typeof value === 'boolean') {
    return value ? 'true' : 'false';
  }
  if (typeof value === 'string') {
    const formatted = value.replace(/_/g, ' ');
    return formatted.length > 30 ? `${formatted.slice(0, 30)}...` : formatted;
  }
  if (Array.isArray(value)) {
    return `[${value.length} items]`;
  }
  if (typeof value === 'object') {
    return '{...}';
  }
  return String(value);
}

