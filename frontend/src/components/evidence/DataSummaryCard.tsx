'use client';

import type { FC } from 'react';
import { Database, Columns, Rows } from 'lucide-react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from '@/components/ui/card';
import type { DataCard } from './types';

interface DataSummaryCardProps {
  card: DataCard | null;
}

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

  return (
    <Card className="bg-card/50">
      <CardHeader className="pb-2 pt-3 px-3">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Database className="h-4 w-4 text-primary" />
          {dataset_name}
        </CardTitle>
      </CardHeader>
      <CardContent className="px-3 pb-3 space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-muted-foreground">Version</span>
          <span className="font-mono">{version}</span>
        </div>
        <div className="flex items-center justify-between text-xs">
          <span className="text-muted-foreground flex items-center gap-1">
            <Rows className="h-3 w-3" /> Rows
          </span>
          <span className="font-medium">
            {statistics.row_count.toLocaleString()}
          </span>
        </div>
        <div className="flex items-center justify-between text-xs">
          <span className="text-muted-foreground flex items-center gap-1">
            <Columns className="h-3 w-3" /> Columns
          </span>
          <span className="font-medium">{statistics.column_count}</span>
        </div>
        <div className="grid grid-cols-2 gap-2 pt-1 border-t border-border/50 text-xs">
          <div>
            <span className="text-muted-foreground">Numeric: </span>
            <span>{statistics.numeric_features}</span>
          </div>
          <div>
            <span className="text-muted-foreground">Categorical: </span>
            <span>{statistics.categorical_features}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

