/**
 * Types for explainability visualizations.
 * These extend the shared PricingResult with detailed explanation data.
 */

import type { PricingResult, PricingFactor } from '@prismiq/shared';

/**
 * Feature contribution for feature importance chart.
 */
export interface FeatureContribution {
  /** Feature name (technical) */
  name: string;
  /** Human-readable display name */
  displayName: string;
  /** Importance score (0-1) */
  importance: number;
  /** Direction of impact */
  direction: 'positive' | 'negative' | 'neutral';
  /** Current value of the feature */
  currentValue: string | number;
}

/**
 * Single step in the decision trace pipeline.
 */
export interface DecisionStep {
  /** Step identifier */
  id: string;
  /** Step name */
  name: string;
  /** Step description */
  description: string;
  /** Execution time in ms */
  durationMs: number;
  /** Status of this step */
  status: 'success' | 'warning' | 'error';
  /** Input data for this step */
  inputs: Record<string, unknown>;
  /** Output data from this step */
  outputs: Record<string, unknown>;
}

/**
 * Point on demand/profit curve.
 */
export interface CurvePoint {
  /** Price point */
  price: number;
  /** Value at this price (demand or profit) */
  value: number;
}

/**
 * Sensitivity analysis result.
 */
export interface SensitivityResult {
  /** Base price being analyzed */
  basePrice: number;
  /** Lower bound of confidence interval */
  lowerBound: number;
  /** Upper bound of confidence interval */
  upperBound: number;
  /** Robustness score (0-1) */
  robustnessScore: number;
  /** Price points analyzed */
  pricePoints: CurvePoint[];
  /** Confidence level percentage */
  confidenceLevel: number;
}

/**
 * Business rule that was applied.
 */
export interface BusinessRule {
  /** Rule identifier */
  id: string;
  /** Rule name */
  name: string;
  /** Rule description */
  description: string;
  /** Whether the rule was triggered */
  triggered: boolean;
  /** Price before rule application */
  priceBefore: number;
  /** Price after rule application */
  priceAfter: number;
  /** Impact amount */
  impact: number;
  /** Rule type category */
  type: 'floor' | 'ceiling' | 'margin' | 'competitive' | 'promotional';
}

/**
 * Complete price explanation with all visualization data.
 */
export interface PriceExplanation {
  /** The pricing result */
  result: PricingResult;
  /** Feature contributions for importance chart */
  featureContributions: FeatureContribution[];
  /** Decision trace steps */
  decisionTrace: DecisionStep[];
  /** Demand curve data */
  demandCurve: CurvePoint[];
  /** Profit curve data */
  profitCurve: CurvePoint[];
  /** Sensitivity analysis */
  sensitivity: SensitivityResult;
  /** Business rules applied */
  businessRules: BusinessRule[];
  /** Optimal price point */
  optimalPrice: number;
  /** Expected profit at optimal price */
  expectedProfit: number;
  /** Profit uplift percentage */
  profitUpliftPercent: number;
}


