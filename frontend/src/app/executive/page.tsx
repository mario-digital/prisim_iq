'use client';

import { useCallback, useEffect, useState } from 'react';
import { MasterLayout } from '@/components/layout';
import { useLayoutStore } from '@/stores/layoutStore';
import { SummaryDashboard, KPIPanel, type ExecutiveData } from '@/components/executive';

export default function ExecutivePage() {
  const { setLeftCollapsed } = useLayoutStore();
  const [executiveData, setExecutiveData] = useState<ExecutiveData | null>(null);

  // Collapse left panel on mount for executive view
  useEffect(() => {
    setLeftCollapsed(true);
  }, [setLeftCollapsed]);

  // Memoize callback to prevent unnecessary re-renders
  const handleDataLoaded = useCallback((data: ExecutiveData) => {
    setExecutiveData(data);
  }, []);

  return (
    <MasterLayout
      centerContent={<SummaryDashboard onDataLoaded={handleDataLoaded} />}
      rightContent={<KPIPanel data={executiveData} />}
    />
  );
}
