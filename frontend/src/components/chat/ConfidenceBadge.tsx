'use client';

import type { FC } from 'react';
import { cn } from '@/lib/utils';

interface ConfidenceBadgeProps {
  value: number;
  className?: string;
}

/**
 * Displays confidence score as a colored badge.
 * High (>=80%): green, Medium (50-79%): yellow, Low (<50%): red
 */
export const ConfidenceBadge: FC<ConfidenceBadgeProps> = ({ value, className }) => {
  const percentage = Math.round(value * 100);
  
  const colorClass = percentage >= 80
    ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400'
    : percentage >= 50
    ? 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400'
    : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';

  return (
    <span
      className={cn(
        'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium',
        colorClass,
        className
      )}
      title={`Confidence: ${percentage}%`}
    >
      {percentage}% confident
    </span>
  );
};

