'use client';

import type { FC } from 'react';

export const Footer: FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="h-10 border-t border-border bg-card px-4 flex items-center justify-between">
      <span className="text-xs text-muted-foreground">
        © {currentYear} PrismIQ - Dynamic Pricing Copilot
      </span>
      <span className="text-xs text-muted-foreground">
        Footer content (Story 4.7)
      </span>
    </footer>
  );
};

