/**
 * Centralized mock data for executive dashboard components.
 * This ensures consistency across SummaryDashboard and KPIPanel.
 */

import type { SegmentPerformanceData } from '@/components/visualizations';

export interface ExecutiveData {
  profitUplift: number;
  baseline: number;
  keyInsight: string;
  segmentPerformance: SegmentPerformanceData[];
  recommendationsAnalyzed: number;
  complianceRate: number;
  riskAlerts: number;
}

/**
 * Mock data for executive dashboard demo.
 * In production, this would be fetched from the API.
 */
export const mockExecutiveData: ExecutiveData = {
  profitUplift: 24.3,
  baseline: 35.0,
  keyInsight:
    'Dynamic pricing optimization delivered a 24.3% profit improvement across 150 recommendations. Urban Peak Premium segment showed the highest gains (+32%), while Rural segments benefited from fairness constraints maintaining customer satisfaction.',
  segmentPerformance: [
    { segment: 'Urban Peak', baseline: 1000, optimized: 1320, improvement: 32 },
    { segment: 'Urban Standard', baseline: 850, optimized: 1088, improvement: 28 },
    { segment: 'Suburban Peak', baseline: 720, optimized: 878, improvement: 22 },
    { segment: 'Suburban Standard', baseline: 650, optimized: 767, improvement: 18 },
    { segment: 'Rural', baseline: 480, optimized: 538, improvement: 12 },
  ],
  recommendationsAnalyzed: 150,
  complianceRate: 100,
  riskAlerts: 0,
};

/**
 * Simulate fetching executive data from API.
 * @param delayMs - Simulated network delay in milliseconds
 */
export async function fetchExecutiveData(delayMs = 500): Promise<ExecutiveData> {
  await new Promise((resolve) => setTimeout(resolve, delayMs));
  return mockExecutiveData;
}

