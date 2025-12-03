'use client';

import type { FC } from 'react';
import { Lightbulb } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { useStatusStore } from '@/stores/statusStore';

/**
 * Toggle button for Honeywell mapping overlay.
 * Shows 💡 icon, highlights when overlay is active.
 * Full overlay implementation in Story 4.8.
 */
export const HoneywellToggle: FC = () => {
  const { honeywellOverlayVisible, toggleHoneywellOverlay } = useStatusStore();

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={toggleHoneywellOverlay}
      className={cn(
        'h-8 w-8 p-0 transition-colors',
        honeywellOverlayVisible && 'bg-amber-100 text-amber-700 hover:bg-amber-200'
      )}
      title={honeywellOverlayVisible ? 'Hide Honeywell mapping' : 'Show Honeywell mapping'}
      aria-pressed={honeywellOverlayVisible}
    >
      <Lightbulb className="h-4 w-4" />
      <span className="sr-only">
        {honeywellOverlayVisible ? 'Hide' : 'Show'} Honeywell mapping overlay
      </span>
    </Button>
  );
};


