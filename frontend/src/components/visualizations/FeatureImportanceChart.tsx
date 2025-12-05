'use client';

import { memo, type FC } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  LabelList,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  chartColors,
  chartConfig,
  tooltipStyle,
  tooltipWrapperStyle,
  tooltipLabelStyle,
  tooltipItemStyle,
  cursorStyle,
  animationProps,
  getDirectionColor,
} from '@/lib/chartTheme';
import type { FeatureContribution } from './types';

interface FeatureImportanceChartProps {
  data: FeatureContribution[];
}

/**
 * Clamps a value to the specified range [min, max].
 * Defensive utility for handling potentially invalid backend data.
 */
const clamp = (value: number, min: number, max: number): number =>
  Math.max(min, Math.min(max, value));

/**
 * Horizontal bar chart showing feature importance for the pricing decision.
 * Features are sorted by importance and color-coded by impact direction.
 * Memoized to prevent unnecessary re-renders when parent updates.
 *
 * NOTE: Importance values are defensively clamped to [0, 1] to handle
 * potential backend data errors gracefully without breaking the UI.
 */
export const FeatureImportanceChart: FC<FeatureImportanceChartProps> = memo(({
  data,
}) => {
  // Sort by importance and take top 6 features
  // Clamp importance to [0, 1] to handle invalid data gracefully
  const chartData = [...data]
    .sort((a, b) => b.importance - a.importance)
    .slice(0, 6)
    .map((d) => ({
      name: d.displayName,
      value: clamp(d.importance, 0, 1) * 100,
      direction: d.direction,
      currentValue: d.currentValue,
    }));

  const getBarColor = (direction: string) =>
    getDirectionColor(direction as 'positive' | 'negative' | 'neutral');

  return (
    <Card className="overflow-visible">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">Feature Importance</CardTitle>
      </CardHeader>
      <CardContent className="overflow-visible">
        {chartData.length === 0 ? (
          <div className="flex items-center justify-center h-[220px] text-sm text-muted-foreground">
            No feature data available
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={220} className="overflow-visible">
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{ top: 5, right: 45, left: 20, bottom: 5 }}
            >
              <XAxis
                type="number"
                domain={[0, 100]}
                tickFormatter={(v) => `${v}%`}
                fontSize={chartConfig.fontSize}
                tickLine={false}
                tick={{ fill: 'var(--chart-axis-text)' }}
              />
              <YAxis
                type="category"
                dataKey="name"
                width={110}
                fontSize={chartConfig.fontSize}
                tickLine={false}
                axisLine={false}
                tick={{ fill: 'var(--chart-axis-text)' }}
              />
              <Tooltip
                formatter={(value: number) => [`${value.toFixed(1)}%`, 'Importance']}
                labelFormatter={(label) => {
                  const item = chartData.find((d) => d.name === label);
                  return `${label}: ${item?.currentValue ?? 'N/A'}`;
                }}
                contentStyle={tooltipStyle}
                wrapperStyle={tooltipWrapperStyle}
                labelStyle={tooltipLabelStyle}
                itemStyle={tooltipItemStyle}
                cursor={cursorStyle}
                allowEscapeViewBox={{ x: true, y: true }}
              />
              <Bar
                dataKey="value"
                radius={[0, 4, 4, 0]}
                {...animationProps}
              >
                {chartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={getBarColor(entry.direction)}
                  />
                ))}
                <LabelList
                  dataKey="value"
                  position="right"
                  formatter={(v: number) => `${v.toFixed(1)}%`}
                  fontSize={chartConfig.fontSizeSmall}
                  fill={chartColors.muted}
                />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}

        {/* Legend */}
        <div className="flex justify-center gap-4 mt-2 text-xs">
          <div className="flex items-center gap-1.5">
            <div
              className="w-3 h-3 rounded-sm"
              style={{ backgroundColor: chartColors.positive }}
            />
            <span className="text-muted-foreground">Increases price</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div
              className="w-3 h-3 rounded-sm"
              style={{ backgroundColor: chartColors.negative }}
            />
            <span className="text-muted-foreground">Decreases price</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
});

FeatureImportanceChart.displayName = 'FeatureImportanceChart';
