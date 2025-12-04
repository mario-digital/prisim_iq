'use client';

import type { FC } from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface StreamErrorProps {
  error: string;
  onRetry?: () => void;
  showRetry?: boolean;
}

/**
 * Displays stream error with optional retry button.
 * Used when SSE connection fails or stream is interrupted.
 */
export const StreamError: FC<StreamErrorProps> = ({
  error,
  onRetry,
  showRetry = true,
}) => {
  return (
    <div className="flex items-center gap-3 p-3 bg-destructive/10 border border-destructive/20 rounded-lg text-sm animate-in fade-in slide-in-from-bottom-2 duration-300">
      <div className="flex-shrink-0 text-destructive">
        <AlertCircle className="h-5 w-5" />
      </div>
      <div className="flex-1">
        <p className="font-medium text-destructive">Connection Error</p>
        <p className="text-muted-foreground text-xs mt-0.5">{error}</p>
      </div>
      {showRetry && onRetry && (
        <Button
          variant="outline"
          size="sm"
          onClick={onRetry}
          className="flex-shrink-0"
        >
          <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
          Retry
        </Button>
      )}
    </div>
  );
};

