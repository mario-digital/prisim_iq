'use client';

import { memo, type FC } from 'react';
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
import {
  chartColors,
  chartConfig,
  tooltipStyle,
  animationProps,
} from '@/lib/chartTheme';
import type { CurvePoint } from './types';

/**
 * Data point for sensitivity band visualization (scenario-based).
 */
export interface SensitivityBandPoint {
  /** Scenario label or price point */
  scenario: string | number;
  /** Central price value */
  price: number;
  /** Minimum price in band */
  minPrice: number;
  /** Maximum price in band */
  maxPrice: number;
}

interface SensitivityBandChartProps {
  /** Array of sensitivity band data points (scenario-based format) */
  data?: SensitivityBandPoint[];
  /** Alternative: Array of curve points (price vs value format) */
  curveData?: CurvePoint[];
  /** Base price for reference line */
  basePrice: number;
  /** Lower confidence bound */
  lowerBound?: number;
  /** Upper confidence bound */
  upperBound?: number;
  /** Robustness score (0-1) for calculating confidence bands when using curveData */
  robustnessScore?: number;
  /** Whether to show as standalone card or embedded (no card wrapper) */
  embedded?: boolean;
  /** Chart height in pixels */
  height?: number;
}

/**
 * Area chart showing price sensitivity with confidence bands.
 * Supports two data formats:
 * 1. Scenario-based: SensitivityBandPoint[] with explicit min/max per scenario
 * 2. Curve-based: CurvePoint[] with robustnessScore to calculate bands
 * Memoized to prevent unnecessary re-renders.
 */
export const SensitivityBandChart: FC<SensitivityBandChartProps> = memo(
  ({
    data,
    curveData,
    basePrice,
    lowerBound,
    upperBound,
    robustnessScore = 0.8,
    embedded = false,
    height = 200,
  }) => {
    // Determine which data format to use and transform accordingly
    const chartData = (() => {
      if (curveData && curveData.length > 0) {
        // Transform curve data to band format
        // Calculate band width based on robustness (lower robustness = wider bands)
        const bandMultiplier = (1 - robustnessScore) * 0.3;
        return curveData.map((point) => ({
          scenario: point.price,
          price: point.value,
          minPrice: point.value * (1 - bandMultiplier),
          maxPrice: point.value * (1 + bandMultiplier),
        }));
      }
      if (data && data.length > 0) {
        return data;
      }
      return [];
    })();

    const isEmpty = chartData.length === 0;
    const isCurveMode = curveData && curveData.length > 0;

    const chartContent = (
      <>
        {isEmpty ? (
          <div
            className="flex items-center justify-center text-sm text-muted-foreground"
            style={{ height }}
          >
            No sensitivity data available
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={height}>
            <AreaChart data={chartData} margin={chartConfig.margin}>
              <defs>
                <linearGradient
                  id="sensitivityBandGradient"
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop
                    offset="5%"
                    stopColor={chartColors.indigo}
                    stopOpacity={0.3}
                  />
                  <stop
                    offset="95%"
                    stopColor={chartColors.indigo}
                    stopOpacity={0.05}
                  />
                </linearGradient>
              </defs>

              <XAxis
                dataKey="scenario"
                tickFormatter={isCurveMode ? (v) => `$${v}` : undefined}
                fontSize={chartConfig.fontSizeSmall}
                tickLine={false}
              />
              <YAxis
                tickFormatter={(v) => (isCurveMode ? v.toFixed(2) : `$${v}`)}
                fontSize={chartConfig.fontSizeSmall}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip
                formatter={(value: number, name: string) => {
                  const labels: Record<string, string> = {
                    price: isCurveMode ? 'Expected Value' : 'Price',
                    minPrice: 'Min',
                    maxPrice: 'Max',
                  };
                  const formatted = isCurveMode
                    ? value.toFixed(2)
                    : `$${value.toFixed(2)}`;
                  return [formatted, labels[name] || name];
                }}
                labelFormatter={(label) =>
                  isCurveMode ? `Price: $${label}` : `Scenario: ${label}`
                }
                contentStyle={tooltipStyle}
              />

              {/* Confidence band area */}
              <Area
                type="monotone"
                dataKey="maxPrice"
                stroke="transparent"
                fill={chartColors.indigo}
                fillOpacity={0.2}
                {...animationProps}
              />
              <Area
                type="monotone"
                dataKey="minPrice"
                stroke="transparent"
                fill="hsl(var(--card))"
                {...animationProps}
              />

              {/* Central line */}
              <Area
                type="monotone"
                dataKey="price"
                stroke={chartColors.indigo}
                strokeWidth={2}
                fill="none"
                {...animationProps}
              />

              {/* Lower bound reference */}
              {lowerBound !== undefined && (
                <ReferenceLine
                  x={lowerBound}
                  stroke={chartColors.muted}
                  strokeDasharray="4 4"
                  strokeWidth={1}
                />
              )}

              {/* Upper bound reference */}
              {upperBound !== undefined && (
                <ReferenceLine
                  x={upperBound}
                  stroke={chartColors.muted}
                  strokeDasharray="4 4"
                  strokeWidth={1}
                />
              )}

              {/* Base price reference */}
              <ReferenceLine
                x={basePrice}
                stroke={chartColors.primary}
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}

        {/* Legend */}
        {!isEmpty && (
          <div className="flex justify-center gap-4 mt-2 text-xs">
            <div className="flex items-center gap-1.5">
              <div
                className="w-4 h-0.5 rounded"
                style={{ backgroundColor: chartColors.indigo }}
              />
              <span className="text-muted-foreground">
                {isCurveMode ? 'Expected Value' : 'Price'}
              </span>
            </div>
            <div className="flex items-center gap-1.5">
              <div
                className="w-3 h-3 rounded-sm opacity-30"
                style={{ backgroundColor: chartColors.indigo }}
              />
              <span className="text-muted-foreground">Confidence Band</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div
                className="w-4 h-0.5 rounded"
                style={{ backgroundColor: chartColors.primary }}
              />
              <span className="text-muted-foreground">Base Price</span>
            </div>
          </div>
        )}
      </>
    );

    // Return embedded or wrapped in Card
    if (embedded) {
      return <div>{chartContent}</div>;
    }

    return (
      <Card>
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-medium">
              Price Sensitivity Band
            </CardTitle>
            {lowerBound !== undefined && upperBound !== undefined && (
              <span className="text-xs text-muted-foreground">
                Range: ${lowerBound.toFixed(2)} - ${upperBound.toFixed(2)}
              </span>
            )}
          </div>
        </CardHeader>
        <CardContent>{chartContent}</CardContent>
      </Card>
    );
  }
);

SensitivityBandChart.displayName = 'SensitivityBandChart';

