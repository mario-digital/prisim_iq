'use client';

import type { FC } from 'react';

/**
 * Animated typing indicator shown while AI is responding.
 */
export const TypingIndicator: FC = () => {
  return (
    <div className="flex items-center gap-1.5 px-4 py-3">
      <div className="flex items-center gap-1">
        <div className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-bounce [animation-delay:-0.3s]" />
        <div className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-bounce [animation-delay:-0.15s]" />
        <div className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-bounce" />
      </div>
      <span className="text-xs text-muted-foreground ml-2">AI is thinking...</span>
    </div>
  );
};

