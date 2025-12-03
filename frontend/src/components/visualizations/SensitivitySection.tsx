'use client';

import { useState, type FC } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import type { SensitivityResult } from './types';

interface SensitivitySectionProps {
  sensitivity: SensitivityResult;
}

/**
 * Expandable section showing sensitivity analysis with confidence bands.
 * Displays robustness score and price range visualization.
 */
export const SensitivitySection: FC<SensitivitySectionProps> = ({
  sensitivity,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getRobustnessColor = (score: number) => {
    if (score >= 0.8) return 'text-emerald-600 dark:text-emerald-400';
    if (score >= 0.5) return 'text-amber-600 dark:text-amber-400';
    return 'text-red-600 dark:text-red-400';
  };

  const getRobustnessLabel = (score: number) => {
    if (score >= 0.8) return 'High';
    if (score >= 0.5) return 'Medium';
    return 'Low';
  };

  const priceRange = sensitivity.upperBound - sensitivity.lowerBound;

  return (
    <Card>
      <CardHeader className="pb-2">
        <button
          type="button"
          onClick={() => setIsExpanded(!isExpanded)}
          aria-expanded={isExpanded}
          aria-label={`${isExpanded ? 'Collapse' : 'Expand'} sensitivity analysis details`}
          className="w-full flex items-center justify-between text-left"
        >
          <CardTitle className="text-sm font-medium">
            Sensitivity Analysis
          </CardTitle>
          <div className="flex items-center gap-2">
            <span
              className={cn(
                'text-sm font-semibold',
                getRobustnessColor(sensitivity.robustnessScore)
              )}
            >
              {getRobustnessLabel(sensitivity.robustnessScore)} Robustness
            </span>
            <span
              className={cn(
                'text-muted-foreground transition-transform',
                isExpanded && 'rotate-180'
              )}
            >
              ▼
            </span>
          </div>
        </button>
      </CardHeader>

      <CardContent className={cn('space-y-4', !isExpanded && 'pb-2')}>
        {/* Summary - always visible */}
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="p-2 rounded-lg bg-muted/50">
            <div className="text-xs text-muted-foreground">Lower Bound</div>
            <div className="text-sm font-semibold">
              ${sensitivity.lowerBound.toFixed(2)}
            </div>
          </div>
          <div className="p-2 rounded-lg bg-primary/10">
            <div className="text-xs text-muted-foreground">Recommended</div>
            <div className="text-sm font-semibold text-primary">
              ${sensitivity.basePrice.toFixed(2)}
            </div>
          </div>
          <div className="p-2 rounded-lg bg-muted/50">
            <div className="text-xs text-muted-foreground">Upper Bound</div>
            <div className="text-sm font-semibold">
              ${sensitivity.upperBound.toFixed(2)}
            </div>
          </div>
        </div>

        {/* Expanded content */}
        {isExpanded && (
          <>
            {/* Robustness details */}
            <div className="flex justify-between items-center p-3 rounded-lg bg-muted/30">
              <div>
                <div className="text-xs text-muted-foreground">
                  Robustness Score
                </div>
                <div
                  className={cn(
                    'text-lg font-semibold',
                    getRobustnessColor(sensitivity.robustnessScore)
                  )}
                >
                  {(sensitivity.robustnessScore * 100).toFixed(0)}%
                </div>
              </div>
              <div className="text-right">
                <div className="text-xs text-muted-foreground">
                  Confidence Level
                </div>
                <div className="text-sm font-medium">
                  {sensitivity.confidenceLevel}%
                </div>
              </div>
              <div className="text-right">
                <div className="text-xs text-muted-foreground">Price Range</div>
                <div className="text-sm font-medium">
                  ±${(priceRange / 2).toFixed(2)}
                </div>
              </div>
            </div>

            {/* Confidence band chart */}
            {sensitivity.pricePoints.length > 0 && (
              <div>
                <div className="text-xs text-muted-foreground mb-2">
                  Confidence Band Visualization
                </div>
                <ResponsiveContainer width="100%" height={150}>
                  <AreaChart
                    data={sensitivity.pricePoints}
                    margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
                  >
                    <defs>
                      <linearGradient
                        id="sensitivityGradient"
                        x1="0"
                        y1="0"
                        x2="0"
                        y2="1"
                      >
                        <stop
                          offset="5%"
                          stopColor="#6366f1"
                          stopOpacity={0.3}
                        />
                        <stop
                          offset="95%"
                          stopColor="#6366f1"
                          stopOpacity={0.05}
                        />
                      </linearGradient>
                    </defs>

                    <XAxis
                      dataKey="price"
                      tickFormatter={(v) => `$${v}`}
                      fontSize={11}
                      tickLine={false}
                    />
                    <YAxis
                      tickFormatter={(v) => v.toFixed(0)}
                      fontSize={11}
                      tickLine={false}
                      axisLine={false}
                    />
                    <Tooltip
                      formatter={(value: number) => [
                        value.toFixed(2),
                        'Expected Value',
                      ]}
                      labelFormatter={(label) => `Price: $${label}`}
                      contentStyle={{
                        backgroundColor: 'hsl(var(--card))',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px',
                        fontSize: '12px',
                      }}
                    />

                    {/* Lower bound reference */}
                    <ReferenceLine
                      x={sensitivity.lowerBound}
                      stroke="#94a3b8"
                      strokeDasharray="4 4"
                    />

                    {/* Upper bound reference */}
                    <ReferenceLine
                      x={sensitivity.upperBound}
                      stroke="#94a3b8"
                      strokeDasharray="4 4"
                    />

                    {/* Base price reference */}
                    <ReferenceLine
                      x={sensitivity.basePrice}
                      stroke="#3b82f6"
                      strokeWidth={2}
                    />

                    <Area
                      type="monotone"
                      dataKey="value"
                      stroke="#6366f1"
                      strokeWidth={2}
                      fill="url(#sensitivityGradient)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Interpretation */}
            <div className="text-xs text-muted-foreground p-3 rounded-lg bg-muted/30">
              <strong>Interpretation:</strong>{' '}
              {sensitivity.robustnessScore >= 0.8 ? (
                <>
                  The recommended price is highly stable. Demand remains
                  consistent within the ${priceRange.toFixed(2)} price range.
                </>
              ) : sensitivity.robustnessScore >= 0.5 ? (
                <>
                  The recommended price shows moderate sensitivity. Consider
                  monitoring demand closely if adjusting price.
                </>
              ) : (
                <>
                  The recommended price is sensitive to changes. Small
                  adjustments may significantly impact demand.
                </>
              )}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
};

