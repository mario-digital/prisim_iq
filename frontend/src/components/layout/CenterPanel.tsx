'use client';

import type { FC, ReactNode } from 'react';
import { cn } from '@/lib/utils';

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
      {children || (
        <div className="flex-1 flex items-center justify-center p-4 text-sm text-muted-foreground">
          Center panel content will be implemented in Story 4.3
        </div>
      )}
    </main>
  );
};

