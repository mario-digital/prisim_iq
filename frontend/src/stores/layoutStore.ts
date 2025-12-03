'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type ActiveTab = 'workspace' | 'executive' | 'evidence';

interface LayoutState {
  leftPanelCollapsed: boolean;
  rightPanelCollapsed: boolean;
  activeTab: ActiveTab;
  toggleLeftPanel: () => void;
  toggleRightPanel: () => void;
  setLeftCollapsed: (collapsed: boolean) => void;
  setRightCollapsed: (collapsed: boolean) => void;
  setActiveTab: (tab: ActiveTab) => void;
}

export const useLayoutStore = create<LayoutState>()(
  persist(
    (set) => ({
      leftPanelCollapsed: false,
      rightPanelCollapsed: false,
      activeTab: 'workspace',
      toggleLeftPanel: () =>
        set((state) => ({ leftPanelCollapsed: !state.leftPanelCollapsed })),
      toggleRightPanel: () =>
        set((state) => ({ rightPanelCollapsed: !state.rightPanelCollapsed })),
      setLeftCollapsed: (collapsed) => set({ leftPanelCollapsed: collapsed }),
      setRightCollapsed: (collapsed) => set({ rightPanelCollapsed: collapsed }),
      setActiveTab: (tab) => set({ activeTab: tab }),
    }),
    { name: 'prismiq-layout' }
  )
);

