'use client';

import { useCallback, useRef, useState, type FC } from 'react';
import { useChatStore } from '@/stores/chatStore';
import { useContextStore } from '@/stores/contextStore';
import { streamMessage, sendMessage } from '@/services/chatService';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { WelcomeMessage } from './WelcomeMessage';

/** Max consecutive SSE failures before falling back to non-streaming */
const MAX_STREAM_FAILURES = 3;

/**
 * Main chat panel component with SSE streaming support.
 */
export const ChatPanel: FC = () => {
  const {
    messages,
    isLoading,
    streamingContent,
    currentToolCall,
    streamError,
    addMessage,
    startStreaming,
    appendToken,
    setToolCall,
    finalizeStream,
    setStreamError,
    cancelStream,
  } = useChatStore();
  const context = useContextStore((state) => state.context);

  // Track streaming failures for fallback logic
  const streamFailures = useRef(0);
  const [useStreaming, setUseStreaming] = useState(true);

  // Abort controller for cancellation
  const abortControllerRef = useRef<AbortController | null>(null);

  /**
   * Handle sending message with streaming.
   */
  const handleStreamingMessage = useCallback(
    async (content: string) => {
      addMessage({ role: 'user', content });
      startStreaming();
      setToolCall(null);

      const controller = new AbortController();
      abortControllerRef.current = controller;

      try {
        console.log('[ChatPanel] Starting stream for:', content);
        for await (const event of streamMessage(content, context, {
          keepalive: true,
          interval: 15,
          signal: controller.signal,
        })) {
          console.log('[ChatPanel] Received event:', event);
          
          // Handle token events
          if ('token' in event && event.token) {
            console.log('[ChatPanel] Appending token:', event.token);
            appendToken(event.token);
          }

          // Handle tool call events
          if ('tool_call' in event && event.tool_call) {
            console.log('[ChatPanel] Tool call:', event.tool_call);
            setToolCall(event.tool_call);
          }

          // Handle completion
          if ('done' in event && event.done === true) {
            console.log('[ChatPanel] Stream complete, done event:', event);
            if ('error' in event) {
              // Error event
              setStreamError(event.error);
              addMessage({
                role: 'assistant',
                content: `Sorry, I encountered an error: ${event.error}. Please try again.`,
              });
              cancelStream();
            } else if ('message' in event) {
              // Success event
              console.log('[ChatPanel] Finalizing stream with message');
              finalizeStream({
                role: 'assistant',
                content: event.message,
                confidence: event.confidence,
                toolsUsed: event.tools_used,
              });
              // Reset failure counter on success
              streamFailures.current = 0;
            }
            break;
          }
        }
        console.log('[ChatPanel] Stream loop ended');
      } catch (error) {
        // Don't report abort errors
        if (error instanceof Error && error.name === 'AbortError') {
          cancelStream();
          return;
        }

        // Increment failure counter
        streamFailures.current += 1;

        const errorMessage =
          error instanceof Error ? error.message : 'Connection lost';

        // If we've failed too many times, disable streaming
        if (streamFailures.current >= MAX_STREAM_FAILURES) {
          setUseStreaming(false);
          console.warn(
            `Streaming failed ${MAX_STREAM_FAILURES} times, falling back to non-streaming`
          );
        }

        setStreamError(errorMessage);
        addMessage({
          role: 'assistant',
          content: `Sorry, I encountered an error: ${errorMessage}. ${
            streamFailures.current >= MAX_STREAM_FAILURES
              ? 'Switching to non-streaming mode.'
              : 'Please try again.'
          }`,
        });
        cancelStream();
      } finally {
        abortControllerRef.current = null;
      }
    },
    [
      addMessage,
      startStreaming,
      appendToken,
      setToolCall,
      finalizeStream,
      setStreamError,
      cancelStream,
      context,
    ]
  );

  /**
   * Handle sending message without streaming (fallback).
   */
  const handleNonStreamingMessage = useCallback(
    async (content: string) => {
      addMessage({ role: 'user', content });
      startStreaming(); // Use loading state

      try {
        const response = await sendMessage(content, context);
        finalizeStream({
          role: 'assistant',
          content: response.message,
          toolsUsed: response.tools_used,
        });
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : 'An unexpected error occurred';
        setStreamError(errorMessage);
        addMessage({
          role: 'assistant',
          content: `Sorry, I encountered an error: ${errorMessage}. Please try again.`,
        });
        cancelStream();
      }
    },
    [addMessage, startStreaming, finalizeStream, setStreamError, cancelStream, context]
  );

  /**
   * Main send handler - uses streaming or fallback based on state.
   */
  const handleSendMessage = useCallback(
    async (content: string) => {
      if (useStreaming) {
        await handleStreamingMessage(content);
      } else {
        await handleNonStreamingMessage(content);
      }
    },
    [useStreaming, handleStreamingMessage, handleNonStreamingMessage]
  );

  const handleExampleClick = useCallback(
    (question: string) => {
      handleSendMessage(question);
    },
    [handleSendMessage]
  );

  /**
   * Retry the last failed message.
   */
  const handleRetry = useCallback(() => {
    // Find the last user message
    const lastUserMsg = messages
      .slice()
      .reverse()
      .find((m) => m.role === 'user');
    
    if (lastUserMsg) {
      // Clear the error and re-send
      setStreamError(null);
      handleSendMessage(lastUserMsg.content);
    }
  }, [messages, setStreamError, handleSendMessage]);

  const showWelcome = messages.length === 0 && !isLoading;

  return (
    <div className="flex flex-col h-full">
      {showWelcome ? (
        <WelcomeMessage onExampleClick={handleExampleClick} />
      ) : (
        <MessageList
          messages={messages}
          isLoading={isLoading}
          streamingContent={streamingContent}
          currentToolCall={currentToolCall}
          streamError={streamError}
          onRetry={handleRetry}
        />
      )}
      <ChatInput onSend={handleSendMessage} disabled={isLoading} />
    </div>
  );
};

