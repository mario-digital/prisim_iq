'use client';

import type { FC } from 'react';
import ReactMarkdown from 'react-markdown';
import type { Message } from '@/stores/chatStore';
import { ConfidenceBadge } from './ConfidenceBadge';
import { formatMessageTime } from './utils';

/** Message type restricted to assistant role only */
type AssistantMessage = Message & { role: 'assistant' };

/**
 * Props for AIMessage component.
 * 
 * @property message - The assistant message to render (must have role='assistant')
 * @property isStreaming - Controls streaming-phase UI behavior:
 *   - When true: Shows blinking cursor, hides footer (confidence, tools, timestamp)
 *   - When false: Shows complete message with footer metadata
 * 
 * @note If adding more streaming-phase-only UI in the future, ensure the
 * interface between chatStore streaming state and this component is validated
 * with types and tests. See MessageList.tsx for streaming state management.
 */
interface AIMessageProps {
  message: AssistantMessage;
  isStreaming?: boolean;
}

/**
 * AI message bubble - left-aligned with markdown support.
 * Supports streaming mode with blinking cursor indicator.
 * 
 * @note Only renders messages with role='assistant'. Returns null for other roles.
 */
export const AIMessage: FC<AIMessageProps> = ({ message, isStreaming = false }) => {
  // Runtime guard: only render assistant messages
  // This should never happen if types are used correctly - the AssistantMessage type
  // ensures only assistant messages are passed. This guard catches runtime misuse.
  if (message.role !== 'assistant') {
    if (process.env.NODE_ENV === 'development') {
      // Throw in development to catch misuse early - silent failures hide bugs
      throw new Error(
        `[AIMessage] Component received non-assistant message with role="${message.role}". ` +
        `This component only renders assistant messages. Check your message filtering logic.`
      );
    }
    // In production, fail gracefully to avoid crashing the UI
    return null;
  }

  return (
    <div className="flex justify-start message-enter">
      <div className="max-w-[80%] bg-card border border-border/30 rounded-2xl rounded-tl-sm px-4 py-2 shadow-lg shadow-black/10">
        <div className="prose prose-sm dark:prose-invert max-w-none">
          <ReactMarkdown
            components={{
              // Style code blocks
              code: ({ className, children, ...props }) => {
                const isInline = !className;
                return isInline ? (
                  <code
                    className="bg-background/50 px-1 py-0.5 rounded text-sm font-mono"
                    {...props}
                  >
                    {children}
                  </code>
                ) : (
                  <code
                    className={`${className} block bg-background/50 p-2 rounded-md text-sm font-mono overflow-x-auto`}
                    {...props}
                  >
                    {children}
                  </code>
                );
              },
              // Style links
              a: ({ children, ...props }) => (
                <a
                  className="text-primary hover:underline"
                  target="_blank"
                  rel="noopener noreferrer"
                  {...props}
                >
                  {children}
                </a>
              ),
              // Style lists
              ul: ({ children }) => (
                <ul className="list-disc list-inside my-2">{children}</ul>
              ),
              ol: ({ children }) => (
                <ol className="list-decimal list-inside my-2">{children}</ol>
              ),
            }}
          >
            {message.content}
          </ReactMarkdown>
          {/* Blinking cursor during streaming */}
          {isStreaming && (
            <span
              className="inline-block w-2 h-4 bg-cyan-400 ml-0.5 rounded-sm streaming-cursor"
              aria-label="Streaming in progress"
            />
          )}
        </div>
        {/* Footer: only show when not streaming */}
        {!isStreaming && (
          <div className="flex items-center gap-2 mt-2 flex-wrap">
            {message.confidence !== undefined && (
              <ConfidenceBadge value={message.confidence} />
            )}
            {message.toolsUsed && message.toolsUsed.length > 0 && (
              <span className="text-xs text-muted-foreground">
                Used: {message.toolsUsed.join(', ')}
              </span>
            )}
            <span className="text-xs text-muted-foreground">
              {formatMessageTime(message.timestamp)}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

