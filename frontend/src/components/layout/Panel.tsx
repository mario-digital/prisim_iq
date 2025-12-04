'use client';

import type { FC, ReactNode } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

interface PanelProps {
  children: ReactNode;
  collapsed: boolean;
  onToggle: () => void;
  side: 'left' | 'right';
  className?: string;
  /** Panel title - supports string or ReactNode for i18n/icons */
  title?: ReactNode;
}

export const Panel: FC<PanelProps> = ({
  children,
  collapsed,
  onToggle,
  side,
  className,
  title,
}) => {
  const isLeft = side === 'left';

  return (
    <aside
      className={cn(
        'relative flex flex-col border-border bg-card transition-all duration-300 ease-in-out',
        isLeft ? 'border-r' : 'border-l',
        collapsed ? 'w-12' : 'w-1/4 min-w-[280px]',
        className
      )}
    >
      {/* Toggle Button */}
      <Button
        variant="ghost"
        size="icon"
        onClick={onToggle}
        className={cn(
          'absolute top-3 z-10 h-6 w-6 rounded-full border bg-background shadow-sm hover:bg-muted',
          isLeft ? '-right-3' : '-left-3'
        )}
        aria-label={collapsed ? 'Expand panel' : 'Collapse panel'}
      >
        {isLeft ? (
          collapsed ? (
            <ChevronRight className="h-3 w-3" />
          ) : (
            <ChevronLeft className="h-3 w-3" />
          )
        ) : collapsed ? (
          <ChevronLeft className="h-3 w-3" />
        ) : (
          <ChevronRight className="h-3 w-3" />
        )}
      </Button>

      {/* Panel Content */}
      <div
        className={cn(
          'flex-1 flex flex-col min-h-0 transition-opacity duration-300',
          collapsed ? 'opacity-0' : 'opacity-100'
        )}
      >
        {title && !collapsed && (
          <div className="flex-shrink-0 border-b border-border px-4 py-3">
            <h2 className="text-sm font-semibold text-foreground">{title}</h2>
          </div>
        )}
        <div className={cn('flex-1 min-h-0 overflow-y-auto', collapsed ? 'invisible' : 'visible')}>
          {children}
        </div>
      </div>

      {/* Collapsed State Indicator */}
      {collapsed && (
        <div className="flex flex-1 items-center justify-center">
          <span
            className="text-xs font-medium text-muted-foreground"
            style={{ writingMode: 'vertical-rl', textOrientation: 'mixed' }}
          >
            {title}
          </span>
        </div>
      )}
    </aside>
  );
};

