'use client';

import type { FC } from 'react';
import { SlidersHorizontal, RotateCcw } from 'lucide-react';
import { Slider } from '@/components/ui/slider';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { useContextStore } from '@/stores/contextStore';

export const ScenarioControls: FC = () => {
  const { context, updateContext, resetContext } = useContextStore();

  const handleDemandChange = (value: number[]) => {
    // Adjust riders based on demand multiplier (1-4x)
    const multiplier = value[0];
    updateContext({ number_of_riders: Math.round(25 * multiplier) });
  };

  const handleSupplyChange = (value: number[]) => {
    // Adjust drivers based on supply level (10-50)
    updateContext({ number_of_drivers: value[0] });
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="h-4 w-4 text-muted-foreground" />
          <h3 className="text-sm font-semibold">Scenario Controls</h3>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={resetContext}
          className="h-7 text-xs"
        >
          <RotateCcw className="h-3 w-3 mr-1" />
          Reset
        </Button>
      </div>

      {/* Demand Slider */}
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <Label className="text-xs text-muted-foreground">Demand Level</Label>
          <span className="text-xs font-medium">
            {context.number_of_riders} riders
          </span>
        </div>
        <Slider
          value={[context.number_of_riders / 25]}
          onValueChange={handleDemandChange}
          min={1}
          max={4}
          step={0.5}
          className="py-1"
        />
        <div className="flex justify-between text-[10px] text-muted-foreground">
          <span>Low</span>
          <span>High</span>
        </div>
      </div>

      {/* Supply Slider */}
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <Label className="text-xs text-muted-foreground">Supply Level</Label>
          <span className="text-xs font-medium">
            {context.number_of_drivers} drivers
          </span>
        </div>
        <Slider
          value={[context.number_of_drivers]}
          onValueChange={(v) => handleSupplyChange(v)}
          min={10}
          max={50}
          step={5}
          className="py-1"
        />
        <div className="flex justify-between text-[10px] text-muted-foreground">
          <span>10</span>
          <span>50</span>
        </div>
      </div>
    </div>
  );
};

