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
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { FeatureContribution } from './types';

interface FeatureImportanceChartProps {
  data: FeatureContribution[];
}

/**
 * Horizontal bar chart showing feature importance for the pricing decision.
 * Features are sorted by importance and color-coded by impact direction.
 * Memoized to prevent unnecessary re-renders when parent updates.
 */
export const FeatureImportanceChart: FC<FeatureImportanceChartProps> = memo(({
  data,
}) => {
  // Sort by importance and take top 6 features
  const chartData = [...data]
    .sort((a, b) => b.importance - a.importance)
    .slice(0, 6)
    .map((d) => ({
      name: d.displayName,
      value: d.importance * 100,
      direction: d.direction,
      currentValue: d.currentValue,
    }));

  const getBarColor = (direction: string) => {
    switch (direction) {
      case 'positive':
        return '#10b981'; // emerald-500
      case 'negative':
        return '#ef4444'; // red-500
      default:
        return '#6b7280'; // gray-500
    }
  };

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">Feature Importance</CardTitle>
      </CardHeader>
      <CardContent>
        {chartData.length === 0 ? (
          <div className="flex items-center justify-center h-[200px] text-sm text-muted-foreground">
            No feature data available
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={200}>
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <XAxis
                type="number"
                domain={[0, 100]}
                tickFormatter={(v) => `${v}%`}
                fontSize={12}
              />
              <YAxis
                type="category"
                dataKey="name"
                width={100}
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip
                formatter={(value: number) => [`${value.toFixed(1)}%`, 'Importance']}
                labelFormatter={(label) => {
                  const item = chartData.find((d) => d.name === label);
                  return `${label}: ${item?.currentValue ?? 'N/A'}`;
                }}
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '8px',
                  fontSize: '12px',
                }}
              />
              <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                {chartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={getBarColor(entry.direction)}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}

        {/* Legend */}
        <div className="flex justify-center gap-4 mt-2 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-sm bg-emerald-500" />
            <span className="text-muted-foreground">Increases price</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-sm bg-red-500" />
            <span className="text-muted-foreground">Decreases price</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
});

FeatureImportanceChart.displayName = 'FeatureImportanceChart';

