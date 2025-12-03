/**
 * Explainability schemas for feature importance results.
 * Source: backend/src/schemas/explainability.py
 */
import { z } from 'zod';

export const FeatureDirection = z.enum(['positive', 'negative']);
export const ExplanationType = z.enum(['global', 'local_shap']);

/**
 * A single feature's contribution to a prediction.
 * Source: backend/src/schemas/explainability.py::FeatureContribution
 */
export const FeatureContributionSchema = z.object({
  feature_name: z.string().describe('Internal feature identifier'),
  display_name: z.string().describe('Human-readable feature name'),
  importance: z.number().min(0).max(1).describe('Normalized importance (0-1)'),
  direction: FeatureDirection.describe('Impact direction on prediction'),
  description: z.string().describe('Plain-English explanation'),
});

export type FeatureContribution = z.infer<typeof FeatureContributionSchema>;

/**
 * Complete feature importance result for a prediction.
 * Source: backend/src/schemas/explainability.py::FeatureImportanceResult
 */
export const FeatureImportanceResultSchema = z.object({
  contributions: z.array(FeatureContributionSchema).describe('Ranked feature contributions'),
  model_used: z.string().describe('Model name used for prediction'),
  explanation_type: ExplanationType.describe('Type of explanation'),
  top_3_summary: z.string().describe('Natural language summary of top factors'),
});

export type FeatureImportanceResult = z.infer<typeof FeatureImportanceResultSchema>;
export type FeatureDirectionType = z.infer<typeof FeatureDirection>;
export type ExplanationTypeValue = z.infer<typeof ExplanationType>;

