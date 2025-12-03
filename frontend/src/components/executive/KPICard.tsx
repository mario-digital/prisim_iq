'use client';

import type { FC, ReactNode } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface KPICardProps {
  /** Title of the KPI */
  title: string;
  /** Main value to display */
  value: string | number;
  /** Optional subtitle text */
  subtitle?: string;
  /** Optional icon */
  icon?: ReactNode;
  /** Trend direction */
  trend?: 'up' | 'down' | 'neutral';
  /** Color variant for the value */
  variant?: 'default' | 'success' | 'warning' | 'danger';
}

export const KPICard: FC<KPICardProps> = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  variant = 'default',
}) => {
  const TrendIcon =
    trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus;

  const valueColors = {
    default: 'text-foreground',
    success: 'text-green-500',
    warning: 'text-yellow-500',
    danger: 'text-red-500',
  };

  const trendColors = {
    up: 'text-green-500',
    down: 'text-red-500',
    neutral: 'text-muted-foreground',
  };

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center gap-2">
          {icon && <span className="text-muted-foreground">{icon}</span>}
          <span className="text-sm text-muted-foreground font-medium">
            {title}
          </span>
        </div>
        <div className="flex items-center gap-2 mt-2">
          <p className={cn('text-2xl font-bold', valueColors[variant])}>
            {value}
          </p>
          {trend && (
            <TrendIcon className={cn('h-4 w-4', trendColors[trend])} />
          )}
        </div>
        {subtitle && (
          <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
        )}
      </CardContent>
    </Card>
  );
};

