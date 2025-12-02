# 10. Frontend Architecture

## 10.1 Component Organization

```
frontend/src/
├── app/                          # Next.js App Router
│   ├── layout.tsx                # Root layout with providers
│   ├── page.tsx                  # Home → redirect to /workspace
│   ├── workspace/
│   │   └── page.tsx              # Analyst Workspace
│   ├── executive/
│   │   └── page.tsx              # Executive Summary
│   └── evidence/
│       └── page.tsx              # Evidence & Methods
│
├── components/
│   ├── ui/                       # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   └── ...
│   ├── chat/                     # Chat interface
│   │   ├── ChatPanel.tsx
│   │   ├── MessageList.tsx
│   │   ├── Message.tsx
│   │   └── ChatInput.tsx
│   ├── context/                  # Market context inputs
│   │   ├── ContextPanel.tsx
│   │   ├── LocationSelector.tsx
│   │   └── DemandSliders.tsx
│   ├── visualizations/           # Charts and data viz
│   │   ├── DemandCurve.tsx
│   │   ├── FeatureImportance.tsx
│   │   └── PriceGauge.tsx
│   └── layout/                   # Layout components
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── ThreePanel.tsx
│
├── hooks/                        # Custom React hooks
│   ├── useChat.ts
│   ├── useOptimizePrice.ts
│   └── useScenarios.ts
│
├── services/                     # API client layer
│   ├── api.ts                    # Base API configuration
│   ├── chat.service.ts
│   ├── pricing.service.ts
│   └── scenarios.service.ts
│
├── stores/                       # Zustand state stores
│   ├── chatStore.ts
│   ├── contextStore.ts
│   └── scenarioStore.ts
│
├── lib/                          # Utilities
│   ├── utils.ts                  # General utilities
│   └── cn.ts                     # Class name helper
│
└── types/                        # Local type extensions
    └── index.ts
```

## 10.2 State Management (Zustand)

```typescript
// stores/chatStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { ChatMessage } from '@prismiq/shared';

interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  conversationId: string | null;
  
  // Actions
  addMessage: (message: ChatMessage) => void;
  clearMessages: () => void;
  setLoading: (loading: boolean) => void;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      messages: [],
      isLoading: false,
      conversationId: null,
      
      addMessage: (message) =>
        set((state) => ({
          messages: [...state.messages, message],
        })),
      
      clearMessages: () =>
        set({ messages: [], conversationId: null }),
      
      setLoading: (loading) =>
        set({ isLoading: loading }),
    }),
    {
      name: 'prismiq-chat',
    }
  )
);
```

## 10.3 Routing Strategy

```typescript
// App Router structure
// All routes use server components by default
// Client components marked with 'use client'

const routes = {
  '/': {
    redirect: '/workspace',
  },
  '/workspace': {
    component: 'WorkspacePage',
    layout: 'ThreePanelLayout',
    description: 'Main analyst interface with chat + context + viz',
  },
  '/executive': {
    component: 'ExecutivePage',
    layout: 'SinglePanelLayout',
    description: 'Executive summary dashboard',
  },
  '/evidence': {
    component: 'EvidencePage',
    layout: 'SinglePanelLayout',
    description: 'Methodology and technical details',
  },
};
```

## 10.4 API Integration Pattern

```typescript
// services/api.ts
import ky from 'ky';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = ky.create({
  prefixUrl: API_BASE,
  timeout: 30000,
  hooks: {
    beforeRequest: [
      (request) => {
        request.headers.set('Content-Type', 'application/json');
      },
    ],
    afterResponse: [
      async (request, options, response) => {
        if (!response.ok) {
          const error = await response.json();
          throw new APIError(error.detail, response.status);
        }
      },
    ],
  },
});

// services/pricing.service.ts
import { api } from './api';
import type { MarketContext, PricingResult } from '@prismiq/shared';

export const pricingService = {
  async optimizePrice(context: MarketContext): Promise<PricingResult> {
    return api.post('api/v1/optimize_price', {
      json: { context },
    }).json();
  },
};
```

---
