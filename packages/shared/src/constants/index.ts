/**
 * Shared constants for PrismIQ.
 */

/**
 * Customer segment display names.
 */
export const SEGMENT_LABELS = {
  price_sensitive: 'Price Sensitive',
  value_seeker: 'Value Seeker',
  premium: 'Premium',
  enterprise: 'Enterprise',
} as const;

/**
 * Segment colors for visualizations.
 */
export const SEGMENT_COLORS = {
  price_sensitive: '#ef4444', // red
  value_seeker: '#f59e0b', // amber
  premium: '#8b5cf6', // violet
  enterprise: '#0ea5e9', // sky
} as const;

/**
 * Confidence level display configuration.
 */
export const CONFIDENCE_CONFIG = {
  low: {
    label: 'Low Confidence',
    color: '#ef4444',
    minScore: 0,
    maxScore: 0.5,
  },
  medium: {
    label: 'Medium Confidence',
    color: '#f59e0b',
    minScore: 0.5,
    maxScore: 0.8,
  },
  high: {
    label: 'High Confidence',
    color: '#22c55e',
    minScore: 0.8,
    maxScore: 1,
  },
} as const;

/**
 * Season labels.
 */
export const SEASON_LABELS = {
  spring: 'Spring',
  summer: 'Summer',
  fall: 'Fall',
  winter: 'Winter',
} as const;

/**
 * Day of week labels.
 */
export const DAY_LABELS = [
  'Sunday',
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
] as const;

/**
 * API endpoints.
 */
export const API_ENDPOINTS = {
  health: '/health',
  chat: '/api/chat',
  optimize: '/api/pricing/optimize',
  segment: '/api/pricing/segment',
  explain: '/api/explainability/explain',
  sensitivity: '/api/explainability/sensitivity',
} as const;

/**
 * Default market context values.
 */
export const DEFAULT_MARKET_CONTEXT = {
  customerSegment: 'value_seeker',
  demandLevel: 0.5,
  competitorPrice: 100,
  customerLifetimeValue: 500,
  inventoryLevel: 100,
  dayOfWeek: 1,
  hourOfDay: 12,
  season: 'spring',
  isPromotionActive: false,
  basePrice: 100,
} as const;

