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

/**
 * Data point for sensitivity band visualization.
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
  /** Array of sensitivity band data points */
  data: SensitivityBandPoint[];
  /** Base price for reference line */
  basePrice: number;
  /** Lower confidence bound */
  lowerBound?: number;
  /** Upper confidence bound */
  upperBound?: number;
}

/**
 * Area chart showing price sensitivity with confidence bands.
 * Displays min/max price range with base price reference line.
 * Memoized to prevent unnecessary re-renders.
 */
export const SensitivityBandChart: FC<SensitivityBandChartProps> = memo(
  ({ data, basePrice, lowerBound, upperBound }) => {
    // Transform data for stacked area (band visualization)
    const chartData = data.map((point) => ({
      ...point,
      // For proper band visualization, we need the range
      bandLow: point.minPrice,
      bandHigh: point.maxPrice - point.minPrice, // Stacked on top of low
    }));

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
        <CardContent>
          {data.length === 0 ? (
            <div className="flex items-center justify-center h-[200px] text-sm text-muted-foreground">
              No sensitivity data available
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart
                data={chartData}
                margin={chartConfig.margin}
              >
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
                      stopOpacity={0.1}
                    />
                  </linearGradient>
                </defs>

                <XAxis
                  dataKey="scenario"
                  fontSize={chartConfig.fontSize}
                  tickLine={false}
                />
                <YAxis
                  tickFormatter={(v) => `$${v}`}
                  fontSize={chartConfig.fontSize}
                  tickLine={false}
                  axisLine={false}
                  domain={['dataMin - 5', 'dataMax + 5']}
                />
                <Tooltip
                  formatter={(value: number, name: string) => {
                    const labels: Record<string, string> = {
                      price: 'Price',
                      minPrice: 'Min',
                      maxPrice: 'Max',
                    };
                    return [`$${value.toFixed(2)}`, labels[name] || name];
                  }}
                  labelFormatter={(label) => `Scenario: ${label}`}
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

                {/* Central price line */}
                <Area
                  type="monotone"
                  dataKey="price"
                  stroke={chartColors.primary}
                  strokeWidth={2}
                  fill="none"
                  {...animationProps}
                />

                {/* Lower bound reference */}
                {lowerBound !== undefined && (
                  <ReferenceLine
                    y={lowerBound}
                    stroke={chartColors.muted}
                    strokeDasharray="4 4"
                    strokeWidth={1}
                  />
                )}

                {/* Upper bound reference */}
                {upperBound !== undefined && (
                  <ReferenceLine
                    y={upperBound}
                    stroke={chartColors.muted}
                    strokeDasharray="4 4"
                    strokeWidth={1}
                  />
                )}

                {/* Base price reference */}
                <ReferenceLine
                  y={basePrice}
                  stroke={chartColors.secondary}
                  strokeWidth={2}
                  label={{
                    value: `Base: $${basePrice.toFixed(0)}`,
                    position: 'right',
                    fontSize: chartConfig.fontSizeSmall,
                    fill: chartColors.secondary,
                  }}
                />
              </AreaChart>
            </ResponsiveContainer>
          )}

          {/* Legend */}
          <div className="flex justify-center gap-4 mt-2 text-xs">
            <div className="flex items-center gap-1.5">
              <div
                className="w-4 h-0.5 rounded"
                style={{ backgroundColor: chartColors.primary }}
              />
              <span className="text-muted-foreground">Price</span>
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
                style={{ backgroundColor: chartColors.secondary }}
              />
              <span className="text-muted-foreground">Base Price</span>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }
);

SensitivityBandChart.displayName = 'SensitivityBandChart';

