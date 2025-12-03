'use client';

import { type FC } from 'react';
import { cn } from '@/lib/utils';

interface LegendItem {
  /** Label text */
  label: string;
  /** Color for the indicator */
  color: string;
  /** Shape of the indicator */
  shape?: 'circle' | 'square' | 'line';
}

interface ChartLegendProps {
  /** Legend items to display */
  items: LegendItem[];
  /** Position of the legend */
  position?: 'top' | 'bottom' | 'center';
  /** Additional CSS classes */
  className?: string;
}

/**
 * Custom legend component for consistent styling across all charts.
 * Supports different indicator shapes for various chart types.
 */
export const ChartLegend: FC<ChartLegendProps> = ({
  items,
  position = 'bottom',
  className,
}) => {
  const getIndicatorClass = (shape: LegendItem['shape'] = 'circle') => {
    switch (shape) {
      case 'square':
        return 'w-3 h-3 rounded-sm';
      case 'line':
        return 'w-4 h-0.5 rounded-full';
      default:
        return 'w-3 h-3 rounded-full';
    }
  };

  return (
    <div
      className={cn(
        'flex flex-wrap gap-4 text-xs',
        position === 'center' && 'justify-center',
        position === 'bottom' && 'justify-center mt-2',
        position === 'top' && 'justify-center mb-2',
        className
      )}
    >
      {items.map((item, index) => (
        <div
          key={`legend-${index}`}
          className="flex items-center gap-1.5"
        >
          <span
            className={getIndicatorClass(item.shape)}
            style={{ backgroundColor: item.color }}
          />
          <span className="text-muted-foreground">{item.label}</span>
        </div>
      ))}
    </div>
  );
};

