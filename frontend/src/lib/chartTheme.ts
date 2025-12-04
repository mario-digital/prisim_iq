/**
 * Shared chart theme configuration for Recharts.
 * Provides consistent colors, fonts, and styling across all visualizations.
 */

/**
 * Chart color palette matching the PrismIQ dark theme.
 * Vibrant colors optimized for dark backgrounds.
 */
export const chartColors = {
  /** Primary cyan - main data series, matches brand */
  primary: '#22d3ee',
  /** Secondary emerald - positive/success indicators */
  secondary: '#34d399',
  /** Accent amber - highlights and attention */
  accent: '#fbbf24',
  /** Muted slate - reference lines, secondary info */
  muted: '#64748b',
  /** Positive emerald - upward trends, benefits */
  positive: '#34d399',
  /** Negative rose - downward trends, costs */
  negative: '#f43f5e',
  /** Indigo - alternative marker color */
  indigo: '#818cf8',
  /** Purple - tertiary data series */
  purple: '#a78bfa',
  /** Gradient colors for area fills - optimized for dark mode */
  gradient: {
    primary: {
      start: 'rgba(34, 211, 238, 0.35)',
      end: 'rgba(34, 211, 238, 0.02)',
    },
    secondary: {
      start: 'rgba(52, 211, 153, 0.35)',
      end: 'rgba(52, 211, 153, 0.02)',
    },
    indigo: {
      start: 'rgba(129, 140, 248, 0.3)',
      end: 'rgba(129, 140, 248, 0.02)',
    },
  },
} as const;

/**
 * Segment-specific colors for grouped comparisons.
 * Vibrant colors optimized for dark backgrounds.
 */
export const segmentColors: Record<string, string> = {
  premium: '#a78bfa',    // Soft purple
  standard: '#22d3ee',   // Cyan
  budget: '#34d399',     // Emerald
  enterprise: '#fbbf24', // Amber
  default: '#94a3b8',    // Slate
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
 * Tooltip styling that matches the app's dark card design.
 */
export const tooltipStyle = {
  backgroundColor: 'hsl(var(--card))',
  border: '1px solid hsl(var(--border))',
  borderRadius: '8px',
  fontSize: '12px',
  boxShadow: '0 8px 24px -4px rgba(0, 0, 0, 0.4), 0 4px 8px -2px rgba(0, 0, 0, 0.2)',
  color: 'hsl(var(--foreground))',
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

