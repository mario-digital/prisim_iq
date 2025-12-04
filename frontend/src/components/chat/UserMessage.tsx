'use client';

import type { FC } from 'react';
import type { Message } from '@/stores/chatStore';
import { formatMessageTime } from './utils';

interface UserMessageProps {
  message: Message;
}

/**
 * User message bubble - right-aligned with gradient styling.
 */
export const UserMessage: FC<UserMessageProps> = ({ message }) => {
  return (
    <div className="flex justify-end message-enter">
      <div className="max-w-[80%] bg-gradient-to-br from-cyan-500 to-blue-600 text-white rounded-2xl rounded-tr-sm px-4 py-2 shadow-lg shadow-cyan-500/20">
        <p className="whitespace-pre-wrap">{message.content}</p>
        <span className="block text-xs opacity-70 mt-1 text-right">
          {formatMessageTime(message.timestamp)}
        </span>
      </div>
    </div>
  );
};
