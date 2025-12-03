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
  const priceChangePercent = ((priceChange / result.basePrice) * 100);

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          Recommended Price
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Main price display */}
        <div className="text-4xl font-bold text-primary tracking-tight">
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
              priceChange > 0 ? 'text-emerald-600' : priceChange < 0 ? 'text-red-600' : 'text-muted-foreground'
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
                  ? 'text-emerald-600 dark:text-emerald-400'
                  : profitUpliftPercent < 0
                  ? 'text-red-600 dark:text-red-400'
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
            <span className="text-lg font-semibold">
              {result.expectedDemand.toFixed(0)} units
            </span>
          </div>
        </div>

        {/* Segment badge */}
        <div className="mt-4 pt-4 border-t">
          <span className="text-xs text-muted-foreground">Segment: </span>
          <span className="text-xs font-medium capitalize">
            {result.segment.replace('_', ' ')}
          </span>
        </div>
      </CardContent>
    </Card>
  );
};

