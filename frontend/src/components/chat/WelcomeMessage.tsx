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
      {/* Animated icon with glow */}
      <div className="relative mb-4">
        <div className="absolute inset-0 bg-cyan-400/20 blur-xl rounded-full animate-pulse" />
        <div className="relative p-4 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-blue-500/20 border border-cyan-500/20">
          <Sparkles className="w-8 h-8 text-cyan-400" />
        </div>
      </div>
      
      <h2 className="text-xl font-semibold mb-2 bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
        Welcome to PrismIQ!
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
              className="text-left px-4 py-3 rounded-xl border border-border/50 bg-card/50 hover:bg-accent hover:border-cyan-500/30 transition-all duration-200 text-sm group"
            >
              <span className="text-muted-foreground group-hover:text-foreground transition-colors">
                {question}
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

