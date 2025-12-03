/**
 * Explainability visualization components.
 */

export { ExplainabilityPanel } from './ExplainabilityPanel';
export { RecommendationCard } from './RecommendationCard';
export { FeatureImportanceChart } from './FeatureImportanceChart';
export { DecisionTrace } from './DecisionTrace';
export { DemandCurveChart } from './DemandCurveChart';
export { ProfitCurveChart } from './ProfitCurveChart';
export { SensitivitySection } from './SensitivitySection';
export { SensitivityBandChart } from './SensitivityBandChart';
export { SegmentPerformanceChart } from './SegmentPerformanceChart';
export { BusinessRulesList } from './BusinessRulesList';

// Chart shared utilities
export * from './charts/shared';

export type {
  FeatureContribution,
  DecisionStep,
  CurvePoint,
  SensitivityResult,
  BusinessRule,
  PriceExplanation,
} from './types';

export type { SensitivityBandPoint } from './SensitivityBandChart';
export type { SegmentPerformanceData } from './SegmentPerformanceChart';

