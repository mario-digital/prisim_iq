'use client';

import type { FC } from 'react';
import { Factory } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { useLayoutStore } from '@/stores/layoutStore';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

/**
 * Toggle button for Honeywell mapping overlay.
 * Shows Factory icon, highlights when overlay is active.
 */
export const HoneywellToggle: FC = () => {
  const { isHoneywellOpen, toggleHoneywell } = useLayoutStore();

  return (
    <TooltipProvider delayDuration={200}>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleHoneywell}
            className={cn(
              'h-8 px-3 gap-2 transition-all duration-200',
              isHoneywellOpen
                ? 'bg-gradient-to-r from-orange-500/20 to-amber-500/15 text-orange-600 dark:text-orange-400 shadow-sm shadow-orange-500/15'
                : 'text-muted-foreground hover:text-foreground'
            )}
            aria-pressed={isHoneywellOpen}
          >
            <Factory className="h-4 w-4" />
            <span className="text-xs font-medium hidden sm:inline">Honeywell</span>
          </Button>
        </TooltipTrigger>
        <TooltipContent>
          <p className="text-xs">
            {isHoneywellOpen ? 'Hide' : 'Show'} Honeywell enterprise mapping
          </p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};
