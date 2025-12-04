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
        'relative flex flex-col border-border/40 bg-card/50 backdrop-blur-sm transition-all duration-300 ease-in-out',
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
          'absolute top-3 z-10 h-6 w-6 rounded-full border border-border/50 bg-card shadow-lg shadow-black/20 hover:bg-accent hover:border-cyan-500/30 transition-all duration-200',
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
          <div className="flex-shrink-0 border-b border-border/30 px-4 py-3 bg-gradient-to-r from-transparent via-cyan-500/5 to-transparent">
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

