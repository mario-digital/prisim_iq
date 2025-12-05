'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type ActiveTab = 'workspace' | 'executive' | 'evidence';

interface LayoutState {
  leftPanelCollapsed: boolean;
  rightPanelCollapsed: boolean;
  activeTab: ActiveTab;
  isHoneywellOpen: boolean;
  toggleLeftPanel: () => void;
  toggleRightPanel: () => void;
  setLeftCollapsed: (collapsed: boolean) => void;
  setRightCollapsed: (collapsed: boolean) => void;
  setActiveTab: (tab: ActiveTab) => void;
  setHoneywellOpen: (open: boolean) => void;
  toggleHoneywell: () => void;
}

export const useLayoutStore = create<LayoutState>()(
  persist(
    (set) => ({
      leftPanelCollapsed: false,
      rightPanelCollapsed: false,
      activeTab: 'workspace',
      isHoneywellOpen: false,
      toggleLeftPanel: () =>
        set((state) => ({ leftPanelCollapsed: !state.leftPanelCollapsed })),
      toggleRightPanel: () =>
        set((state) => ({ rightPanelCollapsed: !state.rightPanelCollapsed })),
      setLeftCollapsed: (collapsed) => set({ leftPanelCollapsed: collapsed }),
      setRightCollapsed: (collapsed) => set({ rightPanelCollapsed: collapsed }),
      setActiveTab: (tab) => set({ activeTab: tab }),
      setHoneywellOpen: (open) => set({ isHoneywellOpen: open }),
      toggleHoneywell: () =>
        set((state) => ({ isHoneywellOpen: !state.isHoneywellOpen })),
    }),
    { name: 'prismiq-layout' }
  )
);
