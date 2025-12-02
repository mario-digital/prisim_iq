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
        'flex-1 flex flex-col min-w-0 bg-background',
        className
      )}
    >
      {children || <ChatPanel />}
    </main>
  );
};
