'use client';

import type { FC } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { BarChart3 } from 'lucide-react';

interface SegmentData {
  segment: string;
  uplift: number;
}

interface SegmentPerformanceChartProps {
  /** Segment performance data */
  data: SegmentData[];
}

export const SegmentPerformanceChart: FC<SegmentPerformanceChartProps> = ({
  data,
}) => {
  // Color based on uplift value
  const getBarColor = (uplift: number) => {
    if (uplift >= 25) return '#22c55e'; // green-500
    if (uplift >= 15) return '#84cc16'; // lime-500
    if (uplift >= 10) return '#eab308'; // yellow-500
    return '#f97316'; // orange-500
  };

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-primary" />
          Segment Performance
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[250px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={data}
              layout="vertical"
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
              <XAxis
                type="number"
                domain={[0, 'auto']}
                tickFormatter={(value) => `${value}%`}
                fontSize={12}
              />
              <YAxis
                type="category"
                dataKey="segment"
                width={120}
                fontSize={12}
                tickLine={false}
              />
              <Tooltip
                formatter={(value: number) => [`${value.toFixed(1)}%`, 'Profit Uplift']}
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '8px',
                }}
              />
              <Bar dataKey="uplift" radius={[0, 4, 4, 0]}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getBarColor(entry.uplift)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
};

