'use client';

import type { FC } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Lightbulb } from 'lucide-react';

interface KeyInsightProps {
  /** The insight narrative text */
  insight: string;
}

export const KeyInsight: FC<KeyInsightProps> = ({ insight }) => {
  return (
    <Card className="bg-primary/5 border-primary/20">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-primary" />
          Key Insight
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-base leading-relaxed text-foreground/90">
          {insight}
        </p>
      </CardContent>
    </Card>
  );
};

