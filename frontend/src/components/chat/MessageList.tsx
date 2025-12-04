'use client';

import { useEffect, useRef, type FC } from 'react';
import type { Message as MessageType } from '@/stores/chatStore';
import { Message } from './Message';
import { AIMessage } from './AIMessage';
import { TypingIndicator } from './TypingIndicator';
import { ToolCallIndicator } from './ToolCallIndicator';
import { StreamError } from './StreamError';

/** Debug logging flag - only enabled in development */
const DEBUG = process.env.NODE_ENV === 'development';

interface MessageListProps {
  messages: MessageType[];
  isLoading: boolean;
  streamingContent?: string | null;
  currentToolCall?: string | null;
  streamError?: string | null;
  onRetry?: () => void;
}

/**
 * Scrollable message list with auto-scroll on new messages.
 * Supports streaming mode with partial content, tool call indicators, and error handling.
 */
export const MessageList: FC<MessageListProps> = ({
  messages,
  isLoading,
  streamingContent,
  currentToolCall,
  streamError,
  onRetry,
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Track if we're actively streaming (have content OR tool call)
  const isStreaming = streamingContent !== null && streamingContent !== undefined;
  
  // Debug logging - only in development
  if (DEBUG) {
    console.log('[MessageList] Render:', { 
      messagesCount: messages.length, 
      isLoading, 
      streamingContent: streamingContent?.slice(0, 50), 
      currentToolCall, 
      isStreaming 
    });
  }

  // Auto-scroll to bottom when messages change, loading, or streaming content changes
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading, streamingContent, currentToolCall, streamError]);

  return (
    <div ref={containerRef} className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((message) => (
        <Message key={message.id} message={message} />
      ))}

      {/* Stream error with retry option */}
      {streamError && !isLoading && (
        <StreamError error={streamError} onRetry={onRetry} showRetry={!!onRetry} />
      )}

      {/* Tool call indicator - shown during tool execution */}
      {currentToolCall && <ToolCallIndicator toolName={currentToolCall} />}

      {/* Streaming message - shown while receiving tokens */}
      {isStreaming && streamingContent && (
        <AIMessage
          message={{
            id: 'streaming',
            role: 'assistant',
            content: streamingContent,
            timestamp: new Date().toISOString(),
          }}
          isStreaming
        />
      )}

      {/* Typing indicator - only shown when loading but no streaming content yet */}
      {isLoading && !isStreaming && !currentToolCall && <TypingIndicator />}

      <div ref={bottomRef} />
    </div>
  );
};

