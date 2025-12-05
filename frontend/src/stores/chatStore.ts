'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  confidence?: number;
  pricingResult?: unknown;
}

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  setLoading: (loading: boolean) => void;
  clearChat: () => void;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      messages: [],
      isLoading: false,
      addMessage: (msg) =>
        set((s) => ({
          messages: [
            ...s.messages,
            {
              ...msg,
              id: crypto.randomUUID(),
              timestamp: new Date().toISOString(),
            },
          ],
        })),
      setLoading: (isLoading) => set({ isLoading }),
      clearChat: () => set({ messages: [] }),
    }),
    { name: 'prismiq-chat' }
  )
);

