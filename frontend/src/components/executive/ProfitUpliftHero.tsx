'use client';

import type { FC } from 'react';
import { cn } from '@/lib/utils';
import { TrendingUp, TrendingDown, DollarSign, Target } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

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
  const optimizedPrice = baseline * (1 + value / 100);

  return (
    <Card className="border border-border/30 bg-gradient-to-br from-card via-card to-emerald-950/20 shadow-lg shadow-black/10">
      <CardContent className="p-6">
        <div className="flex items-center justify-between gap-6">
          {/* Main uplift metric */}
          <div className="flex items-center gap-4">
            <div
              className={cn(
                'flex items-center justify-center h-14 w-14 rounded-xl shadow-lg',
                isPositive
                  ? 'bg-emerald-500/20 text-emerald-400 shadow-emerald-500/20'
                  : 'bg-rose-500/20 text-rose-400 shadow-rose-500/20'
              )}
            >
              <TrendIcon className="h-7 w-7" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wide font-medium">
                Profit Uplift
              </p>
              <p
                className={cn(
                  'text-3xl font-bold tabular-nums',
                  isPositive ? 'text-emerald-400' : 'text-rose-400'
                )}
              >
                {isPositive ? '+' : ''}
                {value.toFixed(1)}%
              </p>
            </div>
          </div>

          {/* Divider */}
          <div className="h-12 w-px bg-border/30" />

          {/* Baseline */}
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-slate-500/20 text-slate-400">
              <DollarSign className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Baseline</p>
              <p className="text-lg font-semibold tabular-nums text-slate-300">
                ${baseline.toFixed(2)}
              </p>
            </div>
          </div>

          {/* Divider */}
          <div className="h-12 w-px bg-border/30" />

          {/* Optimized */}
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-cyan-500/20 text-cyan-400">
              <Target className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Optimized Avg</p>
              <p className="text-lg font-semibold tabular-nums text-cyan-400">
                ${optimizedPrice.toFixed(2)}
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

