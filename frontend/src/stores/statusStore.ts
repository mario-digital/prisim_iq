'use client';

import { create } from 'zustand';

export type HealthStatus = 'healthy' | 'degraded' | 'unhealthy';
export type PipelineStage = -1 | 0 | 1 | 2 | 3; // -1 = idle, 0-3 = Context/ML/Optimize/Price

export const PIPELINE_STAGES = ['Context', 'ML', 'Optimize', 'Price'] as const;

interface StatusState {
  // System health
  health: HealthStatus;
  lastHealthCheck: Date | null;
  
  // Pipeline state
  currentStage: PipelineStage;
  isProcessing: boolean;
  completedStages: number[]; // Array of completed stage indices
  
  // Footer stats
  currentSegment: string | null;
  modelsReady: number;
  totalModels: number;
  lastResponseTime: number | null;
  
  // Honeywell overlay
  honeywellOverlayVisible: boolean;
  
  // Actions
  setHealth: (health: HealthStatus) => void;
  setHealthCheck: (health: HealthStatus) => void;
  startProcessing: () => void;
  advanceStage: () => void;
  completeProcessing: (responseTime: number) => void;
  resetPipeline: () => void;
  setSegment: (segment: string | null) => void;
  setModelsReady: (ready: number, total?: number) => void;
  toggleHoneywellOverlay: () => void;
  setHoneywellOverlay: (visible: boolean) => void;
}

export const useStatusStore = create<StatusState>((set, get) => ({
  // Initial state
  health: 'healthy',
  lastHealthCheck: null,
  currentStage: -1,
  isProcessing: false,
  completedStages: [],
  currentSegment: null,
  modelsReady: 3,
  totalModels: 3,
  lastResponseTime: null,
  honeywellOverlayVisible: false,

  // Actions
  setHealth: (health) => set({ health }),
  
  setHealthCheck: (health) => set({ 
    health, 
    lastHealthCheck: new Date() 
  }),

  startProcessing: () => set({ 
    isProcessing: true, 
    currentStage: 0,
    completedStages: [],
  }),

  advanceStage: () => {
    const { currentStage, completedStages } = get();
    if (currentStage >= 0 && currentStage < 3) {
      set({
        completedStages: [...completedStages, currentStage],
        currentStage: (currentStage + 1) as PipelineStage,
      });
    }
  },

  completeProcessing: (responseTime) => {
    const { completedStages, currentStage } = get();
    set({
      isProcessing: false,
      currentStage: -1,
      completedStages: [...completedStages, currentStage].filter((s) => s >= 0),
      lastResponseTime: responseTime,
    });
    // Reset completed stages after brief display
    setTimeout(() => {
      set({ completedStages: [] });
    }, 2000);
  },

  resetPipeline: () => set({
    isProcessing: false,
    currentStage: -1,
    completedStages: [],
  }),

  setSegment: (currentSegment) => set({ currentSegment }),

  setModelsReady: (ready, total) => set({ 
    modelsReady: ready,
    ...(total !== undefined && { totalModels: total }),
  }),

  toggleHoneywellOverlay: () => set((state) => ({ 
    honeywellOverlayVisible: !state.honeywellOverlayVisible 
  })),

  setHoneywellOverlay: (visible) => set({ honeywellOverlayVisible: visible }),
}));


