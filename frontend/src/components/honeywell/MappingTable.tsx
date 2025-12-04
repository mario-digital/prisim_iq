'use client';

import type { FC } from 'react';
import { useCallback, useEffect, useState } from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { getHoneywellMapping } from '@/services/evidenceService';
import type { HoneywellMappingResponse } from '@/services/evidenceService';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';

/**
 * Loading skeleton for the mapping table.
 */
const TableSkeleton: FC = () => (
  <div className="border rounded-lg overflow-hidden">
    <div className="bg-muted px-4 py-3">
      <div className="flex gap-4">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-4 w-48" />
      </div>
    </div>
    <div className="divide-y">
      {[1, 2, 3, 4, 5].map((i) => (
        <div key={i} className="px-4 py-3 flex gap-4">
          <Skeleton className="h-4 w-28" />
          <Skeleton className="h-4 w-36" />
          <Skeleton className="h-4 w-56" />
        </div>
      ))}
    </div>
  </div>
);

/**
 * MappingTable displays the ride-sharing to Honeywell concept mapping.
 * Fetches data from API with caching and shows loading skeleton.
 * Includes error state handling with retry capability.
 */
export const MappingTable: FC = () => {
  const [mapping, setMapping] = useState<HoneywellMappingResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchMapping = useCallback(() => {
    setIsLoading(true);
    setError(null);
    getHoneywellMapping()
      .then(setMapping)
      .catch((err) => setError(err instanceof Error ? err : new Error('Failed to load mapping')))
      .finally(() => setIsLoading(false));
  }, []);

  useEffect(() => {
    fetchMapping();
  }, [fetchMapping]);

  if (isLoading) {
    return <TableSkeleton />;
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-8 gap-3 text-destructive">
        <AlertCircle className="h-8 w-8" />
        <p className="text-sm font-medium">Failed to load mapping data</p>
        <Button
          variant="outline"
          size="sm"
          onClick={fetchMapping}
          className="gap-2"
        >
          <RefreshCw className="h-4 w-4" />
          Try Again
        </Button>
      </div>
    );
  }

  if (!mapping || mapping.mappings.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No mapping data available.
      </div>
    );
  }

  return (
    <div className="border rounded-lg overflow-hidden">
      <table className="w-full">
        <thead className="bg-muted">
          <tr>
            <th className="px-4 py-3 text-left font-medium text-sm">
              Ride-Sharing Concept
            </th>
            <th className="px-4 py-3 text-left font-medium text-sm">
              Honeywell Equivalent
            </th>
            <th className="px-4 py-3 text-left font-medium text-sm">
              Rationale
            </th>
          </tr>
        </thead>
        <tbody className="divide-y">
          {mapping.mappings.map((row, i) => (
            <tr key={i} className="hover:bg-muted/50 transition-colors">
              <td className="px-4 py-3 font-medium text-sm">
                {row.ride_sharing_concept}
              </td>
              <td className="px-4 py-3 text-sm">
                {row.honeywell_equivalent}
              </td>
              <td className="px-4 py-3 text-sm text-muted-foreground">
                {row.rationale}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

