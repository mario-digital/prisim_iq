'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  confidence?: number;
  toolsUsed?: string[];
  pricingResult?: unknown;
}

interface ChatState {
  messages: Message[];
  isLoading: boolean;

  // Streaming state
  streamingContent: string | null;
  currentToolCall: string | null;
  streamError: string | null;

  // Actions
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  setLoading: (loading: boolean) => void;
  clearChat: () => void;

  // Streaming actions
  startStreaming: () => void;
  appendToken: (token: string) => void;
  setToolCall: (toolName: string | null) => void;
  setStreamError: (error: string | null) => void;
  finalizeStream: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  cancelStream: () => void;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      messages: [],
      isLoading: false,
      streamingContent: null,
      currentToolCall: null,
      streamError: null,

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

      clearChat: () =>
        set({
          messages: [],
          streamingContent: null,
          currentToolCall: null,
          streamError: null,
        }),

      // Start streaming mode - reset streaming state
      startStreaming: () =>
        set({
          isLoading: true,
          streamingContent: '',
          currentToolCall: null,
          streamError: null,
        }),

      // Append token to streaming content
      appendToken: (token) =>
        set((s) => ({
          streamingContent: (s.streamingContent ?? '') + token,
        })),

      // Set current tool being called
      setToolCall: (toolName) => set({ currentToolCall: toolName }),

      // Set stream error
      setStreamError: (error) =>
        set({
          streamError: error,
          isLoading: false,
        }),

      // Finalize stream: convert streaming content to a complete message
      finalizeStream: (msg) =>
        set((s) => ({
          messages: [
            ...s.messages,
            {
              ...msg,
              id: crypto.randomUUID(),
              timestamp: new Date().toISOString(),
            },
          ],
          streamingContent: null,
          currentToolCall: null,
          isLoading: false,
        })),

      // Cancel streaming and clear state
      cancelStream: () =>
        set({
          streamingContent: null,
          currentToolCall: null,
          isLoading: false,
        }),
    }),
    {
      name: 'prismiq-chat',
      // Only persist messages, not streaming state
      partialize: (state) => ({ messages: state.messages }),
    }
  )
);

