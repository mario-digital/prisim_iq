/**
 * Central export file for all Zod schemas.
 * These schemas mirror backend Pydantic models for runtime validation.
 *
 * Usage:
 *   import { MarketContextSchema, type MarketContext } from '@prismiq/shared/schemas';
 */

// Common schemas
export { ErrorResponseSchema, type ErrorResponse } from './common';

// Market context schemas
export {
  LocationCategory,
  CustomerLoyaltyStatus,
  TimeOfBooking,
  VehicleType,
  MarketContextSchema,
  getSupplyDemandRatio,
  type MarketContext,
  type LocationCategoryType,
  type CustomerLoyaltyStatusType,
  type TimeOfBookingType,
  type VehicleTypeType,
} from './market';

// Segment schemas
export {
  ConfidenceLevel,
  SegmentResultSchema,
  SegmentDetailsSchema,
  type SegmentResult,
  type SegmentDetails,
  type ConfidenceLevelType,
} from './segment';

// Rules schemas
export {
  AppliedRuleSchema,
  RulesResultSchema,
  type AppliedRule,
  type RulesResult,
} from './rules';

// Optimization schemas
export {
  PriceDemandPointSchema,
  OptimizationResultSchema,
  type PriceDemandPoint,
  type OptimizationResult,
} from './optimization';

// Pricing schemas
export { PricingResultSchema, type PricingResult } from './pricing';

// Chat schemas
export {
  ChatRequestSchema,
  ChatResponseSchema,
  ChatStreamEventSchema,
  type ChatRequest,
  type ChatResponse,
  type ChatStreamEvent,
} from './chat';

// Explainability schemas
export {
  FeatureDirection,
  ExplanationType,
  FeatureContributionSchema,
  FeatureImportanceResultSchema,
  type FeatureContribution,
  type FeatureImportanceResult,
  type FeatureDirectionType,
  type ExplanationTypeValue,
} from './explainability';

// Decision trace schemas
export {
  TraceStepStatus,
  AgreementStatus,
  TraceStepSchema,
  ModelAgreementSchema,
  DecisionTraceSchema,
  type TraceStep,
  type ModelAgreement,
  type DecisionTrace,
  type TraceStepStatusType,
  type AgreementStatusType,
} from './decision-trace';

// Explanation schemas
export {
  ExplainRequestSchema,
  PriceExplanationSchema,
  type ExplainRequest,
  type PriceExplanation,
} from './explanation';

// Evidence schemas
export {
  ModelHyperparametersSchema,
  ModelDetailsSchema,
  IntendedUseSchema,
  TrainingDataSchema,
  ModelMetricsSchema,
  EthicalConsiderationsSchema,
  ModelCardSchema,
  DistributionType,
  DataFeatureSchema,
  DataSourceSchema,
  DataStatisticsSchema,
  DataCardSchema,
  DocSectionSchema,
  MethodologyDocSchema,
  EvidenceResponseSchema,
  HoneywellCategory,
  HoneywellMappingSchema,
  HoneywellMappingResponseSchema,
  type ModelHyperparameters,
  type ModelDetails,
  type IntendedUse,
  type TrainingData,
  type ModelMetrics,
  type EthicalConsiderations,
  type ModelCard,
  type DataFeature,
  type DataSource,
  type DataStatistics,
  type DataCard,
  type DocSection,
  type MethodologyDoc,
  type EvidenceResponse,
  type HoneywellMapping,
  type HoneywellMappingResponse,
  type HoneywellCategoryType,
  type DistributionTypeValue,
} from './evidence';

// Sensitivity schemas
export {
  ScenarioType,
  ScenarioResultSchema,
  ConfidenceBandSchema,
  SensitivityResultSchema,
  SensitivityPointSchema,
  MarketContextSummarySchema,
  ScenarioSummarySchema,
  SensitivityResponseSchema,
  type ScenarioResult,
  type ConfidenceBand,
  type SensitivityResult,
  type SensitivityPoint,
  type MarketContextSummary,
  type ScenarioSummary,
  type SensitivityResponse,
  type ScenarioTypeValue,
} from './sensitivity';

// Health schemas
export {
  HealthStatus,
  HealthResponseSchema,
  ModelInfoSchema,
  ModelsStatusResponseSchema,
  type HealthResponse,
  type HealthStatusType,
  type ModelInfo,
  type ModelsStatusResponse,
} from './health';

// Data schemas
export {
  PriceRangeSchema,
  DataSummaryResponseSchema,
  type PriceRange,
  type DataSummaryResponse,
} from './data';

