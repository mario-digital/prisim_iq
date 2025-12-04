'use client';

import type { FC } from 'react';

/**
 * Brand component displaying PrismIQ logo and tagline.
 * Per PRD: "🔷 PrismIQ" + "Dynamic Pricing Copilot" tagline.
 */
export const Brand: FC = () => {
  return (
    <div className="flex items-center gap-2">
      {/* Diamond emoji as logo per PRD */}
      <span className="text-2xl" role="img" aria-label="PrismIQ logo">
        🔷
      </span>
      
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


