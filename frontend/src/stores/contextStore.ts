'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { MarketContext } from '@prismiq/shared/schemas';

// Re-export the shared MarketContext type for convenience
// This ensures type consistency with the Zod schema validation
export type { MarketContext };

export interface SavedScenario {
    id: string;
    name: string;
    context: MarketContext;
    createdAt: string;
}

interface ContextState {
    context: MarketContext;
    savedScenarios: SavedScenario[];
    isLoading: boolean;
    updateContext: (updates: Partial<MarketContext>) => void;
    resetContext: () => void;
    saveScenario: (name: string) => void;
    loadScenario: (id: string) => void;
    deleteScenario: (id: string) => void;
    setLoading: (loading: boolean) => void;
}

export const defaultContext: MarketContext = {
    number_of_riders: 50,
    number_of_drivers: 25,
    location_category: 'Urban',
    customer_loyalty_status: 'Silver',
    number_of_past_rides: 10,
    average_ratings: 4.5,
    time_of_booking: 'Evening',
    vehicle_type: 'Premium',
    expected_ride_duration: 30,
    historical_cost_of_ride: 35.0,
};

export const useContextStore = create<ContextState>()(
    persist(
        (set, get) => ({
            context: defaultContext,
            savedScenarios: [],
            isLoading: false,
            updateContext: (updates) => set((s) => ({ context: { ...s.context, ...updates } })),
            resetContext: () => set({ context: defaultContext }),
            saveScenario: (name) => {
                const newScenario: SavedScenario = {
                    id: crypto.randomUUID(),
                    name,
                    context: get().context,
                    createdAt: new Date().toISOString(),
                };
                set((s) => ({ savedScenarios: [...s.savedScenarios, newScenario] }));
            },
            loadScenario: (id) => {
                const scenario = get().savedScenarios.find((s) => s.id === id);
                if (scenario) set({ context: scenario.context });
            },
            deleteScenario: (id) =>
                set((s) => ({
                    savedScenarios: s.savedScenarios.filter((sc) => sc.id !== id),
                })),
            setLoading: (loading) => set({ isLoading: loading }),
        }),
        { name: 'prismiq-context' }
    )
);
