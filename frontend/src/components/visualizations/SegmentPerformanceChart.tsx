'use client';

import { memo, type FC } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  chartColors,
  chartConfig,
  tooltipStyle,
  tooltipLabelStyle,
  tooltipItemStyle,
  cursorStyle,
  animationProps,
} from '@/lib/chartTheme';

/**
 * Data point for segment performance comparison.
 */
export interface SegmentPerformanceData {
  /** Segment name (e.g., 'Premium', 'Standard', 'Budget') */
  segment: string;
  /** Baseline metric value (before optimization) */
  baseline: number;
  /** Optimized metric value (after optimization) */
  optimized: number;
  /** Improvement percentage */
  improvement?: number;
}

interface SegmentPerformanceChartProps {
  /** Array of segment performance data */
  data: SegmentPerformanceData[];
  /** Metric being compared (e.g., 'Revenue', 'Margin') */
  metricLabel?: string;
  /** Format values as currency */
  isCurrency?: boolean;
}

/**
 * Grouped bar chart comparing baseline vs optimized performance across segments.
 * Shows improvement with different colored bars for each category.
 * Memoized to prevent unnecessary re-renders.
 */
export const SegmentPerformanceChart: FC<SegmentPerformanceChartProps> = memo(
  ({ data, metricLabel = 'Value', isCurrency = true }) => {
    const formatValue = (value: number) =>
      isCurrency ? `$${value.toFixed(0)}` : value.toFixed(1);

    // Custom legend formatter
    const legendFormatter = (value: string) => (
      <span className="text-xs text-muted-foreground capitalize">{value}</span>
    );

    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">
            Segment Performance Comparison
          </CardTitle>
        </CardHeader>
        <CardContent>
          {data.length === 0 ? (
            <div className="flex items-center justify-center h-[200px] text-sm text-muted-foreground">
              No segment data available
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart
                data={data}
                margin={{ top: 10, right: 30, left: 10, bottom: 5 }}
              >
                <XAxis
                  dataKey="segment"
                  fontSize={chartConfig.fontSize}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  tickFormatter={formatValue}
                  fontSize={chartConfig.fontSize}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip
                  formatter={(value: number, name: string) => [
                    formatValue(value),
                    name.charAt(0).toUpperCase() + name.slice(1),
                  ]}
                  labelFormatter={(label) => `Segment: ${label}`}
                  contentStyle={tooltipStyle}
                  labelStyle={tooltipLabelStyle}
                  itemStyle={tooltipItemStyle}
                  cursor={cursorStyle}
                />
                <Legend
                  formatter={legendFormatter}
                  iconType="square"
                  iconSize={10}
                  wrapperStyle={{ fontSize: '12px' }}
                />
                <Bar
                  dataKey="baseline"
                  name="Baseline"
                  fill={chartColors.muted}
                  radius={[4, 4, 0, 0]}
                  {...animationProps}
                />
                <Bar
                  dataKey="optimized"
                  name="Optimized"
                  fill={chartColors.primary}
                  radius={[4, 4, 0, 0]}
                  {...animationProps}
                  animationBegin={100}
                />
              </BarChart>
            </ResponsiveContainer>
          )}

          {/* Improvement summary */}
          {data.length > 0 && (
            <div className="flex justify-center gap-4 mt-3 text-xs">
              {data
                .filter((d) => d.improvement !== undefined)
                .map((d) => (
                  <div
                    key={d.segment}
                    className="flex items-center gap-1.5"
                  >
                    <span className="text-muted-foreground">{d.segment}:</span>
                    <span
                      className={
                        (d.improvement ?? 0) >= 0
                          ? 'text-emerald-600 dark:text-emerald-400 font-medium'
                          : 'text-red-600 dark:text-red-400 font-medium'
                      }
                    >
                      {(d.improvement ?? 0) >= 0 ? '+' : ''}
                      {d.improvement?.toFixed(1)}%
                    </span>
                  </div>
                ))}
            </div>
          )}
        </CardContent>
      </Card>
    );
  }
);

SegmentPerformanceChart.displayName = 'SegmentPerformanceChart';

