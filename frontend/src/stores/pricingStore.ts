/**
 * Pricing store for managing pricing results and explainability data.
 *
 * DESIGN DECISION: This store is intentionally ephemeral (not persisted).
 *
 * Rationale:
 * - Pricing results are context-specific to current market conditions
 * - Persisted stale pricing data could mislead users into wrong decisions
 * - Each session should fetch fresh data reflecting real-time market state
 * - The API is the source of truth, not localStorage
 *
 * If historic pricing analysis is needed, consider a separate "pricing history"
 * feature with proper timestamps and context preservation.
 * 
 * TRANSFORMATION NOTE:
 * The backend returns data in snake_case format matching the Pydantic schemas.
 * The frontend UI components expect camelCase format with different structure.
 * The transformExplanation function bridges this gap.
 */

import { create } from 'zustand';
import type { PriceExplanation } from '@/components/visualizations/types';
import type { MarketContext } from './contextStore';
import { apiUrl } from '@/lib/api';

/**
 * Backend API response type for /explain_decision endpoint.
 * This matches the actual backend schema (snake_case).
 */
interface BackendPriceExplanation {
  recommendation: {
    recommended_price: number;
    confidence_score: number;
    expected_demand: number;
    expected_profit: number;
    baseline_profit: number;
    profit_uplift_percent: number;
    segment: {
      segment_name: string;
      cluster_id: number;
      characteristics: Record<string, unknown>;
      centroid_distance: number;
      human_readable_description: string;
      confidence_level: 'low' | 'medium' | 'high';
    };
    model_used: string;
    rules_applied: Array<{
      rule_name: string;
      condition: string;
      action: string;
      was_triggered: boolean;
      price_impact: number;
    }>;
    price_before_rules: number;
    price_demand_curve: Array<{ price: number; demand: number }>;
    processing_time_ms: number;
    timestamp: string;
  };
  feature_importance: Array<{
    feature_name: string;
    display_name: string;
    importance: number;
    direction: 'positive' | 'negative';
    description: string;
  }>;
  global_importance: Array<{
    feature_name: string;
    display_name: string;
    importance: number;
    direction: 'positive' | 'negative';
    description: string;
  }>;
  decision_trace?: {
    steps: Array<{
      name: string;
      input: Record<string, unknown>;
      output: Record<string, unknown>;
      duration_ms: number;
      status: 'success' | 'warning' | 'error';
      message?: string;
    }>;
    total_duration_ms: number;
  } | null;
  model_agreement: {
    models_compared: string[];
    predictions: Record<string, number>;
    max_deviation_percent: number;
    is_agreement: boolean;
    status: 'full_agreement' | 'partial_agreement' | 'disagreement';
  };
  model_predictions: Record<string, number>;
  natural_language_summary: string;
  key_factors: string[];
  explanation_time_ms: number;
  timestamp: string;
}

/**
 * Map backend segment to frontend segment type.
 * Note: Frontend expects a string enum but backend returns complex object.
 */
function mapSegment(segment: BackendPriceExplanation['recommendation']['segment']): 'price_sensitive' | 'value_seeker' | 'premium' | 'enterprise' {
  // Map based on segment name or characteristics
  const name = segment.segment_name.toLowerCase();
  if (name.includes('premium')) return 'premium';
  if (name.includes('enterprise') || name.includes('business')) return 'enterprise';
  if (name.includes('value') || name.includes('budget')) return 'value_seeker';
  return 'price_sensitive';
}

/**
 * Transform backend API response to frontend UI format.
 * This bridges the gap between backend snake_case and frontend camelCase types.
 */
function transformExplanation(backend: BackendPriceExplanation): PriceExplanation {
  const { recommendation } = backend;

  return {
    result: {
      recommendedPrice: recommendation.recommended_price,
      basePrice: recommendation.price_before_rules,
      priceAdjustment: ((recommendation.recommended_price - recommendation.price_before_rules) / recommendation.price_before_rules) * 100,
      confidence: recommendation.confidence_score >= 0.8 ? 'high' :
        recommendation.confidence_score >= 0.5 ? 'medium' : 'low',
      confidenceScore: recommendation.confidence_score,
      segment: mapSegment(recommendation.segment),
      factors: backend.feature_importance.map((f) => ({
        name: f.feature_name,
        impact: f.importance,
        description: f.description,
        weight: f.importance,
      })),
      expectedDemand: recommendation.expected_demand,
      expectedRevenue: recommendation.expected_profit / (recommendation.expected_demand || 0.5), // Rough approximation
      explanation: backend.natural_language_summary,
      timestamp: recommendation.timestamp,
    },
    featureContributions: backend.feature_importance.map((f) => ({
      name: f.feature_name,
      displayName: f.display_name,
      importance: f.importance,
      direction: f.direction === 'positive' ? 'positive' :
        f.direction === 'negative' ? 'negative' : 'neutral',
      currentValue: f.description,
    })),
    decisionTrace: backend.decision_trace?.steps.map((step, index) => ({
      id: `step-${index}`,
      name: step.name,
      description: step.message || `Processed ${step.name}`,
      durationMs: step.duration_ms,
      status: step.status,
      inputs: step.input,
      outputs: step.output,
    })) || [],
    demandCurve: recommendation.price_demand_curve.map((p) => ({
      price: p.price,
      value: p.demand,
    })),
    profitCurve: recommendation.price_demand_curve.map((p) => ({
      price: p.price,
      value: p.price * p.demand, // Revenue as proxy for profit curve
    })),
    sensitivity: {
      basePrice: recommendation.recommended_price,
      lowerBound: recommendation.recommended_price * 0.9,
      upperBound: recommendation.recommended_price * 1.1,
      robustnessScore: recommendation.confidence_score,
      pricePoints: recommendation.price_demand_curve.map((p) => ({
        price: p.price,
        value: p.demand,
      })),
      confidenceLevel: recommendation.confidence_score * 100,
    },
    businessRules: recommendation.rules_applied.map((rule, index) => ({
      id: `rule-${index}`,
      name: rule.rule_name,
      description: `${rule.condition} → ${rule.action}`,
      triggered: rule.was_triggered,
      priceBefore: recommendation.price_before_rules,
      priceAfter: recommendation.recommended_price,
      impact: rule.price_impact,
      type: 'margin' as const, // Default type since backend doesn't specify
    })),
    optimalPrice: recommendation.recommended_price,
    expectedProfit: recommendation.expected_profit,
    profitUpliftPercent: recommendation.profit_uplift_percent,
  };
}

interface PricingState {
  /** Current price explanation with all visualization data */
  explanation: PriceExplanation | null;

  /** Loading state for pricing operations */
  isLoading: boolean;

  /** Error message if pricing failed (null = no error) */
  error: string | null;

  /** Fetch pricing explanation for a market context */
  fetchPricing: (context: MarketContext) => Promise<void>;

  /** Set the complete explanation data (clears loading and error) */
  setExplanation: (explanation: PriceExplanation) => void;

  /** Set loading state with explicit error handling */
  setLoading: (isLoading: boolean) => void;

  /** Set error state (clears loading) */
  setError: (error: string | null) => void;

  /** Clear all pricing data to initial state */
  clear: () => void;
}

/** Initial state for the pricing store */
const INITIAL_STATE = {
  explanation: null,
  isLoading: false,
  error: null,
} as const;

/**
 * Store for managing pricing results and explainability data.
 * Used by the ExplainabilityPanel to display visualization components.
 *
 * State transitions:
 * - setLoading(true)  → clears error, sets loading
 * - setLoading(false) → only clears loading (error preserved for display)
 * - setExplanation()  → clears loading AND error, sets data
 * - setError()        → clears loading, sets error
 * - clear()           → resets to initial state
 */
export const usePricingStore = create<PricingState>((set) => ({
  ...INITIAL_STATE,

  fetchPricing: async (context: MarketContext) => {
    set({ isLoading: true, error: null });

    try {
      const response = await fetch(apiUrl('/api/v1/explain_decision'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ context }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `Request failed with status ${response.status}`
        );
      }

      const backendData: BackendPriceExplanation = await response.json();
      const explanation = transformExplanation(backendData);

      set({
        explanation,
        isLoading: false,
        error: null,
      });
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to fetch pricing';
      set({
        error: message,
        isLoading: false,
      });
    }
  },

  setExplanation: (explanation) =>
    set({
      explanation,
      isLoading: false,
      error: null,
    }),

  setLoading: (isLoading) =>
    set((state) => ({
      isLoading,
      // Clear error when starting new operation; preserve when stopping
      // This allows error messages to remain visible after loading completes
      error: isLoading ? null : state.error,
    })),

  setError: (error) =>
    set({
      error,
      isLoading: false,
    }),

  clear: () => set(INITIAL_STATE),
}));
