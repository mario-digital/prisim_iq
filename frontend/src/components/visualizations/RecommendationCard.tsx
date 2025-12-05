'use client';

import type { FC } from 'react';
import type { PricingResult } from '@prismiq/shared';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ConfidenceBadge } from '@/components/chat/ConfidenceBadge';
import { cn } from '@/lib/utils';

interface RecommendationCardProps {
  result: PricingResult;
  profitUpliftPercent: number;
}

/**
 * Displays the recommended price with confidence and profit uplift.
 * This is the primary summary card shown at the top of explainability panel.
 */
export const RecommendationCard: FC<RecommendationCardProps> = ({
  result,
  profitUpliftPercent,
}) => {
  const priceChange = result.recommendedPrice - result.basePrice;
  // Guard against division by zero - if basePrice is 0, show 0% change
  const priceChangePercent = result.basePrice > 0
    ? ((priceChange / result.basePrice) * 100)
    : 0;

  return (
    <Card className="bg-gradient-to-br from-card to-card/80 border-border/50 shadow-lg shadow-black/10">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          Recommended Price
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Main price display with gradient */}
        <div className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent tracking-tight">
          ${result.recommendedPrice.toFixed(2)}
        </div>

        {/* Price change from base */}
        <div className="flex items-center gap-2 mt-1">
          <span className="text-sm text-muted-foreground">
            Base: ${result.basePrice.toFixed(2)}
          </span>
          <span
            className={cn(
              'text-sm font-medium',
              priceChange > 0 ? 'text-emerald-400' : priceChange < 0 ? 'text-rose-400' : 'text-muted-foreground'
            )}
          >
            ({priceChange > 0 ? '+' : ''}
            {priceChangePercent.toFixed(1)}%)
          </span>
        </div>

        {/* Metrics row */}
        <div className="flex flex-wrap gap-4 mt-4">
          {/* Confidence */}
          <div className="flex flex-col gap-1">
            <span className="text-xs text-muted-foreground">Confidence</span>
            <ConfidenceBadge value={result.confidenceScore} />
          </div>

          {/* Profit Uplift */}
          <div className="flex flex-col gap-1">
            <span className="text-xs text-muted-foreground">Profit Uplift</span>
            <span
              className={cn(
                'text-lg font-semibold',
                profitUpliftPercent > 0
                  ? 'text-emerald-400'
                  : profitUpliftPercent < 0
                  ? 'text-rose-400'
                  : 'text-muted-foreground'
              )}
            >
              {profitUpliftPercent > 0 ? '+' : ''}
              {profitUpliftPercent.toFixed(1)}%
            </span>
          </div>

          {/* Expected Demand */}
          <div className="flex flex-col gap-1">
            <span className="text-xs text-muted-foreground">Expected Demand</span>
            <span className="text-lg font-semibold text-amber-400">
              {result.expectedDemand.toFixed(2)} units
            </span>
          </div>
        </div>

        {/* Segment badge */}
        <div className="mt-4 pt-4 border-t border-border/30">
          <span className="text-xs text-muted-foreground">Segment: </span>
          <span className="text-xs font-medium capitalize text-cyan-400/80">
            {result.segment.replace(/_/g, ' ')}
          </span>
        </div>
      </CardContent>
    </Card>
  );
};

