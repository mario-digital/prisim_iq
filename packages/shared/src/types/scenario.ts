/**
 * Scenario and sensitivity analysis types.
 */

import type { MarketContext } from './market';
import type { PricingResult } from './pricing';

/**
 * Single scenario definition.
 */
export interface Scenario {
  /** Unique scenario ID */
  id: string;
  
  /** Human-readable name */
  name: string;
  
  /** Description of what this scenario represents */
  description: string;
  
  /** Market context for this scenario */
  context: MarketContext;
  
  /** Tags for categorization */
  tags?: string[];
}

/**
 * Result of running a scenario.
 */
export interface ScenarioResult {
  /** The scenario that was run */
  scenario: Scenario;
  
  /** Pricing result for this scenario */
  result: PricingResult;
  
  /** Comparison to baseline if available */
  comparison?: ScenarioComparison;
}

/**
 * Comparison between two scenario results.
 */
export interface ScenarioComparison {
  /** Price difference */
  priceDelta: number;
  
  /** Price difference percentage */
  priceDeltaPercent: number;
  
  /** Revenue difference */
  revenueDelta: number;
  
  /** Demand difference */
  demandDelta: number;
  
  /** Key differences in factors */
  factorChanges: FactorChange[];
}

/**
 * Change in a pricing factor between scenarios.
 */
export interface FactorChange {
  /** Factor name */
  factor: string;
  
  /** Previous impact */
  previousImpact: number;
  
  /** New impact */
  newImpact: number;
  
  /** Delta */
  delta: number;
}

/**
 * Sensitivity analysis request.
 */
export interface SensitivityRequest {
  /** Base context to analyze */
  baseContext: MarketContext;
  
  /** Variable to sweep */
  variable: keyof MarketContext;
  
  /** Minimum value for sweep */
  minValue: number;
  
  /** Maximum value for sweep */
  maxValue: number;
  
  /** Number of steps */
  steps: number;
}

/**
 * Single point in sensitivity analysis.
 */
export interface SensitivityPoint {
  /** Variable value */
  value: number;
  
  /** Resulting price */
  price: number;
  
  /** Expected demand */
  demand: number;
  
  /** Expected revenue */
  revenue: number;
}

/**
 * Complete sensitivity analysis result.
 */
export interface SensitivityResult {
  /** Variable that was swept */
  variable: string;
  
  /** All data points */
  points: SensitivityPoint[];
  
  /** Optimal value found */
  optimalValue: number;
  
  /** Price at optimal value */
  optimalPrice: number;
  
  /** Maximum revenue found */
  maxRevenue: number;
}

