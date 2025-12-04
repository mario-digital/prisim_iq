'use client';

import type { FC, ReactNode } from 'react';
import { cn } from '@/lib/utils';
import { ChatPanel } from '@/components/chat';

interface CenterPanelProps {
  children?: ReactNode;
  className?: string;
}

export const CenterPanel: FC<CenterPanelProps> = ({ children, className }) => {
  return (
    <main
      className={cn(
        'flex-1 flex flex-col items-center min-w-0 min-h-0 bg-background overflow-hidden',
        className
      )}
    >
      <div className="w-full max-w-4xl h-full flex flex-col">
        {children || <ChatPanel />}
      </div>
    </main>
  );
};
