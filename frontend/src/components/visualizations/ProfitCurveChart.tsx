'use client';

import { memo, type FC } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceDot,
  ReferenceLine,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  chartColors,
  chartConfig,
  tooltipStyle,
  cursorStyle,
  animationProps,
} from '@/lib/chartTheme';
import type { CurvePoint } from './types';

interface ProfitCurveChartProps {
  data: CurvePoint[];
  optimalPrice: number;
}

/**
 * Area chart showing price vs. expected profit with gradient fill.
 * Highlights the maximum profit point.
 * Memoized to prevent unnecessary re-renders when parent updates.
 */
export const ProfitCurveChart: FC<ProfitCurveChartProps> = memo(({
  data,
  optimalPrice,
}) => {
  // Find the point with maximum profit and the optimal price point
  const maxProfitPoint = data.reduce(
    (max, point) => (point.value > max.value ? point : max),
    data[0] || { price: 0, value: 0 }
  );

  const optimalPoint =
    data.length > 0
      ? data.reduce((closest, point) =>
          Math.abs(point.price - optimalPrice) <
          Math.abs(closest.price - optimalPrice)
            ? point
            : closest
        )
      : null;

  // Calculate baseline (minimum profit for comparison)
  const minProfit = data.length > 0 ? Math.min(...data.map((d) => d.value)) : 0;

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium">Profit Curve</CardTitle>
          {maxProfitPoint && (
            <span className="text-xs text-muted-foreground">
              Max: ${maxProfitPoint.value.toFixed(0)} @ ${maxProfitPoint.price}
            </span>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <div className="flex items-center justify-center h-[200px] text-sm text-muted-foreground">
            No profit data available
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart
              data={data}
              margin={chartConfig.margin}
            >
              {/* Gradient definition */}
              <defs>
                <linearGradient id="profitGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop
                    offset="5%"
                    stopColor={chartColors.primary}
                    stopOpacity={0.4}
                  />
                  <stop
                    offset="95%"
                    stopColor={chartColors.primary}
                    stopOpacity={0.05}
                  />
                </linearGradient>
              </defs>

              <XAxis
                dataKey="price"
                tickFormatter={(v) => `$${v}`}
                fontSize={chartConfig.fontSize}
                tickLine={false}
              />
              <YAxis
                tickFormatter={(v) => `$${v}`}
                fontSize={chartConfig.fontSize}
                tickLine={false}
                axisLine={false}
                domain={[minProfit * 0.9, 'auto']}
              />
              <Tooltip
                formatter={(value: number) => [`$${value.toFixed(2)}`, 'Expected Profit']}
                labelFormatter={(label) => `Price: $${label}`}
                contentStyle={tooltipStyle}
                cursor={cursorStyle}
              />

              {/* Baseline reference */}
              {minProfit > 0 && (
                <ReferenceLine
                  y={minProfit}
                  stroke={chartColors.muted}
                  strokeDasharray="4 4"
                  strokeWidth={1}
                />
              )}

              {/* Main profit curve */}
              <Area
                type="monotone"
                dataKey="value"
                stroke={chartColors.primary}
                strokeWidth={2}
                fill="url(#profitGradient)"
                activeDot={{ r: 4, fill: chartColors.primary }}
                {...animationProps}
              />

              {/* Maximum profit point marker with label */}
              {maxProfitPoint && (
                <ReferenceDot
                  x={maxProfitPoint.price}
                  y={maxProfitPoint.value}
                  r={6}
                  fill={chartColors.secondary}
                  stroke="#fff"
                  strokeWidth={2}
                  label={{
                    value: `$${maxProfitPoint.value.toFixed(0)}`,
                    position: 'top',
                    fontSize: chartConfig.fontSizeSmall,
                    fill: chartColors.secondary,
                  }}
                />
              )}

              {/* Optimal price point if different from max */}
              {optimalPoint &&
                Math.abs(optimalPoint.price - maxProfitPoint.price) > 1 && (
                  <ReferenceDot
                    x={optimalPoint.price}
                    y={optimalPoint.value}
                    r={5}
                    fill={chartColors.accent}
                    stroke="#fff"
                    strokeWidth={2}
                  />
                )}
            </AreaChart>
          </ResponsiveContainer>
        )}

        {/* Legend */}
        <div className="flex justify-center gap-4 mt-2 text-xs">
          <div className="flex items-center gap-1.5">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: chartColors.secondary }}
            />
            <span className="text-muted-foreground">Maximum Profit</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: chartColors.accent }}
            />
            <span className="text-muted-foreground">Recommended</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
});

ProfitCurveChart.displayName = 'ProfitCurveChart';

