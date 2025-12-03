'use client';

import type { FC } from 'react';
import { Check, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useStatusStore, PIPELINE_STAGES } from '@/stores/statusStore';

/**
 * Pipeline status indicator showing processing stages.
 * Stages: Context → ML → Optimize → Price
 * Shows animation during processing, checkmarks for completed stages.
 */
export const PipelineStatus: FC = () => {
  const { currentStage, isProcessing, completedStages } = useStatusStore();

  return (
    <div className="flex items-center gap-0.5">
      {PIPELINE_STAGES.map((stage, index) => {
        const isActive = currentStage === index && isProcessing;
        const isCompleted = completedStages.includes(index);
        const isPending = currentStage < index || currentStage === -1;

        return (
          <div key={stage} className="flex items-center">
            {/* Stage pill */}
            <div
              className={cn(
                'flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition-all duration-300',
                isActive && 'bg-prism-100 text-prism-700 animate-pulse shadow-sm',
                isCompleted && 'bg-green-100 text-green-700',
                isPending && !isActive && 'bg-muted text-muted-foreground'
              )}
            >
              {isCompleted && (
                <Check className="h-3 w-3" />
              )}
              {stage}
            </div>

            {/* Arrow separator */}
            {index < PIPELINE_STAGES.length - 1 && (
              <ChevronRight 
                className={cn(
                  'h-3 w-3 mx-0.5 transition-colors duration-300',
                  (isCompleted || (isActive && index < currentStage))
                    ? 'text-green-400'
                    : 'text-muted-foreground/50'
                )}
              />
            )}
          </div>
        );
      })}
    </div>
  );
};


