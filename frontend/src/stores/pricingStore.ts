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

  /** Error message if pricing failed */
  error: string | null;

  /** Set the complete explanation data */
  setExplanation: (explanation: PriceExplanation) => void;

  /** Set loading state */
  setLoading: (isLoading: boolean) => void;

  /** Set error state */
  setError: (error: string | null) => void;

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

  clear: () =>
    set({
      explanation: null,
      isLoading: false,
      error: null,
    }),
}));

