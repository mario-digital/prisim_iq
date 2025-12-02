'use client';

import type { FC } from 'react';
import { Zap } from 'lucide-react';

export const Header: FC = () => {
  return (
    <header className="h-14 border-b border-border bg-card px-4 flex items-center justify-between">
      {/* Logo */}
      <div className="flex items-center gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-prism-500 to-prism-700">
          <Zap className="h-4 w-4 text-white" />
        </div>
        <span className="text-lg font-semibold">
          Prism<span className="text-prism-600">IQ</span>
        </span>
      </div>

      {/* Placeholder for additional header content - Grace will implement */}
      <div className="text-xs text-muted-foreground">
        Header content (Story 4.7)
      </div>
    </header>
  );
};

