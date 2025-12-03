'use client';

import type { FC } from 'react';
import { Zap } from 'lucide-react';

/**
 * Brand component displaying PrismIQ logo and tagline.
 * Used in the Header for brand identity.
 */
export const Brand: FC = () => {
  return (
    <div className="flex items-center gap-3">
      {/* Logo */}
      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-prism-500 to-prism-700 shadow-sm">
        <Zap className="h-5 w-5 text-white" />
      </div>
      
      {/* Text */}
      <div className="flex flex-col">
        <h1 className="text-lg font-bold leading-tight">
          Prism<span className="text-prism-600">IQ</span>
        </h1>
        <p className="text-xs text-muted-foreground leading-tight">
          Dynamic Pricing Copilot
        </p>
      </div>
    </div>
  );
};


