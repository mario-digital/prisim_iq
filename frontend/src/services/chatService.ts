/**
 * Chat service for communicating with the AI backend.
 * Uses validated API client with Zod schema validation.
 */
import type { MarketContext } from '@/stores/contextStore';
import { ChatResponseSchema } from '@prismiq/shared/schemas';
import { postValidated, api } from '@/lib/api-client';

/**
 * Chat request matching backend ChatRequest schema.
 */
export interface ChatRequest {
  message: string;
  context: MarketContext;
  session_id?: string | null;
}

/**
 * Chat response from the API.
 */
export interface ChatResponse {
  message: string;
  tools_used: string[];
  context: Record<string, unknown>;
  timestamp: string;
  processing_time_ms?: number | null;
  error?: string | null;
}

/**
 * Send a message to the AI chat endpoint.
 *
 * @param message - User's message
 * @param context - Current market context
 * @param sessionId - Optional session ID for conversation continuity
 * @returns Validated chat response
 */
export async function sendMessage(
  message: string,
  context: MarketContext,
  sessionId?: string | null
): Promise<ChatResponse> {
  const request: ChatRequest = {
    message,
    context,
    session_id: sessionId,
  };

  return postValidated('api/v1/chat', ChatResponseSchema, request);
}

/**
 * Send a message and receive streaming response.
 * Returns an AsyncGenerator that yields ChatStreamEvent objects.
 *
 * @param message - User's message
 * @param context - Current market context
 * @param sessionId - Optional session ID for conversation continuity
 * @yields Parsed SSE events from the stream
 */
export async function* sendMessageStream(
  message: string,
  context: MarketContext,
  sessionId?: string | null
): AsyncGenerator<{ token?: string; tool_call?: string; message?: string; done: boolean }> {
  const request: ChatRequest = {
    message,
    context,
    session_id: sessionId,
  };

  const response = await api.post('api/v1/chat/stream', {
    json: request,
  });

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('No response body');
  }

  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6).trim();
          if (data === '[DONE]') {
            return;
          }
          try {
            const event = JSON.parse(data);
            yield event;
          } catch {
            // Skip malformed JSON
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}
