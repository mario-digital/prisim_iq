/**
 * Pricing result schemas for price optimization API responses.
 * Source: backend/src/schemas/pricing.py
 */
import { z } from 'zod';
import { AppliedRuleSchema } from './rules';
import { PriceDemandPointSchema } from './optimization';
import { SegmentDetailsSchema } from './segment';

/**
 * Complete pricing recommendation result from optimization endpoint.
 * Source: backend/src/schemas/pricing.py::PricingResult
 */
export const PricingResultSchema = z.object({
  // Core recommendation
  recommended_price: z
    .number()
    .min(0)
    .describe('Final recommended price after ML optimization and business rules'),
  confidence_score: z
    .number()
    .min(0)
    .max(1)
    .describe('Confidence score based on segment centroid distance (0.0-1.0, higher is better)'),

  // Demand and profit metrics
  expected_demand: z
    .number()
    .min(0)
    .max(1)
    .describe('Predicted demand at recommended price (0.0-1.0)'),
  expected_profit: z.number().describe('Expected profit at recommended price'),
  baseline_profit: z.number().describe('Profit at historical/baseline price'),
  profit_uplift_percent: z
    .number()
    .describe('Percentage improvement over baseline: (optimal - baseline) / baseline * 100'),

  // Segment information
  segment: SegmentDetailsSchema.describe('Market segment classification with characteristics'),

  // Model information
  model_used: z
    .string()
    .describe("Name of ML model used for demand prediction (e.g., 'xgboost')"),

  // Business rules applied
  rules_applied: z
    .array(AppliedRuleSchema)
    .default([])
    .describe('List of business rules that modified the price'),
  price_before_rules: z
    .number()
    .min(0)
    .describe('ML-optimized price before business rule adjustments'),

  // Visualization data
  price_demand_curve: z
    .array(PriceDemandPointSchema)
    .default([])
    .describe('Sample points for price-demand curve visualization'),

  // Metadata
  processing_time_ms: z.number().min(0).describe('Total processing time in milliseconds'),
  timestamp: z.string().datetime().describe('Timestamp of the optimization'),
});

export type PricingResult = z.infer<typeof PricingResultSchema>;

