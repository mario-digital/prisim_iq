'use client';

import type { FC } from 'react';
import { cn } from '@/lib/utils';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface ProfitUpliftHeroProps {
  /** Profit uplift percentage */
  value: number;
  /** Baseline price for comparison */
  baseline: number;
}

export const ProfitUpliftHero: FC<ProfitUpliftHeroProps> = ({
  value,
  baseline,
}) => {
  const isPositive = value > 0;
  const TrendIcon = isPositive ? TrendingUp : TrendingDown;

  return (
    <div className="text-center py-8">
      <p className="text-sm text-muted-foreground uppercase tracking-wide font-medium">
        Total Profit Uplift
      </p>
      <div className="flex items-center justify-center gap-3 mt-2">
        <TrendIcon
          className={cn(
            'h-10 w-10',
            isPositive ? 'text-green-500' : 'text-red-500'
          )}
        />
        <p
          className={cn(
            'text-7xl font-bold tabular-nums',
            isPositive ? 'text-green-500' : 'text-red-500'
          )}
        >
          {isPositive ? '+' : ''}
          {value.toFixed(1)}%
        </p>
      </div>
      <p className="text-sm text-muted-foreground mt-3">
        vs. ${baseline.toFixed(2)} baseline pricing
      </p>
    </div>
  );
};

