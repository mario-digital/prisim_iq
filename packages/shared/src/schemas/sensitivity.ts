/**
 * Sensitivity analysis result schemas.
 * Source: backend/src/schemas/sensitivity.py
 */
import { z } from 'zod';

export const ScenarioType = z.enum(['elasticity', 'demand', 'cost']);

/**
 * Result from a single sensitivity scenario.
 * Source: backend/src/schemas/sensitivity.py::ScenarioResult
 */
export const ScenarioResultSchema = z.object({
  scenario_name: z.string().describe('Unique name for the scenario'),
  scenario_type: ScenarioType.describe('Type of sensitivity being tested'),
  modifier: z.number().describe('Multiplier applied (e.g., 0.9 for -10%)'),
  optimal_price: z.number().describe('Optimal price under this scenario'),
  expected_profit: z.number().describe('Expected profit at optimal price'),
  expected_demand: z.number().min(0).max(1).describe('Expected demand at optimal price'),
});

export type ScenarioResult = z.infer<typeof ScenarioResultSchema>;

/**
 * Price confidence band across all scenarios.
 * Source: backend/src/schemas/sensitivity.py::ConfidenceBand
 */
export const ConfidenceBandSchema = z.object({
  min_price: z.number().describe('Minimum optimal price across scenarios'),
  max_price: z.number().describe('Maximum optimal price across scenarios'),
  price_range: z.number().describe('Difference between max and min price'),
  range_percent: z.number().describe('Range as percentage of base price: (max-min)/base * 100'),
});

export type ConfidenceBand = z.infer<typeof ConfidenceBandSchema>;

/**
 * Complete sensitivity analysis result.
 * Source: backend/src/schemas/sensitivity.py::SensitivityResult
 */
export const SensitivityResultSchema = z.object({
  base_price: z.number().describe('Base optimal price (no modifiers)'),
  base_profit: z.number().describe('Base expected profit (no modifiers)'),
  elasticity_sensitivity: z
    .array(ScenarioResultSchema)
    .describe('Results for elasticity sensitivity scenarios'),
  demand_sensitivity: z
    .array(ScenarioResultSchema)
    .describe('Results for demand sensitivity scenarios'),
  cost_sensitivity: z
    .array(ScenarioResultSchema)
    .describe('Results for cost sensitivity scenarios'),
  confidence_band: ConfidenceBandSchema.describe('Price range across all scenarios'),
  worst_case: ScenarioResultSchema.describe('Scenario with lowest expected profit'),
  best_case: ScenarioResultSchema.describe('Scenario with highest expected profit'),
  robustness_score: z
    .number()
    .min(0)
    .max(100)
    .describe('Score 0-100: higher = more robust (less variation)'),
  analysis_time_ms: z.number().min(0).describe('Total analysis time in milliseconds'),
});

export type SensitivityResult = z.infer<typeof SensitivityResultSchema>;

// ----- Chart-Ready Response Schemas (Story 3.6) -----

/**
 * Single data point for sensitivity charts (Recharts-ready).
 * Source: backend/src/schemas/sensitivity.py::SensitivityPoint
 */
export const SensitivityPointSchema = z.object({
  x: z.number().describe('Modifier value (e.g., 0.8 for -20%)'),
  y: z.number().describe('Resulting optimal price'),
  label: z.string().describe("Human-readable label (e.g., '-20%', 'Base', '+20%')"),
  profit: z.number().describe('Expected profit at this point'),
  demand: z.number().describe('Expected demand at this point'),
});

export type SensitivityPoint = z.infer<typeof SensitivityPointSchema>;

/**
 * Summary of the base market context for the analysis.
 * Source: backend/src/schemas/sensitivity.py::MarketContextSummary
 */
export const MarketContextSummarySchema = z.object({
  location_category: z.string().describe('Geographic location category'),
  vehicle_type: z.string().describe('Vehicle type (Economy/Premium)'),
  customer_loyalty_status: z.string().describe('Customer loyalty tier'),
  time_of_booking: z.string().describe('Time period of booking'),
  supply_demand_ratio: z.number().describe('Supply/demand ratio'),
});

export type MarketContextSummary = z.infer<typeof MarketContextSummarySchema>;

/**
 * Summary of worst/best case scenarios for display.
 * Source: backend/src/schemas/sensitivity.py::ScenarioSummary
 */
export const ScenarioSummarySchema = z.object({
  scenario_name: z.string().describe('Name of the scenario'),
  scenario_type: z.string().describe('Type: elasticity, demand, or cost'),
  price: z.number().describe('Optimal price under this scenario'),
  profit: z.number().describe('Expected profit under this scenario'),
  description: z.string().describe('Human-readable description of the scenario impact'),
});

export type ScenarioSummary = z.infer<typeof ScenarioSummarySchema>;

/**
 * Complete sensitivity analysis response formatted for frontend charts.
 * Source: backend/src/schemas/sensitivity.py::SensitivityResponse
 */
export const SensitivityResponseSchema = z.object({
  // Base reference
  base_context: MarketContextSummarySchema.describe('Summary of the input market context'),
  base_price: z.number().describe('Base optimal price (no modifiers)'),
  base_profit: z.number().describe('Base expected profit (no modifiers)'),

  // Sensitivity arrays (Recharts-ready)
  elasticity_sensitivity: z
    .array(SensitivityPointSchema)
    .describe('Elasticity sensitivity points for chart plotting (7 points)'),
  demand_sensitivity: z
    .array(SensitivityPointSchema)
    .describe('Demand sensitivity points for chart plotting (5 points)'),
  cost_sensitivity: z
    .array(SensitivityPointSchema)
    .describe('Cost sensitivity points for chart plotting (5 points)'),

  // Confidence metrics
  confidence_band: ConfidenceBandSchema.describe('Price confidence band across all scenarios'),
  robustness_score: z
    .number()
    .min(0)
    .max(100)
    .describe('Score 0-100: higher = more robust (less price variation)'),

  // Extremes
  worst_case: ScenarioSummarySchema.describe('Scenario with lowest expected profit'),
  best_case: ScenarioSummarySchema.describe('Scenario with highest expected profit'),

  // Metadata
  scenarios_calculated: z.number().int().describe('Total number of scenarios analyzed'),
  processing_time_ms: z.number().min(0).describe('Total processing time in milliseconds'),
});

export type SensitivityResponse = z.infer<typeof SensitivityResponseSchema>;
export type ScenarioTypeValue = z.infer<typeof ScenarioType>;

