/**
 * Centralized mock data for executive dashboard components.
 * This ensures consistency across SummaryDashboard and KPIPanel.
 */

export interface SegmentPerformance {
  segment: string;
  uplift: number;
}

export interface ExecutiveData {
  profitUplift: number;
  baseline: number;
  keyInsight: string;
  segmentPerformance: SegmentPerformance[];
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
    { segment: 'Urban Peak', uplift: 32 },
    { segment: 'Urban Standard', uplift: 28 },
    { segment: 'Suburban Peak', uplift: 22 },
    { segment: 'Suburban Standard', uplift: 18 },
    { segment: 'Rural', uplift: 12 },
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

