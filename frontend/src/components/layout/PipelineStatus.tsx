'use client';

import type { FC } from 'react';
import { Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useStatusStore, PIPELINE_STAGES } from '@/stores/statusStore';

/**
 * Pipeline status indicator showing processing stages.
 * Stages: Context → ML → Optimize → Price
 * Modern, minimal design with animated stages.
 */
export const PipelineStatus: FC = () => {
  const { currentStage, isProcessing, completedStages } = useStatusStore();

  return (
    <div className="flex items-center gap-1">
      {PIPELINE_STAGES.map((stage, index) => {
        const isActive = currentStage === index && isProcessing;
        const isCompleted = completedStages.includes(index);
        const isPending = currentStage < index || currentStage === -1;

        return (
          <div key={stage} className="flex items-center">
            {/* Stage indicator */}
            <div
              className={cn(
                'flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium transition-all duration-300',
                isActive && 'bg-cyan-500/15 text-cyan-400 ring-1 ring-cyan-500/30',
                isCompleted && 'bg-emerald-500/15 text-emerald-400',
                isPending && !isActive && 'text-muted-foreground/50'
              )}
            >
              {isCompleted && (
                <Check className="h-3 w-3" />
              )}
              {isActive && (
                <span className="relative flex h-1.5 w-1.5">
                  <span className="absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75 animate-ping" />
                  <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-cyan-400" />
                </span>
              )}
              {stage}
            </div>

            {/* Connector line */}
            {index < PIPELINE_STAGES.length - 1 && (
              <div
                className={cn(
                  'w-4 h-px mx-0.5 transition-colors duration-300',
                  isCompleted ? 'bg-emerald-500/50' : 'bg-border/30'
                )}
              />
            )}
          </div>
        );
      })}
    </div>
  );
};
