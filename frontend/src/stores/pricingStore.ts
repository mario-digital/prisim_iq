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
 */

import { create } from 'zustand';
import type { PriceExplanation } from '@/components/visualizations/types';
import type { MarketContext } from './contextStore';
import { apiUrl } from '@/lib/api';

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
      const response = await fetch(apiUrl('/api/v1/explain-decision'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(context),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `Request failed with status ${response.status}`
        );
      }

      const data: PriceExplanation = await response.json();
      set({
        explanation: data,
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
