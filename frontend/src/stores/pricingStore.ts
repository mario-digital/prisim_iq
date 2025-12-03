/**
 * Pricing store for managing pricing results and explainability data.
 */

import { create } from 'zustand';
import type { PriceExplanation } from '@/components/visualizations/types';
import type { MarketContext } from './contextStore';
import { apiUrl, apiConfig } from '@/lib/api';

interface PricingState {
  /** Current price explanation with all visualization data */
  explanation: PriceExplanation | null;

  /** Loading state for pricing operations */
  isLoading: boolean;

  /** Error message if pricing failed */
  error: string | null;

  /** Set the complete explanation data */
  setExplanation: (explanation: PriceExplanation) => void;

  /** Set loading state */
  setLoading: (isLoading: boolean) => void;

  /** Set error state */
  setError: (error: string | null) => void;

  /** Fetch pricing from API with market context */
  fetchPricing: (context: MarketContext) => Promise<void>;

  /** Clear all pricing data */
  clear: () => void;
}

/**
 * Store for managing pricing results and explainability data.
 * Used by the ExplainabilityPanel to display visualization components.
 */
export const usePricingStore = create<PricingState>((set) => ({
  explanation: null,
  isLoading: false,
  error: null,

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

  fetchPricing: async (context: MarketContext) => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetch(apiUrl(apiConfig.endpoints.optimize), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(context),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `API error: ${response.status}`);
      }

      const data = await response.json();
      
      // Transform API response to PriceExplanation format
      // The API returns the core pricing result, we build the explanation structure
      set({
        explanation: {
          result: data,
          featureContributions: data.feature_contributions || [],
          decisionTrace: data.decision_trace || [],
          demandCurve: data.demand_curve || [],
          profitCurve: data.profit_curve || [],
          sensitivity: data.sensitivity || {
            basePrice: data.optimal_price || 0,
            lowerBound: 0,
            upperBound: 0,
            robustnessScore: 0,
            pricePoints: [],
            confidenceLevel: 95,
          },
          businessRules: data.business_rules || [],
          optimalPrice: data.optimal_price || 0,
          expectedProfit: data.expected_profit || 0,
          profitUpliftPercent: data.profit_uplift_percent || 0,
        },
        isLoading: false,
        error: null,
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch pricing';
      set({ error: message, isLoading: false });
    }
  },

  clear: () =>
    set({
      explanation: null,
      isLoading: false,
      error: null,
    }),
}));

