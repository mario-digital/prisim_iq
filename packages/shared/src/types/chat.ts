/**
 * Chat and conversation types for the agent interface.
 */

/**
 * Role of a message sender.
 */
export type MessageRole = 'user' | 'assistant' | 'system';

/**
 * Type of message content.
 */
export type MessageType = 
  | 'text'
  | 'pricing_result'
  | 'chart'
  | 'error'
  | 'loading';

/**
 * Single chat message.
 */
export interface ChatMessage {
  /** Unique message ID */
  id: string;
  
  /** Message sender role */
  role: MessageRole;
  
  /** Type of content */
  type: MessageType;
  
  /** Text content */
  content: string;
  
  /** Structured data (pricing result, chart data, etc.) */
  data?: unknown;
  
  /** Timestamp */
  timestamp: string;
  
  /** Whether message is still being generated */
  isStreaming?: boolean;
}

/**
 * Chat session state.
 */
export interface ChatSession {
  /** Session ID */
  id: string;
  
  /** All messages in the session */
  messages: ChatMessage[];
  
  /** Session creation time */
  createdAt: string;
  
  /** Last activity time */
  updatedAt: string;
  
  /** Session title (generated from first message) */
  title?: string;
}

/**
 * Request to send a chat message.
 */
export interface ChatRequest {
  /** User's message */
  message: string;
  
  /** Session ID for context */
  sessionId?: string;
  
  /** Current market context */
  context?: unknown;
}

/**
 * Response from chat endpoint.
 */
export interface ChatResponse {
  /** Assistant's response */
  message: ChatMessage;
  
  /** Session ID */
  sessionId: string;
  
  /** Any actions to take (e.g., update context) */
  actions?: ChatAction[];
}

/**
 * Action for the frontend to execute.
 */
export interface ChatAction {
  /** Action type */
  type: 'update_context' | 'show_chart' | 'navigate';
  
  /** Action payload */
  payload: unknown;
}

