/**
 * Explanation schemas for explain_decision endpoint.
 * Source: backend/src/schemas/explanation.py
 */
import { z } from 'zod';
import { MarketContextSchema } from './market';
import { PricingResultSchema } from './pricing';
import { FeatureContributionSchema } from './explainability';
import { DecisionTraceSchema, ModelAgreementSchema } from './decision-trace';

/**
 * Request schema for the explain_decision endpoint.
 * Source: backend/src/schemas/explanation.py::ExplainRequest
 */
export const ExplainRequestSchema = z.object({
  context: MarketContextSchema.describe('Market conditions and customer profile'),
  pricing_result_id: z
    .string()
    .nullable()
    .optional()
    .describe('Optional reference to a previous pricing result for consistency'),
  include_trace: z.boolean().default(true).describe('Include full decision trace in response'),
  include_shap: z.boolean().default(true).describe('Include SHAP-based local feature importance'),
});

export type ExplainRequest = z.infer<typeof ExplainRequestSchema>;

/**
 * Complete price explanation response.
 * Source: backend/src/schemas/explanation.py::PriceExplanation
 */
export const PriceExplanationSchema = z.object({
  // Core recommendation
  recommendation: PricingResultSchema.describe('Complete pricing recommendation'),

  // Feature importance
  feature_importance: z
    .array(FeatureContributionSchema)
    .describe('Local SHAP-based feature contributions for this prediction'),
  global_importance: z
    .array(FeatureContributionSchema)
    .describe('Model-level global feature importance'),

  // Decision trace
  decision_trace: DecisionTraceSchema.nullable()
    .optional()
    .describe('Step-by-step decision pipeline trace'),

  // Model comparison
  model_agreement: ModelAgreementSchema.describe('Cross-model agreement analysis'),
  model_predictions: z
    .record(z.string(), z.number())
    .describe('Predictions from all available models'),

  // Natural language
  natural_language_summary: z
    .string()
    .describe('Human-readable explanation of the pricing recommendation'),
  key_factors: z
    .array(z.string())
    .describe("Top factors driving the recommendation (e.g., 'High demand', 'Evening peak')"),

  // Metadata
  explanation_time_ms: z
    .number()
    .min(0)
    .describe('Time taken to generate explanation in milliseconds'),
  timestamp: z.string().datetime().describe('Timestamp when explanation was generated'),
});

export type PriceExplanation = z.infer<typeof PriceExplanationSchema>;

