'use client';

import type { FC } from 'react';
import { 
  DollarSign, 
  TrendingUp, 
  Target, 
  ShieldCheck, 
  AlertTriangle,
  BarChart3,
  Users,
  Zap
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';

export interface MetricCardData {
  label: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon: 'revenue' | 'profit' | 'recommendations' | 'compliance' | 'risk' | 'accuracy' | 'customers' | 'efficiency';
  trend?: 'up' | 'down' | 'neutral';
}

interface MetricCardsProps {
  metrics: MetricCardData[];
}

const iconMap = {
  revenue: DollarSign,
  profit: TrendingUp,
  recommendations: BarChart3,
  compliance: ShieldCheck,
  risk: AlertTriangle,
  accuracy: Target,
  customers: Users,
  efficiency: Zap,
};

const iconColorMap = {
  revenue: 'text-emerald-400 bg-emerald-400/10',
  profit: 'text-cyan-400 bg-cyan-400/10',
  recommendations: 'text-blue-400 bg-blue-400/10',
  compliance: 'text-green-400 bg-green-400/10',
  risk: 'text-amber-400 bg-amber-400/10',
  accuracy: 'text-purple-400 bg-purple-400/10',
  customers: 'text-pink-400 bg-pink-400/10',
  efficiency: 'text-orange-400 bg-orange-400/10',
};

export const MetricCards: FC<MetricCardsProps> = ({ metrics }) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {metrics.map((metric, index) => {
        const Icon = iconMap[metric.icon];
        const colorClass = iconColorMap[metric.icon];
        
        return (
          <Card key={index} className="bg-card/50 border-border/50">
            <CardContent className="p-4">
              <div className="flex items-start justify-between mb-2">
                <div className={cn('p-2 rounded-lg', colorClass)}>
                  <Icon className="h-4 w-4" />
                </div>
                {metric.change !== undefined && (
                  <span className={cn(
                    'text-xs font-medium px-1.5 py-0.5 rounded',
                    metric.trend === 'up' && 'text-emerald-400 bg-emerald-400/10',
                    metric.trend === 'down' && 'text-rose-400 bg-rose-400/10',
                    metric.trend === 'neutral' && 'text-slate-400 bg-slate-400/10'
                  )}>
                    {metric.change > 0 ? '+' : ''}{metric.change}%
                  </span>
                )}
              </div>
              <div className="text-2xl font-bold text-foreground mb-1">
                {metric.value}
              </div>
              <div className="text-xs text-muted-foreground">
                {metric.label}
              </div>
              {metric.changeLabel && (
                <div className="text-[10px] text-muted-foreground/70 mt-1">
                  {metric.changeLabel}
                </div>
              )}
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
};

