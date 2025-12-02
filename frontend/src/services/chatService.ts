/**
 * Chat service for communicating with the AI backend.
 */
import ky from 'ky';
import type { MarketContext } from '@prismiq/shared';
import { API_BASE_URL } from '@/lib/api';

export interface ChatRequest {
  message: string;
  context?: MarketContext;
}

export interface ChatResponse {
  message: string;
  confidence?: number;
  pricingResult?: unknown;
}

const api = ky.create({
  prefixUrl: API_BASE_URL,
  timeout: 30000,
});

/**
 * Send a message to the AI chat endpoint.
 */
export async function sendMessage(
  message: string,
  context?: MarketContext
): Promise<ChatResponse> {
  return api
    .post('api/v1/chat', {
      json: { message, context } satisfies ChatRequest,
    })
    .json<ChatResponse>();
}

