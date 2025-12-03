'use client';

import type { FC } from 'react';
import { KPICard } from './KPICard';
import { ExecutiveActions } from './ExecutiveActions';
import {
  TrendingUp,
  FileCheck,
  ShieldCheck,
  AlertTriangle,
} from 'lucide-react';
import { mockExecutiveData, type ExecutiveData } from './mockData';

interface KPIPanelProps {
  /** Executive data to display. Falls back to mock data if not provided. */
  data?: ExecutiveData | null;
}

export const KPIPanel: FC<KPIPanelProps> = ({ data }) => {
  // Use provided data or fall back to mock data
  const kpiData = data ?? mockExecutiveData;

  return (
    <div className="flex flex-col gap-4 p-4 h-full">
      <h2 className="text-lg font-semibold text-foreground">Key Metrics</h2>

      <div className="flex flex-col gap-3 flex-1">
        <KPICard
          title="Total Profit Uplift"
          value={`+${kpiData.profitUplift}%`}
          subtitle="vs. baseline pricing"
          icon={<TrendingUp className="h-4 w-4" />}
          trend="up"
          variant="success"
        />

        <KPICard
          title="Recommendations Analyzed"
          value={kpiData.recommendationsAnalyzed}
          subtitle="pricing decisions"
          icon={<FileCheck className="h-4 w-4" />}
        />

        <KPICard
          title="Compliance Rate"
          value={`${kpiData.complianceRate}%`}
          subtitle="all rules satisfied"
          icon={<ShieldCheck className="h-4 w-4" />}
          variant="success"
        />

        <KPICard
          title="Risk Alerts"
          value={kpiData.riskAlerts}
          subtitle={
            kpiData.riskAlerts === 0
              ? 'no issues detected'
              : 'require attention'
          }
          icon={<AlertTriangle className="h-4 w-4" />}
          variant={kpiData.riskAlerts === 0 ? 'success' : 'danger'}
        />
      </div>

      <div className="pt-4 border-t">
        <ExecutiveActions />
      </div>
    </div>
  );
};

