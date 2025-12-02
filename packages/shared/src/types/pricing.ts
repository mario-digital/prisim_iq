/**
 * Pricing result types for optimization responses.
 */

import type { CustomerSegment } from './market';

/**
 * Confidence level for pricing recommendation.
 */
export type ConfidenceLevel = 'low' | 'medium' | 'high';

/**
 * Individual factor contributing to pricing decision.
 */
export interface PricingFactor {
  /** Factor name */
  name: string;
  
  /** Contribution to final price (can be positive or negative) */
  impact: number;
  
  /** Human-readable description */
  description: string;
  
  /** Importance weight (0-1) */
  weight: number;
}

/**
 * Complete pricing result with explanation.
 */
export interface PricingResult {
  /** Recommended price */
  recommendedPrice: number;
  
  /** Original base price */
  basePrice: number;
  
  /** Price adjustment percentage */
  priceAdjustment: number;
  
  /** Confidence in recommendation */
  confidence: ConfidenceLevel;
  
  /** Confidence score (0-1) */
  confidenceScore: number;
  
  /** Customer segment used */
  segment: CustomerSegment;
  
  /** Factors that influenced the decision */
  factors: PricingFactor[];
  
  /** Expected demand at this price */
  expectedDemand: number;
  
  /** Expected revenue at this price */
  expectedRevenue: number;
  
  /** Natural language explanation */
  explanation: string;
  
  /** Alternative prices to consider */
  alternatives?: AlternativePrice[];
  
  /** Timestamp of calculation */
  timestamp: string;
}

/**
 * Alternative price option.
 */
export interface AlternativePrice {
  /** Alternative price */
  price: number;
  
  /** Expected demand at this price */
  expectedDemand: number;
  
  /** Expected revenue */
  expectedRevenue: number;
  
  /** Tradeoff description */
  tradeoff: string;
}

