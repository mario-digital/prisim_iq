'use client';

import type { FC } from 'react';
import { Gem } from 'lucide-react';

/**
 * Brand component displaying PrismIQ logo and tagline.
 * Features a glowing gem icon with gradient text for dark theme.
 */
export const Brand: FC = () => {
  return (
    <div className="flex items-center gap-3">
      {/* Gem icon with glow effect */}
      <div className="relative">
        <div className="absolute inset-0 bg-cyan-400/30 blur-lg rounded-full" />
        <div className="relative flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-cyan-400 to-blue-500 shadow-lg shadow-cyan-500/25">
          <Gem className="h-5 w-5 text-white" aria-label="PrismIQ logo" />
        </div>
      </div>
      
      {/* Text with gradient */}
      <div className="flex flex-col">
        <h1 className="text-lg font-bold leading-tight">
          <span className="bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
            Prism
          </span>
          <span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
            IQ
          </span>
        </h1>
        <p className="text-xs text-muted-foreground leading-tight">
          Dynamic Pricing Copilot
        </p>
      </div>
    </div>
  );
};


