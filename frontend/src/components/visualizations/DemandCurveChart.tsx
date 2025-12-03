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
              margin={{ top: 10, right: 30, left: 0, bottom: 5 }}
            >
              <XAxis
                dataKey="price"
                tickFormatter={(v) => `$${v}`}
                fontSize={12}
                tickLine={false}
              />
              <YAxis
                tickFormatter={(v) => v.toFixed(0)}
                fontSize={12}
                tickLine={false}
                axisLine={false}
                label={{
                  value: 'Demand',
                  angle: -90,
                  position: 'insideLeft',
                  fontSize: 11,
                  fill: 'hsl(var(--muted-foreground))',
                }}
              />
              <Tooltip
                formatter={(value: number) => [value.toFixed(0), 'Expected Demand']}
                labelFormatter={(label) => `Price: $${label}`}
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '8px',
                  fontSize: '12px',
                }}
              />

              {/* Main demand curve */}
              <Line
                type="monotone"
                dataKey="value"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, fill: '#3b82f6' }}
              />

              {/* Reference line for current price */}
              {currentPoint && (
                <ReferenceLine
                  x={currentPoint.price}
                  stroke="#10b981"
                  strokeDasharray="4 4"
                  strokeWidth={1}
                />
              )}

              {/* Optimal price point marker */}
              {optimalPoint && (
                <ReferenceDot
                  x={optimalPoint.price}
                  y={optimalPoint.value}
                  r={6}
                  fill="#10b981"
                  stroke="#fff"
                  strokeWidth={2}
                />
              )}

              {/* Current price point marker - only show if both points exist and prices differ */}
              {currentPoint && optimalPoint && currentPoint.price !== optimalPoint.price && (
                <ReferenceDot
                  x={currentPoint.price}
                  y={currentPoint.value}
                  r={5}
                  fill="#6366f1"
                  stroke="#fff"
                  strokeWidth={2}
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        )}

        {/* Legend */}
        <div className="flex justify-center gap-4 mt-2 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-emerald-500" />
            <span className="text-muted-foreground">Optimal Price</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-indigo-500" />
            <span className="text-muted-foreground">Current Price</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
});

DemandCurveChart.displayName = 'DemandCurveChart';

