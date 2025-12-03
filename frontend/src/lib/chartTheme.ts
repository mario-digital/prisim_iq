/**
 * Shared chart theme configuration for Recharts.
 * Provides consistent colors, fonts, and styling across all visualizations.
 */

/**
 * Chart color palette matching the application theme.
 * Uses Tailwind color values for consistency.
 */
export const chartColors = {
  /** Primary blue - main data series */
  primary: '#3b82f6',
  /** Secondary green - positive/success indicators */
  secondary: '#10b981',
  /** Accent amber - highlights and attention */
  accent: '#f59e0b',
  /** Muted slate - reference lines, secondary info */
  muted: '#94a3b8',
  /** Positive green - upward trends, benefits */
  positive: '#22c55e',
  /** Negative red - downward trends, costs */
  negative: '#ef4444',
  /** Indigo - alternative marker color */
  indigo: '#6366f1',
  /** Purple - tertiary data series */
  purple: '#8b5cf6',
  /** Gradient colors for area fills */
  gradient: {
    primary: {
      start: 'rgba(59, 130, 246, 0.4)',
      end: 'rgba(59, 130, 246, 0.05)',
    },
    secondary: {
      start: 'rgba(16, 185, 129, 0.4)',
      end: 'rgba(16, 185, 129, 0.05)',
    },
    indigo: {
      start: 'rgba(99, 102, 241, 0.3)',
      end: 'rgba(99, 102, 241, 0.05)',
    },
  },
} as const;

/**
 * Segment-specific colors for grouped comparisons.
 */
export const segmentColors: Record<string, string> = {
  premium: '#8b5cf6',
  standard: '#3b82f6',
  budget: '#10b981',
  enterprise: '#f59e0b',
  default: '#94a3b8',
};

/**
 * Default chart configuration values.
 */
export const chartConfig = {
  /** Standard margins for charts */
  margin: { top: 10, right: 30, left: 0, bottom: 5 },
  /** Margin with more left space for Y-axis labels */
  marginWithLabel: { top: 10, right: 30, left: 10, bottom: 5 },
  /** Base font size for axis labels */
  fontSize: 12,
  /** Small font size for secondary labels */
  fontSizeSmall: 11,
  /** Font family matching app typography */
  fontFamily: 'Inter, system-ui, sans-serif',
  /** Standard animation duration (ms) */
  animationDuration: 400,
  /** Animation easing function */
  animationEasing: 'ease-out' as const,
} as const;

/**
 * Tooltip styling that matches the app's card design.
 */
export const tooltipStyle = {
  backgroundColor: 'hsl(var(--card))',
  border: '1px solid hsl(var(--border))',
  borderRadius: '8px',
  fontSize: '12px',
  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
} as const;

/**
 * Default animation props for chart elements.
 */
export const animationProps = {
  animationDuration: chartConfig.animationDuration,
  animationEasing: chartConfig.animationEasing,
  animationBegin: 0,
} as const;

/**
 * Price formatter for axis and tooltips.
 */
export const formatPrice = (value: number): string => `$${value.toFixed(0)}`;

/**
 * Detailed price formatter with decimals.
 */
export const formatPriceDetailed = (value: number): string =>
  `$${value.toFixed(2)}`;

/**
 * Percentage formatter for axis and tooltips.
 */
export const formatPercent = (value: number): string => `${value.toFixed(0)}%`;

/**
 * Detailed percentage formatter with one decimal.
 */
export const formatPercentDetailed = (value: number): string =>
  `${value.toFixed(1)}%`;

/**
 * Get color based on direction (positive/negative/neutral).
 */
export const getDirectionColor = (
  direction: 'positive' | 'negative' | 'neutral'
): string => {
  switch (direction) {
    case 'positive':
      return chartColors.positive;
    case 'negative':
      return chartColors.negative;
    default:
      return chartColors.muted;
  }
};

/**
 * Get segment color with fallback.
 */
export const getSegmentColor = (segment: string): string =>
  segmentColors[segment.toLowerCase()] ?? segmentColors.default;

