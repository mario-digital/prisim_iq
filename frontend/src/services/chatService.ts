/**
 * Chat service for communicating with the AI backend.
 * Supports both request/response and SSE streaming modes.
 */
import type { MarketContext } from '@/stores/contextStore';
import { ChatResponseSchema } from '@prismiq/shared/schemas';
import { postValidated } from '@/lib/api-client';
import { API_BASE_URL } from '@/lib/api';

/**
 * Chat request matching backend ChatRequest schema.
 */
export interface ChatRequest {
  message: string;
  context: MarketContext;
  session_id?: string | null;
}

/**
 * Chat response from the API (non-streaming).
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
 * SSE stream event types from the backend.
 */
export type ChatStreamEvent =
  | { token: string; done: false }
  | { tool_call: string; done: false }
  | { message: string; tools_used?: string[]; confidence?: number; done: true }
  | { error: string; done: true }
  | Record<string, never>; // keepalive `{}` (ignored)

/**
 * Options for streaming requests.
 */
export interface StreamOptions {
  plan?: boolean; // orchestrator path (multi-agent)
  keepalive?: boolean; // enable backend heartbeats
  interval?: number; // keepalive interval in seconds
  model?: string; // optional reporter model hint
  signal?: AbortSignal; // for cancellation
  sessionId?: string | null; // conversation continuity
}

/**
 * Send a message to the AI chat endpoint (non-streaming).
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
 * Stream a message and receive SSE response.
 * Returns an AsyncGenerator that yields ChatStreamEvent objects.
 * Handles keepalive comment lines and empty `{}` payloads.
 *
 * @param message - User's message
 * @param context - Current market context
 * @param opts - Stream options (plan, keepalive, model, signal)
 * @yields Parsed SSE events from the stream
 */
export async function* streamMessage(
  message: string,
  context: MarketContext,
  opts: StreamOptions = {}
): AsyncGenerator<ChatStreamEvent> {
  // Build query parameters
  const params = new URLSearchParams({ stream: 'true' });
  if (opts.plan) params.set('plan', 'true');
  if (opts.keepalive) params.set('keepalive', 'true');
  if (opts.interval) params.set('interval', String(opts.interval));
  if (opts.model) params.set('model', opts.model);

  const request: ChatRequest = {
    message,
    context,
    session_id: opts.sessionId,
  };

  const response = await fetch(`${API_BASE_URL}/api/v1/chat?${params.toString()}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
    },
    body: JSON.stringify(request),
    signal: opts.signal,
  });

  if (!response.ok) {
    throw new Error(`SSE response error: ${response.status} ${response.statusText}`);
  }

  if (!response.body) {
    throw new Error('No response body for SSE stream');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  console.log('[chatService] Starting to read stream...');

  try {
    while (true) {
      const { done, value } = await reader.read();
      console.log('[chatService] Read chunk:', { done, bytesReceived: value?.length });
      
      if (done) {
        console.log('[chatService] Reader done, remaining buffer:', buffer);
        break;
      }

      const chunk = decoder.decode(value, { stream: true });
      console.log('[chatService] Decoded chunk:', chunk.slice(0, 200));
      buffer += chunk;

      // Normalize line endings (CRLF → LF) before splitting
      // SSE spec uses \n\n but some servers send \r\n\r\n
      const normalizedBuffer = buffer.replace(/\r\n/g, '\n');
      
      // Split by double newline between SSE events; keep last partial in buffer
      const events = normalizedBuffer.split('\n\n');
      buffer = events.pop() ?? '';
      
      console.log('[chatService] Split into events:', events.length, 'remaining buffer length:', buffer.length);

      for (const raw of events) {
        console.log('[chatService] Processing raw event:', raw.slice(0, 100));
        
        // Ignore SSE comment lines (e.g., ": keepalive")
        if (raw.startsWith(':')) {
          console.log('[chatService] Skipping comment line');
          continue;
        }

        // Find the data: line in this event
        const dataLine = raw.split('\n').find((l) => l.startsWith('data: '));
        if (!dataLine) {
          console.log('[chatService] No data: line found in event');
          continue;
        }

        const jsonText = dataLine.slice(6).trim();
        if (!jsonText) {
          console.log('[chatService] Empty JSON text');
          continue;
        }

        // Handle [DONE] marker (some backends use this)
        if (jsonText === '[DONE]') {
          console.log('[chatService] Received [DONE] marker');
          return;
        }

        try {
          const evt = JSON.parse(jsonText) as ChatStreamEvent;

          // Ignore empty keepalive payloads `{}`
          if (Object.keys(evt).length === 0) {
            console.log('[chatService] Skipping empty keepalive');
            continue;
          }

          console.log('[chatService] Yielding event:', evt);
          yield evt;

          // If done flag is true, we're finished
          if ('done' in evt && evt.done === true) {
            console.log('[chatService] Stream complete (done=true)');
            return;
          }
        } catch (e) {
          // Skip malformed JSON
          console.warn('[chatService] Failed to parse SSE event:', jsonText, e);
        }
      }
    }
  } finally {
    console.log('[chatService] Releasing reader lock');
    reader.releaseLock();
  }
}
