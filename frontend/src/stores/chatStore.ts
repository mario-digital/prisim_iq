'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * Chat message structure.
 * 
 * @note Field naming convention: Frontend uses camelCase (`toolsUsed`),
 * backend API uses snake_case (`tools_used`). Conversion happens in
 * ChatPanel.tsx when processing API responses.
 */
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  confidence?: number;
  /** Tools used by the AI (converted from backend's `tools_used`) */
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
              // NOTE: crypto.randomUUID() is browser-only (Web Crypto API).
              // Safe here because: 1) Store is 'use client', 2) Zustand persist hydrates client-side.
              // TODO(SSR): If future hydration mismatches occur, replace with `uuid` package.
              id: crypto.randomUUID(),
              timestamp: new Date().toISOString(),
            },
          ],
        })),

      /**
       * Set loading state.
       * @note Only sets isLoading flag. Does NOT clear streamError.
       * Use startStreaming() to reset all streaming state, or setStreamError(null) explicitly.
       */
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

