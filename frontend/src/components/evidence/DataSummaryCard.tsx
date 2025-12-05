'use client';

import type { FC } from 'react';
import { Database, Columns, Rows, HelpCircle } from 'lucide-react';
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
import type { DataCard } from './types';
import {
  datasetMetricTooltips,
  cardTooltips,
  getValueTooltip,
} from './tooltipDefinitions';

interface DataSummaryCardProps {
  card: DataCard | null;
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
  const tooltip = datasetMetricTooltips[metricKey as keyof typeof datasetMetricTooltips];
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
              {typeof value === 'number' ? value.toLocaleString() : value}
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

export const DataSummaryCard: FC<DataSummaryCardProps> = ({ card }) => {
  if (!card) {
    return (
      <Card className="bg-card/50">
        <CardHeader className="pb-2 pt-3 px-3">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Database className="h-4 w-4 text-primary" />
            Dataset
          </CardTitle>
        </CardHeader>
        <CardContent className="px-3 pb-3">
          <p className="text-xs text-muted-foreground">Loading...</p>
        </CardContent>
      </Card>
    );
  }

  const { dataset_name, version, statistics } = card;
  const dataCardTooltip = cardTooltips.data_card;

  return (
    <TooltipProvider delayDuration={200}>
      <Tooltip>
        <TooltipTrigger asChild>
          <Card className="bg-card/50 cursor-help hover:bg-card/70 transition-colors">
            <CardHeader className="pb-2 pt-3 px-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Database className="h-4 w-4 text-primary" />
                {dataset_name.replace(/_/g, ' ')}
              </CardTitle>
            </CardHeader>
            <CardContent className="px-3 pb-3 space-y-2">
              <MetricRow
                label="Version"
                value={version}
                valueClassName="font-mono"
                metricKey="version"
              />
              <MetricRow
                icon={<Rows className="h-3 w-3" />}
                label="Rows"
                value={statistics.row_count}
                valueClassName="font-medium"
                metricKey="row_count"
              />
              <MetricRow
                icon={<Columns className="h-3 w-3" />}
                label="Columns"
                value={statistics.column_count}
                valueClassName="font-medium"
                metricKey="column_count"
              />
              <div className="grid grid-cols-2 gap-2 pt-1 border-t border-border/50 text-xs">
                <TooltipProvider delayDuration={200}>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div className="cursor-help hover:text-foreground transition-colors">
                        <span className="text-muted-foreground">Numeric: </span>
                        <span>{statistics.numeric_features}</span>
                        <HelpCircle className="h-2.5 w-2.5 opacity-50 inline ml-1" />
                      </div>
                    </TooltipTrigger>
                    <TooltipContent side="bottom" className="max-w-[220px]">
                      <p className="font-semibold text-xs mb-1">
                        {datasetMetricTooltips.numeric_features.metric}
                      </p>
                      <p className="text-xs opacity-80">
                        {datasetMetricTooltips.numeric_features.description}
                      </p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>

                <TooltipProvider delayDuration={200}>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div className="cursor-help hover:text-foreground transition-colors">
                        <span className="text-muted-foreground">Categorical: </span>
                        <span>{statistics.categorical_features}</span>
                        <HelpCircle className="h-2.5 w-2.5 opacity-50 inline ml-1" />
                      </div>
                    </TooltipTrigger>
                    <TooltipContent side="bottom" className="max-w-[220px]">
                      <p className="font-semibold text-xs mb-1">
                        {datasetMetricTooltips.categorical_features.metric}
                      </p>
                      <p className="text-xs opacity-80">
                        {datasetMetricTooltips.categorical_features.description}
                      </p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
            </CardContent>
          </Card>
        </TooltipTrigger>
        <TooltipContent side="left" className="max-w-[280px]">
          <p className="font-semibold text-xs mb-1">{dataCardTooltip.title}</p>
          <p className="text-xs opacity-80">
            {dataCardTooltip.description}
          </p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};
