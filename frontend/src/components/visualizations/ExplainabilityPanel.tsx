'use client';

import type { FC } from 'react';
import { usePricingStore } from '@/stores/pricingStore';
import { RecommendationCard } from './RecommendationCard';
import { FeatureImportanceChart } from './FeatureImportanceChart';
import { DecisionTrace } from './DecisionTrace';
import { DemandCurveChart } from './DemandCurveChart';
import { ProfitCurveChart } from './ProfitCurveChart';
import { SensitivitySection } from './SensitivitySection';
import { BusinessRulesList } from './BusinessRulesList';
import { Skeleton } from '@/components/ui/skeleton';

/**
 * Main explainability panel containing all visualization components.
 * Displays pricing recommendation with detailed explanations.
 */
export const ExplainabilityPanel: FC = () => {
  const { explanation, isLoading } = usePricingStore();

  if (isLoading) {
    return <ExplainabilityPanelSkeleton />;
  }

  if (!explanation) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-6 text-center">
        <div className="text-muted-foreground">
          <p className="text-sm">No pricing analysis available yet.</p>
          <p className="text-xs mt-2">
            Use the chat to request a price optimization.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 p-4 overflow-y-auto h-full">
      {/* Recommendation Card - Always visible at top */}
      <RecommendationCard
        result={explanation.result}
        profitUpliftPercent={explanation.profitUpliftPercent}
      />

      {/* Feature Importance Chart */}
      <FeatureImportanceChart data={explanation.featureContributions} />

      {/* Decision Trace Accordion */}
      <DecisionTrace steps={explanation.decisionTrace} />

      {/* Demand Curve */}
      <DemandCurveChart
        data={explanation.demandCurve}
        optimalPrice={explanation.optimalPrice}
        currentPrice={explanation.result.recommendedPrice}
      />

      {/* Profit Curve */}
      <ProfitCurveChart
        data={explanation.profitCurve}
        optimalPrice={explanation.optimalPrice}
      />

      {/* Sensitivity Analysis */}
      <SensitivitySection sensitivity={explanation.sensitivity} />

      {/* Business Rules */}
      <BusinessRulesList rules={explanation.businessRules} />
    </div>
  );
};

/**
 * Loading skeleton for the explainability panel.
 */
const ExplainabilityPanelSkeleton: FC = () => {
  return (
    <div className="flex flex-col gap-4 p-4">
      {/* Recommendation card skeleton */}
      <div className="rounded-xl border bg-card p-6">
        <Skeleton className="h-4 w-32 mb-4" />
        <Skeleton className="h-10 w-24 mb-4" />
        <div className="flex gap-4">
          <Skeleton className="h-6 w-20" />
          <Skeleton className="h-6 w-20" />
        </div>
      </div>

      {/* Chart skeletons */}
      <div className="rounded-xl border bg-card p-6">
        <Skeleton className="h-4 w-40 mb-4" />
        <Skeleton className="h-[200px] w-full" />
      </div>

      <div className="rounded-xl border bg-card p-6">
        <Skeleton className="h-4 w-32 mb-4" />
        <Skeleton className="h-[150px] w-full" />
      </div>
    </div>
  );
};

