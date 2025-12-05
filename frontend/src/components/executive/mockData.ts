/**
 * Centralized mock data for executive dashboard components.
 * This ensures consistency across SummaryDashboard and KPIPanel.
 */

import type { SegmentPerformanceData } from '@/components/visualizations';
import type { MetricCardData } from './MetricCards';
import type { ModelMetric } from './ModelPerformanceCard';
import type { Opportunity } from './TopOpportunities';

export interface ExecutiveData {
  // Hero metrics
  profitUplift: number;
  baseline: number;
  
  // Key narrative
  keyInsight: string;
  
  // Segment data
  segmentPerformance: SegmentPerformanceData[];
  
  // KPI metrics
  metrics: MetricCardData[];
  
  // Model performance
  models: ModelMetric[];
  modelAgreement: number;
  
  // Opportunities
  opportunities: Opportunity[];
  
  // Legacy fields (for backward compatibility)
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
    'Dynamic pricing optimization delivered a **24.3% profit improvement** across 1,247 pricing decisions this week. ' +
    'The Urban Peak Premium segment showed the highest gains at **+32%**, driven by improved demand forecasting during rush hours. ' +
    'Business rule compliance remained at **100%** with zero price cap violations. ' +
    'Key driver: Weather-adjusted pricing during the Tuesday rainstorm captured an additional **$12,400** in surge-appropriate revenue.',
  
  segmentPerformance: [
    { segment: 'Urban Peak', baseline: 1000, optimized: 1320, improvement: 32 },
    { segment: 'Urban Standard', baseline: 850, optimized: 1088, improvement: 28 },
    { segment: 'Suburban Peak', baseline: 720, optimized: 878, improvement: 22 },
    { segment: 'Suburban Standard', baseline: 650, optimized: 767, improvement: 18 },
    { segment: 'Rural', baseline: 480, optimized: 538, improvement: 12 },
  ],
  
  metrics: [
    {
      label: 'Revenue Impact',
      value: '$847K',
      change: 24.3,
      changeLabel: 'vs. baseline pricing',
      icon: 'revenue',
      trend: 'up',
    },
    {
      label: 'Decisions Made',
      value: '1,247',
      change: 12,
      changeLabel: 'this week',
      icon: 'recommendations',
      trend: 'up',
    },
    {
      label: 'Avg. Profit/Transaction',
      value: '$23.94',
      change: 18.5,
      changeLabel: 'vs. $20.19 baseline',
      icon: 'profit',
      trend: 'up',
    },
    {
      label: 'Model Accuracy',
      value: '94.2%',
      change: 2.1,
      changeLabel: 'R² score improvement',
      icon: 'accuracy',
      trend: 'up',
    },
    {
      label: 'Rule Compliance',
      value: '100%',
      changeLabel: '0 violations',
      icon: 'compliance',
      trend: 'neutral',
    },
    {
      label: 'Risk Alerts',
      value: '0',
      changeLabel: 'no anomalies detected',
      icon: 'risk',
      trend: 'neutral',
    },
    {
      label: 'Customers Served',
      value: '8,432',
      change: 8.3,
      changeLabel: 'unique customers',
      icon: 'customers',
      trend: 'up',
    },
    {
      label: 'Avg. Response Time',
      value: '142ms',
      change: -15,
      changeLabel: 'faster than last week',
      icon: 'efficiency',
      trend: 'up',
    },
  ],
  
  models: [
    { name: 'XGBoost (Primary)', accuracy: 98.6, status: 'healthy' },
    { name: 'Random Forest', accuracy: 94.2, status: 'healthy' },
    { name: 'Linear Regression', accuracy: 87.1, status: 'healthy' },
  ],
  modelAgreement: 72,
  
  opportunities: [
    {
      title: 'Evening Rush Optimization',
      description: 'Increase dynamic range during 5-7 PM window. Current caps may be leaving 8-12% profit on the table.',
      impact: '+$45K/mo',
      category: 'timing',
      priority: 'high',
    },
    {
      title: 'Suburban Premium Launch',
      description: 'Introduce premium tier in suburban markets. Data shows 23% of suburban customers willing to pay more.',
      impact: '+$28K/mo',
      category: 'location',
      priority: 'high',
    },
    {
      title: 'Weather Integration Enhancement',
      description: 'Real-time weather API showing 15% better demand prediction during adverse conditions.',
      impact: '+$18K/mo',
      category: 'efficiency',
      priority: 'medium',
    },
    {
      title: 'Loyalty Tier Adjustment',
      description: 'Gold tier discount (currently 5%) could be reduced to 3% with minimal churn risk based on elasticity analysis.',
      impact: '+$12K/mo',
      category: 'revenue',
      priority: 'medium',
    },
  ],
  
  // Legacy
  recommendationsAnalyzed: 1247,
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
