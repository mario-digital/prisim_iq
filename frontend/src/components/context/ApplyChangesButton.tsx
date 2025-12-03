'use client';

import type { FC } from 'react';
import { Play, Loader2, AlertCircle, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useContextStore } from '@/stores/contextStore';
import { usePricingStore } from '@/stores/pricingStore';

export const ApplyChangesButton: FC = () => {
  const { context, isLoading, setLoading } = useContextStore();
  const { fetchPricing, isLoading: pricingLoading, error, setError } = usePricingStore();

  const loading = isLoading || pricingLoading;

  const handleApplyChanges = async () => {
    setLoading(true);
    setError(null); // Clear any previous error
    try {
      await fetchPricing(context);
    } finally {
      setLoading(false);
    }
  };

  const handleDismissError = () => {
    setError(null);
  };

  return (
    <div className="space-y-2">
      <Button
        onClick={handleApplyChanges}
        disabled={loading}
        className="w-full"
        size="lg"
      >
        {loading ? (
          <>
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            Calculating...
          </>
        ) : (
          <>
            <Play className="h-4 w-4 mr-2" />
            Apply Changes
          </>
        )}
      </Button>

      {/* Error feedback */}
      {error && (
        <div className="flex items-start gap-2 p-2 rounded-md bg-destructive/10 text-destructive text-sm">
          <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
          <span className="flex-1">{error}</span>
          <button
            onClick={handleDismissError}
            className="p-0.5 hover:bg-destructive/20 rounded transition-colors"
            aria-label="Dismiss error"
          >
            <X className="h-3 w-3" />
          </button>
        </div>
      )}
    </div>
  );
};

