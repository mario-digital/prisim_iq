'use client';

import type { FC } from 'react';
import { Brain, CheckCircle2, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

export interface ModelMetric {
  name: string;
  accuracy: number;
  status: 'healthy' | 'warning' | 'critical';
}

interface ModelPerformanceCardProps {
  models: ModelMetric[];
  overallAgreement: number;
}

export const ModelPerformanceCard: FC<ModelPerformanceCardProps> = ({ 
  models, 
  overallAgreement 
}) => {
  const agreementStatus = overallAgreement >= 80 ? 'convergent' : overallAgreement >= 60 ? 'moderate' : 'divergent';
  
  return (
    <Card className="bg-card/50 border-border/50">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="h-4 w-4 text-purple-400" />
            <CardTitle className="text-sm font-medium">Model Performance</CardTitle>
          </div>
          <div className={cn(
            'text-xs font-medium px-2 py-1 rounded-full',
            agreementStatus === 'convergent' && 'text-emerald-400 bg-emerald-400/10',
            agreementStatus === 'moderate' && 'text-amber-400 bg-amber-400/10',
            agreementStatus === 'divergent' && 'text-rose-400 bg-rose-400/10'
          )}>
            {overallAgreement}% Agreement
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {models.map((model, index) => (
          <div key={index} className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                {model.status === 'healthy' ? (
                  <CheckCircle2 className="h-3 w-3 text-emerald-400" />
                ) : (
                  <AlertCircle className="h-3 w-3 text-amber-400" />
                )}
                <span className="text-muted-foreground">{model.name}</span>
              </div>
              <span className="font-medium text-foreground">{model.accuracy}%</span>
            </div>
            <Progress 
              value={model.accuracy} 
              className="h-1.5"
            />
          </div>
        ))}
        
        <div className="pt-2 border-t border-border/50 text-xs text-muted-foreground">
          <span className="font-medium text-foreground">{models.length} models</span> actively optimizing prices
        </div>
      </CardContent>
    </Card>
  );
};

