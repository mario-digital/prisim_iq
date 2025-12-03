/**
 * Optimization result schemas for price optimization.
 * Source: backend/src/schemas/optimization.py
 */
import { z } from 'zod';

/**
 * A single point on the price-demand curve.
 * Source: backend/src/schemas/optimization.py::PriceDemandPoint
 */
export const PriceDemandPointSchema = z.object({
  price: z.number().describe('Price point'),
  demand: z.number().min(0).max(1).describe('Predicted demand at this price'),
  profit: z.number().describe('Expected profit at this price'),
});

export type PriceDemandPoint = z.infer<typeof PriceDemandPointSchema>;

/**
 * Result from price optimization.
 * Source: backend/src/schemas/optimization.py::OptimizationResult
 */
export const OptimizationResultSchema = z.object({
  optimal_price: z.number().describe('Profit-maximizing price'),
  expected_demand: z.number().min(0).max(1).describe('Expected demand at optimal price'),
  expected_profit: z.number().describe('Expected profit at optimal price'),
  baseline_price: z.number().describe('Historical/baseline price'),
  baseline_profit: z.number().describe('Profit at baseline price'),
  profit_uplift_percent: z
    .number()
    .describe('Percentage improvement over baseline: (optimal - baseline) / baseline * 100'),
  price_demand_curve: z
    .array(PriceDemandPointSchema)
    .describe('Sample points for visualization'),
  optimization_time_ms: z.number().min(0).describe('Time taken to optimize in milliseconds'),
});

export type OptimizationResult = z.infer<typeof OptimizationResultSchema>;

