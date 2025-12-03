'use client';

import type { FC } from 'react';
import { Brain, Activity, Target } from 'lucide-react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from '@/components/ui/card';
import type { ModelCard } from './types';

interface ModelSummaryCardProps {
  card: ModelCard;
}

export const ModelSummaryCard: FC<ModelSummaryCardProps> = ({ card }) => {
  const { model_name, model_version, metrics, model_details } = card;

  // Get display name without "Model Card" suffix
  const displayName = model_name.replace(' Demand Predictor', '');

  return (
    <Card className="bg-card/50">
      <CardHeader className="pb-2 pt-3 px-3">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Brain className="h-4 w-4 text-primary" />
          {displayName}
        </CardTitle>
      </CardHeader>
      <CardContent className="px-3 pb-3 space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-muted-foreground">Version</span>
          <span className="font-mono">{model_version}</span>
        </div>
        <div className="flex items-center justify-between text-xs">
          <span className="text-muted-foreground flex items-center gap-1">
            <Target className="h-3 w-3" /> R² Score
          </span>
          <span className="font-medium text-green-600 dark:text-green-400">
            {(metrics.r2_score * 100).toFixed(1)}%
          </span>
        </div>
        <div className="flex items-center justify-between text-xs">
          <span className="text-muted-foreground flex items-center gap-1">
            <Activity className="h-3 w-3" /> RMSE
          </span>
          <span className="font-mono">{metrics.rmse.toFixed(4)}</span>
        </div>
        <div className="text-xs text-muted-foreground pt-1 border-t border-border/50">
          {model_details.architecture}
        </div>
      </CardContent>
    </Card>
  );
};

