'use client';

import type { FC } from 'react';
import type { Message as MessageType } from '@/stores/chatStore';
import { UserMessage } from './UserMessage';
import { AIMessage } from './AIMessage';

interface MessageProps {
  message: MessageType;
}

/**
 * Message component that renders the appropriate bubble based on role.
 */
export const Message: FC<MessageProps> = ({ message }) => {
  if (message.role === 'user') {
    return <UserMessage message={message} />;
  }
  return <AIMessage message={message} />;
};

