'use client';

import { memo, type FC } from 'react';
import {
  LineChart,
  Line,
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
  tooltipLabelStyle,
  tooltipItemStyle,
  cursorStyle,
  animationProps,
} from '@/lib/chartTheme';
import type { CurvePoint } from './types';

interface DemandCurveChartProps {
  data: CurvePoint[];
  optimalPrice: number;
  currentPrice: number;
}

/**
 * Line chart showing price vs. expected demand relationship.
 * Marks the optimal and current price points.
 * Memoized to prevent unnecessary re-renders when parent updates.
 */
export const DemandCurveChart: FC<DemandCurveChartProps> = memo(({
  data,
  optimalPrice,
  currentPrice,
}) => {
  // Find the data points closest to optimal and current prices
  const findClosestPoint = (targetPrice: number) =>
    data.reduce((closest, point) =>
      Math.abs(point.price - targetPrice) < Math.abs(closest.price - targetPrice)
        ? point
        : closest
    );

  const optimalPoint = data.length > 0 ? findClosestPoint(optimalPrice) : null;
  const currentPoint = data.length > 0 ? findClosestPoint(currentPrice) : null;

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">Demand Curve</CardTitle>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <div className="flex items-center justify-center h-[200px] text-sm text-muted-foreground">
            No demand data available
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={200}>
            <LineChart
              data={data}
              margin={chartConfig.marginWithLabel}
            >
              <XAxis
                dataKey="price"
                tickFormatter={(v) => `$${v}`}
                fontSize={chartConfig.fontSize}
                tickLine={false}
              />
              <YAxis
                tickFormatter={(v) => v.toFixed(2)}
                fontSize={chartConfig.fontSize}
                tickLine={false}
                axisLine={false}
                label={{
                  value: 'Demand',
                  angle: -90,
                  position: 'insideLeft',
                  fontSize: chartConfig.fontSizeSmall,
                  fill: chartColors.muted,
                }}
              />
              <Tooltip
                formatter={(value: number) => [value.toFixed(2), 'Expected Demand']}
                labelFormatter={(label) => `Price: $${label}`}
                contentStyle={tooltipStyle}
                labelStyle={tooltipLabelStyle}
                itemStyle={tooltipItemStyle}
                cursor={cursorStyle}
              />

              {/* Main demand curve */}
              <Line
                type="monotone"
                dataKey="value"
                stroke={chartColors.primary}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, fill: chartColors.primary }}
                {...animationProps}
              />

              {/* Reference line for current price */}
              {currentPoint && (
                <ReferenceLine
                  x={currentPoint.price}
                  stroke={chartColors.secondary}
                  strokeDasharray="4 4"
                  strokeWidth={1}
                />
              )}

              {/* Optimal price point marker with label */}
              {optimalPoint && (
                <ReferenceDot
                  x={optimalPoint.price}
                  y={optimalPoint.value}
                  r={6}
                  fill={chartColors.secondary}
                  stroke="#fff"
                  strokeWidth={2}
                  label={{
                    value: `$${optimalPoint.price}`,
                    position: 'top',
                    fontSize: chartConfig.fontSizeSmall,
                    fill: chartColors.secondary,
                  }}
                />
              )}

              {/* Current price point marker - only show if both points exist and prices differ */}
              {currentPoint && optimalPoint && currentPoint.price !== optimalPoint.price && (
                <ReferenceDot
                  x={currentPoint.price}
                  y={currentPoint.value}
                  r={5}
                  fill={chartColors.indigo}
                  stroke="#fff"
                  strokeWidth={2}
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        )}

        {/* Legend */}
        <div className="flex justify-center gap-4 mt-2 text-xs">
          <div className="flex items-center gap-1.5">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: chartColors.secondary }}
            />
            <span className="text-muted-foreground">Optimal Price</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: chartColors.indigo }}
            />
            <span className="text-muted-foreground">Current Price</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
});

DemandCurveChart.displayName = 'DemandCurveChart';

