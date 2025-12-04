'use client';

import type { FC } from 'react';
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
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
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
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="mr-1.5"
          >
            <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
            <path d="M3 3v5h5" />
            <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" />
            <path d="M16 21h5v-5" />
          </svg>
          Retry
        </Button>
      )}
    </div>
  );
};

