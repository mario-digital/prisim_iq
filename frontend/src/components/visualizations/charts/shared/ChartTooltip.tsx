'use client';

import { type FC } from 'react';
import { tooltipStyle } from '@/lib/chartTheme';

interface ChartTooltipProps {
  active?: boolean;
  payload?: Array<{
    value: number;
    name: string;
    dataKey: string;
    color?: string;
    payload?: Record<string, unknown>;
  }>;
  label?: string | number;
  labelFormatter?: (label: string | number) => string;
  valueFormatter?: (value: number, name: string) => string;
}

/**
 * Custom tooltip component for consistent styling across all charts.
 * Provides formatted label and value display with theme integration.
 */
export const ChartTooltip: FC<ChartTooltipProps> = ({
  active,
  payload,
  label,
  labelFormatter,
  valueFormatter,
}) => {
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  const formattedLabel = labelFormatter ? labelFormatter(label ?? '') : label;

  return (
    <div
      style={tooltipStyle}
      className="px-3 py-2 shadow-lg"
    >
      {formattedLabel && (
        <p className="text-xs font-medium text-muted-foreground mb-1">
          {formattedLabel}
        </p>
      )}
      <div className="space-y-0.5">
        {payload.map((entry, index) => {
          const formattedValue = valueFormatter
            ? valueFormatter(entry.value, entry.name)
            : entry.value.toFixed(2);

          return (
            <div
              key={`tooltip-${index}`}
              className="flex items-center gap-2 text-sm"
            >
              {entry.color && (
                <span
                  className="w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: entry.color }}
                />
              )}
              <span className="text-foreground font-medium">
                {formattedValue}
              </span>
              <span className="text-muted-foreground text-xs">
                {entry.name}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

