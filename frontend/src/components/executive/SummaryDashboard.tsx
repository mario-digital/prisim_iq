'use client';

import type { FC } from 'react';
import { useEffect, useState } from 'react';
import { ProfitUpliftHero } from './ProfitUpliftHero';
import { KeyInsight } from './KeyInsight';
import { MetricCards } from './MetricCards';
import { ModelPerformanceCard } from './ModelPerformanceCard';
import { TopOpportunities } from './TopOpportunities';
import { SegmentPerformanceChart } from '@/components/visualizations';
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
        <div className="max-w-5xl mx-auto space-y-6">
          <div className="text-center py-8">
            <Skeleton className="h-4 w-32 mx-auto mb-4" />
            <Skeleton className="h-16 w-48 mx-auto mb-4" />
            <Skeleton className="h-4 w-40 mx-auto" />
          </div>
          <div className="grid grid-cols-4 gap-3">
            {[1,2,3,4].map(i => <Skeleton key={i} className="h-24" />)}
          </div>
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 p-6 overflow-y-auto">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Hero metric */}
        <ProfitUpliftHero value={data.profitUplift} baseline={data.baseline} />

        {/* KPI Metrics Grid */}
        <MetricCards metrics={data.metrics} />

        {/* Key insight narrative */}
        <KeyInsight insight={data.keyInsight} />

        {/* Two-column layout for charts and insights */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Segment performance chart */}
          <SegmentPerformanceChart data={data.segmentPerformance} />
          
          {/* Model Performance */}
          <ModelPerformanceCard 
            models={data.models} 
            overallAgreement={data.modelAgreement} 
          />
        </div>

        {/* Top Opportunities */}
        <TopOpportunities opportunities={data.opportunities} />
      </div>
    </div>
  );
};
