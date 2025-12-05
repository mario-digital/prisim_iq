'use client';

import type { FC } from 'react';
import { Brain, Activity, Target, HelpCircle } from 'lucide-react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from '@/components/ui/card';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import type { ModelCard } from './types';
import {
  modelMetricTooltips,
  cardTooltips,
  getValueTooltip,
} from './tooltipDefinitions';

interface ModelSummaryCardProps {
  card: ModelCard;
}

interface MetricRowProps {
  icon?: React.ReactNode;
  label: string;
  value: string | number;
  valueClassName?: string;
  metricKey: string;
}

const MetricRow: FC<MetricRowProps> = ({
  icon,
  label,
  value,
  valueClassName = '',
  metricKey,
}) => {
  const tooltip = modelMetricTooltips[metricKey as keyof typeof modelMetricTooltips];
  const valueTooltip = getValueTooltip(metricKey, value);

  return (
    <div className="flex items-center justify-between text-xs">
      <TooltipProvider delayDuration={200}>
        <Tooltip>
          <TooltipTrigger asChild>
            <span className="text-muted-foreground flex items-center gap-1 cursor-help hover:text-foreground transition-colors">
              {icon}
              {label}
              <HelpCircle className="h-2.5 w-2.5 opacity-50" />
            </span>
          </TooltipTrigger>
          <TooltipContent side="left" className="max-w-[250px]">
            <p className="font-semibold text-xs mb-1">{tooltip?.metric || label}</p>
            <p className="text-xs opacity-80">
              {tooltip?.description || 'No description available'}
            </p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>

      <TooltipProvider delayDuration={200}>
        <Tooltip>
          <TooltipTrigger asChild>
            <span className={`cursor-help hover:opacity-80 transition-opacity ${valueClassName}`}>
              {typeof value === 'number' ? value.toFixed(4) : value}
            </span>
          </TooltipTrigger>
          <TooltipContent side="left" className="max-w-[200px]">
            <p className="text-xs">{valueTooltip}</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    </div>
  );
};

export const ModelSummaryCard: FC<ModelSummaryCardProps> = ({ card }) => {
  const { model_name, model_version, metrics, model_details } = card;

  // Get display name without "Model Card" suffix
  const displayName = model_name.replace(' Demand Predictor', '');

  // Determine which card tooltip to use based on model name
  const getCardTooltipKey = () => {
    const lowerName = model_name.toLowerCase();
    if (lowerName.includes('xgboost')) return 'xgboost';
    if (lowerName.includes('random') || lowerName.includes('forest'))
      return 'random_forest';
    if (lowerName.includes('linear')) return 'linear_regression';
    return 'model_card';
  };

  const cardTooltip = cardTooltips[getCardTooltipKey() as keyof typeof cardTooltips];

  return (
    <TooltipProvider delayDuration={200}>
      <Tooltip>
        <TooltipTrigger asChild>
          <Card className="bg-card/50 cursor-help hover:bg-card/70 transition-colors">
            <CardHeader className="pb-2 pt-3 px-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Brain className="h-4 w-4 text-primary" />
                {displayName}
              </CardTitle>
            </CardHeader>
            <CardContent className="px-3 pb-3 space-y-2">
              <MetricRow
                label="Version"
                value={model_version}
                valueClassName="font-mono"
                metricKey="version"
              />
              <MetricRow
                icon={<Target className="h-3 w-3" />}
                label="R² Score"
                value={`${(metrics.r2_score * 100).toFixed(1)}%`}
                valueClassName="font-medium text-green-600 dark:text-green-400"
                metricKey="r2_score"
              />
              <MetricRow
                icon={<Activity className="h-3 w-3" />}
                label="RMSE"
                value={metrics.rmse}
                valueClassName="font-mono"
                metricKey="rmse"
              />
              <TooltipProvider delayDuration={200}>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <div className="text-xs text-muted-foreground pt-1 border-t border-border/50 cursor-help hover:text-foreground transition-colors">
                      {model_details.architecture}
                    </div>
                  </TooltipTrigger>
                  <TooltipContent side="bottom" className="max-w-[250px]">
                    <p className="font-semibold text-xs mb-1">
                      {modelMetricTooltips.architecture.metric}
                    </p>
                    <p className="text-xs opacity-80">
                      {modelMetricTooltips.architecture.description}
                    </p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </CardContent>
          </Card>
        </TooltipTrigger>
        <TooltipContent side="left" className="max-w-[280px]">
          <p className="font-semibold text-xs mb-1">{cardTooltip?.title}</p>
          <p className="text-xs opacity-80">
            {cardTooltip?.description}
          </p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};
