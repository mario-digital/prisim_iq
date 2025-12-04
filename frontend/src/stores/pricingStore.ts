/**
 * Pricing store for managing pricing results and explainability data.
 */

import { create } from 'zustand';
import type { PriceExplanation } from '@/components/visualizations/types';
import type { MarketContext } from '@/stores/contextStore';
import { apiUrl } from '@/lib/api';

interface PricingState {
  /** Current price explanation with all visualization data */
  explanation: PriceExplanation | null;

  /** Loading state for pricing operations */
  isLoading: boolean;

  /** Error message if pricing failed (null = no error) */
  error: string | null;

  /** Fetch pricing explanation from the API */
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
 */
export const usePricingStore = create<PricingState>((set) => ({
  explanation: null,
  isLoading: false,
  error: null,

  fetchPricing: async (context: MarketContext) => {
    set({ isLoading: true, error: null });

    try {
      const response = await fetch(apiUrl('/api/v1/explain_decision'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          context,
          include_trace: true,
          include_shap: true,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `Request failed with status ${response.status}`
        );
      }

      const data = await response.json();

      // Transform backend response to frontend PriceExplanation format
      const explanation: PriceExplanation = transformApiResponse(data);

      set({ explanation, isLoading: false, error: null });
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to fetch pricing';
      set({ error: errorMessage, isLoading: false });
      throw err;
    }
  },

  setExplanation: (explanation) =>
    set({
      explanation,
      isLoading: false,
      error: null,
    }),

  setLoading: (isLoading) =>
    set({
      isLoading,
      error: isLoading ? null : undefined,
    }),

  setError: (error) =>
    set({
      error,
      isLoading: false,
    }),

  clear: () =>
    set({
      explanation: null,
      isLoading: false,
      error: null,
    }),
}));

/**
 * Transform backend PriceExplanation response to frontend format.
 * Maps snake_case API response to camelCase frontend types.
 */
function transformApiResponse(data: Record<string, unknown>): PriceExplanation {
  const recommendation = data.recommendation as Record<string, unknown>;
  const segment = recommendation?.segment as Record<string, unknown> | undefined;
  const priceDemandCurve =
    (recommendation?.price_demand_curve as Array<{
      price: number;
      demand: number;
      profit: number;
    }>) || [];

  // Derive confidence level from score
  const confidenceScore = (recommendation?.confidence_score as number) || 0;
  const confidence: 'low' | 'medium' | 'high' =
    confidenceScore >= 0.8 ? 'high' : confidenceScore >= 0.5 ? 'medium' : 'low';

  // Map feature importance to pricing factors
  const featureImportance =
    (data.feature_importance as Array<Record<string, unknown>>) || [];
  const factors = featureImportance.map((f) => ({
    name: (f.display_name as string) || (f.feature_name as string) || '',
    impact: (f.importance as number) || 0,
    description: (f.description as string) || '',
    weight: (f.importance as number) || 0,
  }));

  const recommendedPrice = (recommendation?.recommended_price as number) || 0;
  const expectedDemand = (recommendation?.expected_demand as number) || 0;

  // Map backend segment name to frontend CustomerSegment type
  const segmentName = ((segment?.segment_name as string) || '').toLowerCase();
  const mappedSegment: 'price_sensitive' | 'value_seeker' | 'premium' | 'enterprise' =
    segmentName.includes('premium') || segmentName.includes('peak')
      ? 'premium'
      : segmentName.includes('value') || segmentName.includes('urban')
        ? 'value_seeker'
        : segmentName.includes('enterprise') || segmentName.includes('business')
          ? 'enterprise'
          : 'price_sensitive';

  return {
    result: {
      recommendedPrice,
      basePrice: (recommendation?.price_before_rules as number) || recommendedPrice,
      priceAdjustment:
        recommendedPrice > 0 && recommendation?.price_before_rules
          ? ((recommendedPrice - (recommendation.price_before_rules as number)) /
              (recommendation.price_before_rules as number)) *
            100
          : 0,
      confidence,
      confidenceScore,
      segment: mappedSegment,
      factors,
      expectedDemand,
      expectedRevenue: recommendedPrice * expectedDemand,
      explanation:
        (data.natural_language_summary as string) ||
        `Recommended price: $${recommendedPrice.toFixed(2)}`,
      timestamp: (recommendation?.timestamp as string) || new Date().toISOString(),
    },
    featureContributions: featureImportance.map((f) => ({
      name: (f.feature_name as string) || '',
      displayName: (f.display_name as string) || (f.feature_name as string) || '',
      importance: (f.importance as number) || 0,
      direction: (f.direction as 'positive' | 'negative' | 'neutral') || 'neutral',
      currentValue: (f.current_value ?? f.description ?? '') as string | number,
    })),
    decisionTrace: (
      ((data.decision_trace as Record<string, unknown>)?.steps as Array<
        Record<string, unknown>
      >) || []
    ).map((step) => ({
      id: (step.step_name as string) || '',
      name: (step.step_name as string) || '',
      description: (step.description as string) || '',
      durationMs: (step.duration_ms as number) || 0,
      status: (step.status as 'success' | 'warning' | 'error') || 'success',
      inputs: (step.inputs as Record<string, unknown>) || {},
      outputs: (step.outputs as Record<string, unknown>) || {},
    })),
    demandCurve: priceDemandCurve.map((p) => ({
      price: p.price,
      value: p.demand,
    })),
    profitCurve: priceDemandCurve.map((p) => ({
      price: p.price,
      value: p.profit,
    })),
    sensitivity: {
      basePrice: recommendedPrice,
      lowerBound: recommendedPrice * 0.9,
      upperBound: recommendedPrice * 1.1,
      robustnessScore: confidenceScore,
      pricePoints: priceDemandCurve.map((p) => ({
        price: p.price,
        value: p.profit,
      })),
      confidenceLevel: 95,
    },
    businessRules: (
      (recommendation?.rules_applied as Array<Record<string, unknown>>) || []
    ).map((rule) => ({
      id: (rule.rule_id as string) || '',
      name: (rule.rule_name as string) || '',
      description: (rule.description as string) || '',
      triggered: true,
      priceBefore: (rule.price_before as number) || 0,
      priceAfter: (rule.price_after as number) || 0,
      impact: (rule.impact as number) || 0,
      type:
        (rule.type as
          | 'floor'
          | 'ceiling'
          | 'margin'
          | 'competitive'
          | 'promotional') || 'margin',
    })),
    optimalPrice: recommendedPrice,
    expectedProfit: (recommendation?.expected_profit as number) || 0,
    profitUpliftPercent: (recommendation?.profit_uplift_percent as number) || 0,
  };
}

