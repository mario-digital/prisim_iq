'use client';

import type { FC } from 'react';
import { Sparkles } from 'lucide-react';

const EXAMPLE_QUESTIONS = [
  "What's the optimal price for downtown rush hour?",
  'Why is surge pricing recommended?',
  'How sensitive is this to demand changes?',
  'Compare urban vs suburban pricing',
];

interface WelcomeMessageProps {
  onExampleClick: (question: string) => void;
}

/**
 * Welcome message shown when chat is empty.
 */
export const WelcomeMessage: FC<WelcomeMessageProps> = ({ onExampleClick }) => {
  return (
    <div className="flex flex-col items-center justify-center h-full p-6 text-center">
      <div className="mb-4 p-3 rounded-full bg-primary/10">
        <Sparkles className="w-8 h-8 text-primary" />
      </div>
      
      <h2 className="text-xl font-semibold mb-2">
        👋 Welcome to PrismIQ!
      </h2>
      
      <p className="text-muted-foreground mb-6 max-w-md">
        I&apos;m your AI pricing copilot. Ask me anything about dynamic pricing,
        market analysis, or optimization strategies.
      </p>

      <div className="w-full max-w-md">
        <p className="text-sm font-medium text-muted-foreground mb-3">
          Try asking:
        </p>
        <div className="flex flex-col gap-2">
          {EXAMPLE_QUESTIONS.map((question) => (
            <button
              key={question}
              onClick={() => onExampleClick(question)}
              className="text-left px-4 py-2 rounded-lg border border-border bg-card hover:bg-accent transition-colors text-sm"
            >
              {question}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

