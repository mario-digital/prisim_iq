'use client';

import type { FC } from 'react';
import { Skeleton } from '@/components/ui/skeleton';
import { ModelSummaryCard } from './ModelSummaryCard';
import { DataSummaryCard } from './DataSummaryCard';
import { EvidenceActions } from './EvidenceActions';
import type { EvidenceResponse } from './types';

interface QuickReferenceProps {
  evidence: EvidenceResponse | null;
  selectedDocId: string;
}

function QuickReferenceSkeleton() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-5 w-32" />
      <Skeleton className="h-28 w-full" />
      <Skeleton className="h-28 w-full" />
      <Skeleton className="h-28 w-full" />
      <Skeleton className="h-24 w-full" />
      <div className="pt-4 border-t space-y-2">
        <Skeleton className="h-9 w-full" />
        <Skeleton className="h-9 w-full" />
        <Skeleton className="h-9 w-full" />
      </div>
    </div>
  );
}

export const QuickReference: FC<QuickReferenceProps> = ({
  evidence,
  selectedDocId,
}) => {
  if (!evidence) {
    return <QuickReferenceSkeleton />;
  }

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-foreground">Quick Reference</h3>

      {/* Model Summary Cards */}
      <div className="space-y-3">
        {evidence.model_cards.map((card) => (
          <ModelSummaryCard key={card.model_name} card={card} />
        ))}
      </div>

      {/* Data Summary Card */}
      <DataSummaryCard card={evidence.data_card} />

      {/* Quick Actions */}
      <EvidenceActions selectedDocId={selectedDocId} />
    </div>
  );
};

