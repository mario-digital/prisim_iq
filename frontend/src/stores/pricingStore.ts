/**
 * Pricing store for managing pricing results and explainability data.
 */

import { create } from 'zustand';
import type { PriceExplanation } from '@/components/visualizations/types';
import type { MarketContext } from '@/stores/contextStore';
import { apiUrl } from '@/lib/api';
import { MarketContextSchema, PriceExplanationSchema } from '@prismiq/shared/schemas';
import { useStatusStore } from '@/stores/statusStore';

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
    const startTime = performance.now();

    // Get statusStore actions for updating footer stats
    const { setSegment, completeProcessing, startProcessing } = useStatusStore.getState();
    startProcessing();

    try {
      // Validate context using shared Zod schema before API call
      const validation = MarketContextSchema.safeParse(context);
      if (!validation.success) {
        const errorMessages = validation.error.issues
          .map((issue) => `${issue.path.join('.')}: ${issue.message}`)
          .join('; ');
        throw new Error(`Validation failed: ${errorMessages}`);
      }

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
        // Handle various error formats from FastAPI
        let errorMessage = `Request failed with status ${response.status}`;
        if (errorData.detail) {
          if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          } else if (Array.isArray(errorData.detail)) {
            // FastAPI validation errors return an array of error objects
            errorMessage = errorData.detail
              .map((e: { msg?: string; loc?: string[] }) => 
                e.msg || (e.loc ? `Error in ${e.loc.join('.')}` : 'Unknown error')
              )
              .join('; ');
          } else if (typeof errorData.detail === 'object') {
            // Single error object
            errorMessage = errorData.detail.msg || JSON.stringify(errorData.detail);
          }
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();

      // Validate response against shared schema (logs warning but doesn't block)
      // This helps detect API drift early in development
      const responseValidation = PriceExplanationSchema.safeParse(data);
      if (!responseValidation.success) {
        console.warn('[pricingStore] API response doesn\'t match expected schema:', 
          responseValidation.error.issues.map(i => `${i.path.join('.')}: ${i.message}`).join('; ')
        );
        // Continue anyway - transformApiResponse has defensive defaults
      }

      // Transform backend response to frontend PriceExplanation format
      const explanation: PriceExplanation = transformApiResponse(data);

      // Calculate response time and update status store
      const responseTimeSeconds = (performance.now() - startTime) / 1000;
      
      // Extract segment name from response for footer display
      const recommendation = (data?.recommendation as Record<string, unknown>) ?? {};
      const segment = (recommendation?.segment as Record<string, unknown>) ?? {};
      const segmentName = String(segment?.segment_name ?? 'Unknown');
      
      // Update footer stats
      setSegment(segmentName);
      completeProcessing(responseTimeSeconds);

      set({ explanation, isLoading: false, error: null });
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to fetch pricing';
      set({ error: errorMessage, isLoading: false });
      
      // Still update response time on error
      const responseTimeSeconds = (performance.now() - startTime) / 1000;
      completeProcessing(responseTimeSeconds);
      
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
 *
 * BACKEND CONTRACT: This transformer assumes the backend /api/v1/explain_decision
 * response follows the PriceExplanation schema from src/schemas/explanation.py.
 * All field access uses defensive defaults (|| '', || 0, || []) to handle:
 * - Missing optional fields
 * - Null values from backend
 * - Schema evolution where new fields may be absent in older responses
 *
 * If backend schema changes significantly, update this transformer accordingly.
 */
function transformApiResponse(data: Record<string, unknown>): PriceExplanation {
  // Safely extract top-level objects with null checks
  const recommendation = (data?.recommendation as Record<string, unknown>) ?? {};
  const segment = (recommendation?.segment as Record<string, unknown>) ?? {};

  // Extract price_demand_curve with type guard for array
  const rawCurve = recommendation?.price_demand_curve;
  const priceDemandCurve: Array<{ price: number; demand: number; profit: number }> =
    Array.isArray(rawCurve)
      ? rawCurve.map((p) => ({
          price: typeof p?.price === 'number' ? p.price : 0,
          demand: typeof p?.demand === 'number' ? p.demand : 0,
          profit: typeof p?.profit === 'number' ? p.profit : 0,
        }))
      : [];

  // Derive confidence level from score with defensive number extraction
  const rawConfidence = recommendation?.confidence_score;
  const confidenceScore = typeof rawConfidence === 'number' ? rawConfidence : 0;
  const confidence: 'low' | 'medium' | 'high' =
    confidenceScore >= 0.8 ? 'high' : confidenceScore >= 0.5 ? 'medium' : 'low';

  // Map feature importance to pricing factors with defensive array handling
  const rawFeatures = data?.feature_importance;
  const featureImportance: Array<Record<string, unknown>> = Array.isArray(rawFeatures)
    ? rawFeatures
    : [];
  const factors = featureImportance.map((f) => ({
    name: String(f?.display_name ?? f?.feature_name ?? ''),
    impact: typeof f?.importance === 'number' ? f.importance : 0,
    description: String(f?.description ?? ''),
    weight: typeof f?.importance === 'number' ? f.importance : 0,
  }));

  // Extract numeric values with type guards
  const rawPrice = recommendation?.recommended_price;
  const recommendedPrice = typeof rawPrice === 'number' ? rawPrice : 0;
  const rawDemand = recommendation?.expected_demand;
  const expectedDemand = typeof rawDemand === 'number' ? rawDemand : 0;

  // Map backend segment name to frontend CustomerSegment type
  // Default to 'price_sensitive' if segment info is missing/malformed
  const segmentName = String(segment?.segment_name ?? '').toLowerCase();
  const mappedSegment: 'price_sensitive' | 'value_seeker' | 'premium' | 'enterprise' =
    segmentName.includes('premium') || segmentName.includes('peak')
      ? 'premium'
      : segmentName.includes('value') || segmentName.includes('urban')
        ? 'value_seeker'
        : segmentName.includes('enterprise') || segmentName.includes('business')
          ? 'enterprise'
          : 'price_sensitive';

  // Extract base price with fallback to recommended price
  const rawBasePrice = recommendation?.price_before_rules;
  const basePrice = typeof rawBasePrice === 'number' ? rawBasePrice : recommendedPrice;

  // Calculate price adjustment percentage safely
  const priceAdjustment =
    recommendedPrice > 0 && basePrice > 0
      ? ((recommendedPrice - basePrice) / basePrice) * 100
      : 0;

  return {
    result: {
      recommendedPrice,
      basePrice,
      priceAdjustment,
      confidence,
      confidenceScore,
      segment: mappedSegment,
      factors,
      expectedDemand,
      expectedRevenue: recommendedPrice * expectedDemand,
      explanation:
        String(data?.natural_language_summary ?? '') ||
        `Recommended price: $${recommendedPrice.toFixed(2)}`,
      timestamp: String(recommendation?.timestamp ?? '') || new Date().toISOString(),
    },
    featureContributions: featureImportance.map((f) => {
      // Validate direction is one of expected values, default to 'neutral'
      const rawDirection = f?.direction;
      const direction: 'positive' | 'negative' | 'neutral' =
        rawDirection === 'positive' || rawDirection === 'negative'
          ? rawDirection
          : 'neutral';
      return {
        name: String(f?.feature_name ?? ''),
        displayName: String(f?.display_name ?? f?.feature_name ?? ''),
        importance: typeof f?.importance === 'number' ? f.importance : 0,
        direction,
        currentValue: String(f?.current_value ?? f?.description ?? ''),
      };
    }),
    decisionTrace: (() => {
      const trace = data?.decision_trace as Record<string, unknown> | undefined;
      const steps = Array.isArray(trace?.steps) ? trace.steps : [];
      return steps.map((step: Record<string, unknown>) => {
        // Validate status is one of expected values
        const rawStatus = step?.status;
        const status: 'success' | 'warning' | 'error' =
          rawStatus === 'warning' || rawStatus === 'error' ? rawStatus : 'success';
        return {
          id: String(step?.step_name ?? ''),
          name: String(step?.step_name ?? ''),
          description: String(step?.description ?? ''),
          durationMs: typeof step?.duration_ms === 'number' ? step.duration_ms : 0,
          status,
          inputs: (step?.inputs as Record<string, unknown>) ?? {},
          outputs: (step?.outputs as Record<string, unknown>) ?? {},
        };
      });
    })(),
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
    businessRules: (() => {
      const rawRules = recommendation?.rules_applied;
      const rules: Array<Record<string, unknown>> = Array.isArray(rawRules) ? rawRules : [];
      return rules.map((rule) => {
        // Validate rule type is one of expected values
        const rawType = rule?.type;
        const validTypes = ['floor', 'ceiling', 'margin', 'competitive', 'promotional'] as const;
        const type: (typeof validTypes)[number] =
          validTypes.includes(rawType as (typeof validTypes)[number])
            ? (rawType as (typeof validTypes)[number])
            : 'margin';
        return {
          id: String(rule?.rule_id ?? ''),
          name: String(rule?.rule_name ?? ''),
          description: String(rule?.description ?? ''),
          triggered: true,
          priceBefore: typeof rule?.price_before === 'number' ? rule.price_before : 0,
          priceAfter: typeof rule?.price_after === 'number' ? rule.price_after : 0,
          impact: typeof rule?.impact === 'number' ? rule.impact : 0,
          type,
        };
      });
    })(),
    optimalPrice: recommendedPrice,
    expectedProfit:
      typeof recommendation?.expected_profit === 'number'
        ? recommendation.expected_profit
        : 0,
    profitUpliftPercent:
      typeof recommendation?.profit_uplift_percent === 'number'
        ? recommendation.profit_uplift_percent
        : 0,
  };
}

