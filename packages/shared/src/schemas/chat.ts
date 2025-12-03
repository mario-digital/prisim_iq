/**
 * Chat schemas for chat endpoint.
 * Source: backend/src/schemas/chat.py
 */
import { z } from 'zod';
import { MarketContextSchema } from './market';

/**
 * Request schema for chat endpoint.
 * Source: backend/src/schemas/chat.py::ChatRequest
 */
export const ChatRequestSchema = z.object({
  message: z
    .string()
    .min(1)
    .max(4000)
    .describe("User's natural language query"),
  context: MarketContextSchema.describe('Current market context for tool execution'),
  session_id: z
    .string()
    .nullable()
    .optional()
    .describe('Session ID for conversation continuity across requests'),
});

export type ChatRequest = z.infer<typeof ChatRequestSchema>;

/**
 * Response schema for chat endpoint (non-streaming).
 * Source: backend/src/schemas/chat.py::ChatResponse
 */
export const ChatResponseSchema = z.object({
  message: z.string().describe("Agent's natural language response"),
  tools_used: z
    .array(z.string())
    .default([])
    .describe('List of tools invoked to answer the query'),
  context: z.record(z.string(), z.unknown()).describe('Market context used for the response'),
  timestamp: z.string().datetime().describe('Response timestamp (UTC)'),
  processing_time_ms: z
    .number()
    .nullable()
    .optional()
    .describe('Time taken to process the request in milliseconds'),
  error: z.string().nullable().optional().describe('Error message if request failed'),
});

export type ChatResponse = z.infer<typeof ChatResponseSchema>;

/**
 * Schema for SSE stream events.
 * Source: backend/src/schemas/chat.py::ChatStreamEvent
 */
export const ChatStreamEventSchema = z.object({
  token: z.string().nullable().optional().describe('Incremental token from LLM output'),
  tool_call: z.string().nullable().optional().describe('Name of tool being invoked'),
  message: z
    .string()
    .nullable()
    .optional()
    .describe('Complete response message (on completion)'),
  tools_used: z
    .array(z.string())
    .nullable()
    .optional()
    .describe('List of all tools used (on completion)'),
  error: z.string().nullable().optional().describe('Error message if stream failed'),
  done: z.boolean().default(false).describe('True when stream is complete (success or error)'),
});

export type ChatStreamEvent = z.infer<typeof ChatStreamEventSchema>;

