'use client';

import type { FC } from 'react';
import { Lightbulb, ArrowRight, TrendingUp, Clock, MapPin } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';

export interface Opportunity {
  title: string;
  description: string;
  impact: string;
  category: 'revenue' | 'efficiency' | 'timing' | 'location';
  priority: 'high' | 'medium' | 'low';
}

interface TopOpportunitiesProps {
  opportunities: Opportunity[];
}

const categoryIcons = {
  revenue: TrendingUp,
  efficiency: Lightbulb,
  timing: Clock,
  location: MapPin,
};

const categoryColors = {
  revenue: 'text-emerald-400',
  efficiency: 'text-cyan-400',
  timing: 'text-amber-400',
  location: 'text-purple-400',
};

export const TopOpportunities: FC<TopOpportunitiesProps> = ({ opportunities }) => {
  return (
    <Card className="bg-card/50 border-border/50">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <Lightbulb className="h-4 w-4 text-amber-400" />
          <CardTitle className="text-sm font-medium">Top Opportunities</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {opportunities.map((opp, index) => {
          const Icon = categoryIcons[opp.category];
          const colorClass = categoryColors[opp.category];
          
          return (
            <div 
              key={index} 
              className={cn(
                "p-3 rounded-lg border transition-colors",
                opp.priority === 'high' && "bg-gradient-to-r from-amber-500/5 to-transparent border-amber-500/20",
                opp.priority === 'medium' && "bg-card border-border/50",
                opp.priority === 'low' && "bg-muted/30 border-transparent"
              )}
            >
              <div className="flex items-start gap-3">
                <div className={cn('mt-0.5', colorClass)}>
                  <Icon className="h-4 w-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <h4 className="text-sm font-medium text-foreground truncate">
                      {opp.title}
                    </h4>
                    <span className={cn(
                      "text-xs font-semibold shrink-0",
                      opp.priority === 'high' && "text-emerald-400"
                    )}>
                      {opp.impact}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground line-clamp-2">
                    {opp.description}
                  </p>
                </div>
                <ArrowRight className="h-4 w-4 text-muted-foreground/50 shrink-0 mt-0.5" />
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
};

