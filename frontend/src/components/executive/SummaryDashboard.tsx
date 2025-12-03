'use client';

import type { FC } from 'react';
import { useEffect, useState } from 'react';
import { ProfitUpliftHero } from './ProfitUpliftHero';
import { KeyInsight } from './KeyInsight';
import { SegmentPerformanceChart } from './SegmentPerformanceChart';
import { useLayoutStore } from '@/stores/layoutStore';
import { Skeleton } from '@/components/ui/skeleton';
import { fetchExecutiveData, type ExecutiveData } from './mockData';

interface SummaryDashboardProps {
  /** Callback to share fetched data with parent/sibling components */
  onDataLoaded?: (data: ExecutiveData) => void;
}

export const SummaryDashboard: FC<SummaryDashboardProps> = ({ onDataLoaded }) => {
  const { activeTab } = useLayoutStore();
  const [data, setData] = useState<ExecutiveData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch data on mount and when tab becomes active
  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      
      // Fetch from centralized mock data service
      const executiveData = await fetchExecutiveData();
      
      setData(executiveData);
      onDataLoaded?.(executiveData);
      setIsLoading(false);
    };

    // Refresh data when executive tab is active
    if (activeTab === 'executive') {
      loadData();
    }
  }, [activeTab, onDataLoaded]);

  if (isLoading || !data) {
    return (
      <div className="flex-1 p-6 overflow-y-auto">
        <div className="max-w-4xl mx-auto space-y-6">
          <div className="text-center py-8">
            <Skeleton className="h-4 w-32 mx-auto mb-4" />
            <Skeleton className="h-16 w-48 mx-auto mb-4" />
            <Skeleton className="h-4 w-40 mx-auto" />
          </div>
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 p-6 overflow-y-auto">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Hero metric */}
        <ProfitUpliftHero value={data.profitUplift} baseline={data.baseline} />

        {/* Key insight narrative */}
        <KeyInsight insight={data.keyInsight} />

        {/* Segment performance chart */}
        <SegmentPerformanceChart data={data.segmentPerformance} />
      </div>
    </div>
  );
};

