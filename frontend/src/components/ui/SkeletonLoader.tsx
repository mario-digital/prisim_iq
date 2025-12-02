'use client';

import type { FC } from 'react';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';

interface SkeletonLoaderProps {
  variant?: 'panel' | 'card' | 'chat' | 'list';
  className?: string;
}

export const SkeletonLoader: FC<SkeletonLoaderProps> = ({
  variant = 'card',
  className,
}) => {
  if (variant === 'panel') {
    return (
      <div className={cn('p-4 space-y-4', className)}>
        <Skeleton className="h-6 w-3/4" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-5/6" />
        <div className="space-y-2 pt-4">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
        </div>
      </div>
    );
  }

  if (variant === 'chat') {
    return (
      <div className={cn('p-4 space-y-4', className)}>
        {/* User message skeleton */}
        <div className="flex justify-end">
          <Skeleton className="h-16 w-3/4 rounded-lg" />
        </div>
        {/* Assistant message skeleton */}
        <div className="flex justify-start">
          <Skeleton className="h-24 w-4/5 rounded-lg" />
        </div>
        {/* User message skeleton */}
        <div className="flex justify-end">
          <Skeleton className="h-12 w-2/3 rounded-lg" />
        </div>
      </div>
    );
  }

  if (variant === 'list') {
    return (
      <div className={cn('space-y-3', className)}>
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="flex items-center gap-3 p-2">
            <Skeleton className="h-10 w-10 rounded-full" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-1/2" />
              <Skeleton className="h-3 w-3/4" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  // Default: card variant
  return (
    <div className={cn('p-4 space-y-3', className)}>
      <Skeleton className="h-8 w-1/2" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-4/5" />
      <Skeleton className="h-32 w-full" />
    </div>
  );
};

