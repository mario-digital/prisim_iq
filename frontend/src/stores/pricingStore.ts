/**
 * Pricing store for managing pricing results and explainability data.
 */

import { create } from 'zustand';
import type { PriceExplanation } from '@/components/visualizations/types';

interface PricingState {
  /** Current price explanation with all visualization data */
  explanation: PriceExplanation | null;

  /** Loading state for pricing operations */
  isLoading: boolean;

  /** Error message if pricing failed (null = no error) */
  error: string | null;

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

