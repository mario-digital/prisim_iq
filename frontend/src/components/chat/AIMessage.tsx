'use client';

import type { FC } from 'react';
import ReactMarkdown from 'react-markdown';
import type { Message } from '@/stores/chatStore';
import { ConfidenceBadge } from './ConfidenceBadge';
import { formatMessageTime } from './utils';

interface AIMessageProps {
  message: Message;
  isStreaming?: boolean;
}

/**
 * AI message bubble - left-aligned with markdown support.
 * Supports streaming mode with blinking cursor indicator.
 */
export const AIMessage: FC<AIMessageProps> = ({ message, isStreaming = false }) => {
  return (
    <div className="flex justify-start">
      <div className="max-w-[80%] bg-muted rounded-2xl rounded-tl-sm px-4 py-2 shadow-sm">
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
              className="inline-block w-2 h-4 bg-primary/80 ml-0.5 rounded-sm streaming-cursor"
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

