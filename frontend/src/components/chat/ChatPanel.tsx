'use client';

import { useCallback, type FC } from 'react';
import { useChatStore } from '@/stores/chatStore';
import { useContextStore } from '@/stores/contextStore';
import { sendMessage } from '@/services/chatService';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { WelcomeMessage } from './WelcomeMessage';

/**
 * Main chat panel component containing the full chat interface.
 */
export const ChatPanel: FC = () => {
  const { messages, isLoading, addMessage, setLoading } = useChatStore();
  const context = useContextStore((state) => state.context);

  const handleSendMessage = useCallback(
    async (content: string) => {
      // Add user message
      addMessage({ role: 'user', content });
      setLoading(true);

      try {
        // Call API with current market context
        const response = await sendMessage(content, context);
        
        // Add AI response
        addMessage({
          role: 'assistant',
          content: response.message,
        });
      } catch (error) {
        // Add error message
        const errorMessage =
          error instanceof Error ? error.message : 'An unexpected error occurred';
        addMessage({
          role: 'assistant',
          content: `Sorry, I encountered an error: ${errorMessage}. Please try again.`,
        });
      } finally {
        setLoading(false);
      }
    },
    [addMessage, setLoading, context]
  );

  const handleExampleClick = useCallback(
    (question: string) => {
      handleSendMessage(question);
    },
    [handleSendMessage]
  );

  const showWelcome = messages.length === 0 && !isLoading;

  return (
    <div className="flex flex-col h-full">
      {showWelcome ? (
        <WelcomeMessage onExampleClick={handleExampleClick} />
      ) : (
        <MessageList messages={messages} isLoading={isLoading} />
      )}
      <ChatInput onSend={handleSendMessage} disabled={isLoading} />
    </div>
  );
};

