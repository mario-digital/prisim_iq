/**
 * Evidence and Honeywell mapping response schemas.
 * Source: backend/src/schemas/evidence.py
 */
import { z } from 'zod';

// ----- Model Card Schemas -----

export const ModelHyperparametersSchema = z.object({
  learning_rate: z.number().nullable().optional(),
  max_depth: z.number().int().nullable().optional(),
  n_estimators: z.number().int().nullable().optional(),
  fit_intercept: z.boolean().nullable().optional(),
  normalize: z.boolean().nullable().optional(),
});

export type ModelHyperparameters = z.infer<typeof ModelHyperparametersSchema>;

export const ModelDetailsSchema = z.object({
  architecture: z.string().describe('Model architecture name'),
  hyperparameters: z
    .union([ModelHyperparametersSchema, z.record(z.string(), z.union([z.number(), z.string(), z.boolean()]))])
    .describe('Training hyperparameters'),
  training_date: z.string().describe('Date model was trained'),
  framework: z.string().describe('ML framework used'),
  input_features: z.array(z.string()).describe('Features used by the model'),
  output: z.string().describe('Model output description'),
});

export type ModelDetails = z.infer<typeof ModelDetailsSchema>;

export const IntendedUseSchema = z.object({
  primary_use: z.string().describe('Primary use case'),
  users: z.array(z.string()).describe('Intended user groups'),
  out_of_scope: z.array(z.string()).describe('Uses that are out of scope'),
});

export type IntendedUse = z.infer<typeof IntendedUseSchema>;

export const TrainingDataSchema = z.object({
  dataset_name: z.string().describe('Name of training dataset'),
  dataset_size: z.number().int().describe('Number of samples'),
  features_used: z.array(z.string()).describe('Features in training data'),
  target_variable: z.string().describe('Target variable name'),
  train_test_split: z.string().describe('Train/test split description'),
});

export type TrainingData = z.infer<typeof TrainingDataSchema>;

export const ModelMetricsSchema = z.object({
  r2_score: z.number().describe('R² coefficient of determination'),
  mae: z.number().describe('Mean Absolute Error'),
  rmse: z.number().describe('Root Mean Square Error'),
  test_set_size: z.number().int().describe('Size of test set'),
});

export type ModelMetrics = z.infer<typeof ModelMetricsSchema>;

export const EthicalConsiderationsSchema = z.object({
  fairness_considerations: z.array(z.string()).describe('Fairness notes'),
  privacy_considerations: z.array(z.string()).describe('Privacy notes'),
  transparency_notes: z.array(z.string()).describe('Transparency notes'),
});

export type EthicalConsiderations = z.infer<typeof EthicalConsiderationsSchema>;

/**
 * Complete model card following ML model card standards.
 * Source: backend/src/schemas/evidence.py::ModelCard
 */
export const ModelCardSchema = z.object({
  model_name: z.string().describe('Name of the model'),
  model_version: z.string().describe('Version string'),
  generated_at: z.string().datetime().describe('When card was generated'),
  model_details: ModelDetailsSchema.describe('Model architecture details'),
  intended_use: IntendedUseSchema.describe('Intended use cases'),
  training_data: TrainingDataSchema.describe('Training data info'),
  metrics: ModelMetricsSchema.describe('Performance metrics'),
  ethical_considerations: EthicalConsiderationsSchema.describe('Ethical notes'),
  limitations: z.array(z.string()).describe('Known limitations'),
  feature_importance: z
    .record(z.string(), z.number())
    .nullable()
    .optional()
    .describe('Feature importance scores (None for linear models)'),
  coefficients: z
    .record(z.string(), z.number())
    .nullable()
    .optional()
    .describe('Model coefficients (for linear models)'),
});

export type ModelCard = z.infer<typeof ModelCardSchema>;

// ----- Data Card Schemas -----

export const DistributionType = z.enum(['continuous', 'categorical']);

export const DataFeatureSchema = z.object({
  name: z.string().describe('Feature name'),
  dtype: z.string().describe('Data type'),
  description: z.string().describe('Feature description'),
  range_or_values: z.string().describe('Value range or categories'),
  distribution: DistributionType.describe('Distribution type'),
});

export type DataFeature = z.infer<typeof DataFeatureSchema>;

export const DataSourceSchema = z.object({
  origin: z.string().describe('Data origin'),
  collection_date: z.string().describe('When data was collected'),
  preprocessing_steps: z.array(z.string()).describe('Preprocessing applied'),
});

export type DataSource = z.infer<typeof DataSourceSchema>;

export const DataStatisticsSchema = z.object({
  row_count: z.number().int().describe('Number of rows'),
  column_count: z.number().int().describe('Number of columns'),
  missing_values: z.number().int().describe('Count of missing values'),
  numeric_features: z.number().int().describe('Number of numeric features'),
  categorical_features: z.number().int().describe('Number of categorical features'),
});

export type DataStatistics = z.infer<typeof DataStatisticsSchema>;

/**
 * Data card documenting the training dataset.
 * Source: backend/src/schemas/evidence.py::DataCard
 */
export const DataCardSchema = z.object({
  dataset_name: z.string().describe('Name of the dataset'),
  version: z.string().describe('Dataset version'),
  generated_at: z.string().datetime().describe('When card was generated'),
  source: DataSourceSchema.describe('Data source information'),
  features: z.array(DataFeatureSchema).describe('Feature descriptions'),
  statistics: DataStatisticsSchema.describe('Dataset statistics'),
  known_biases: z.array(z.string()).describe('Known biases in data'),
  limitations: z.array(z.string()).describe('Dataset limitations'),
  intended_use: z.string().describe('Intended use description'),
});

export type DataCard = z.infer<typeof DataCardSchema>;

// ----- Methodology Documentation -----

// Recursive type for nested sections
export interface DocSection {
  heading: string;
  content: string;
  subsections?: DocSection[] | null;
}

export const DocSectionSchema: z.ZodType<DocSection> = z.lazy(() =>
  z.object({
    heading: z.string().describe('Section heading'),
    content: z.string().describe('Section content (markdown)'),
    subsections: z.array(DocSectionSchema).nullable().optional().describe('Nested subsections'),
  })
);

export const MethodologyDocSchema = z.object({
  title: z.string().describe('Document title'),
  sections: z.array(DocSectionSchema).describe('Document sections'),
});

export type MethodologyDoc = z.infer<typeof MethodologyDocSchema>;

// ----- Evidence Response -----

/**
 * Complete evidence package for the Evidence tab.
 * Source: backend/src/schemas/evidence.py::EvidenceResponse
 */
export const EvidenceResponseSchema = z.object({
  model_cards: z.array(ModelCardSchema).describe('All model cards'),
  data_card: DataCardSchema.describe('Training data card'),
  methodology: MethodologyDocSchema.describe('Methodology documentation'),
  generated_at: z.string().datetime().describe('When evidence was compiled'),
  cache_ttl_seconds: z.number().int().default(86400).describe('Cache TTL in seconds (24 hours)'),
});

export type EvidenceResponse = z.infer<typeof EvidenceResponseSchema>;

// ----- Honeywell Mapping -----

export const HoneywellCategory = z.enum(['pricing', 'demand', 'supply', 'customer']);

/**
 * Single mapping from ride-sharing to Honeywell concept.
 * Source: backend/src/schemas/evidence.py::HoneywellMapping
 */
export const HoneywellMappingSchema = z.object({
  ride_sharing_concept: z.string().describe('Ride-sharing domain concept'),
  honeywell_equivalent: z.string().describe('Honeywell enterprise equivalent'),
  category: HoneywellCategory.describe('Concept category'),
  rationale: z.string().describe('Why these concepts map'),
  applicability: z.string().describe('How this applies to enterprise'),
});

export type HoneywellMapping = z.infer<typeof HoneywellMappingSchema>;

/**
 * Complete Honeywell mapping response.
 * Source: backend/src/schemas/evidence.py::HoneywellMappingResponse
 */
export const HoneywellMappingResponseSchema = z.object({
  title: z.string().describe('Document title'),
  description: z.string().describe('Overview description'),
  mappings: z.array(HoneywellMappingSchema).describe('All concept mappings'),
  business_context: z.string().describe('Business context explanation'),
  rendered_markdown: z
    .string()
    .nullable()
    .optional()
    .describe('Markdown rendering (if format=markdown)'),
});

export type HoneywellMappingResponse = z.infer<typeof HoneywellMappingResponseSchema>;
export type HoneywellCategoryType = z.infer<typeof HoneywellCategory>;
export type DistributionTypeValue = z.infer<typeof DistributionType>;

