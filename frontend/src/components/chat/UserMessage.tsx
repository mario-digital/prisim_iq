'use client';

import type { FC } from 'react';
import type { Message } from '@/stores/chatStore';
import { formatMessageTime } from './utils';

interface UserMessageProps {
  message: Message;
}

/**
 * User message bubble - right-aligned with primary color.
 */
export const UserMessage: FC<UserMessageProps> = ({ message }) => {
  return (
    <div className="flex justify-end">
      <div className="max-w-[80%] bg-primary text-primary-foreground rounded-2xl rounded-tr-sm px-4 py-2 shadow-sm">
        <p className="whitespace-pre-wrap">{message.content}</p>
        <span className="block text-xs opacity-70 mt-1 text-right">
          {formatMessageTime(message.timestamp)}
        </span>
      </div>
    </div>
  );
};

