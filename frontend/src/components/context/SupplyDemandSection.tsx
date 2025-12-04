'use client';

import type { FC } from 'react';
import { useMemo } from 'react';
import { TrendingUp, Users, Car } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { useContextStore } from '@/stores/contextStore';

export const SupplyDemandSection: FC = () => {
  const { context, updateContext } = useContextStore();

  const ratio = useMemo(() => {
    if (context.number_of_drivers === 0) return 0;
    return context.number_of_riders / context.number_of_drivers;
  }, [context.number_of_riders, context.number_of_drivers]);

  const ratioInfo = useMemo(() => {
    if (ratio > 2) return { label: 'High Demand', color: 'text-red-500', bg: 'bg-red-500/10' };
    if (ratio > 1) return { label: 'Balanced', color: 'text-yellow-500', bg: 'bg-yellow-500/10' };
    return { label: 'Low Demand', color: 'text-green-500', bg: 'bg-green-500/10' };
  }, [ratio]);

  const handleRatioSliderChange = (value: number[]) => {
    const newRatio = value[0];
    // Keep drivers constant, adjust riders to match ratio (capped at 100)
    const newRiders = Math.round(context.number_of_drivers * newRatio);
    updateContext({ number_of_riders: Math.min(100, Math.max(1, newRiders)) });
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <TrendingUp className="h-4 w-4 text-muted-foreground" />
        <h3 className="text-sm font-semibold">Supply / Demand</h3>
      </div>

      {/* Riders Input */}
      <div className="space-y-2">
        <Label htmlFor="riders" className="text-xs text-muted-foreground flex items-center gap-1">
          <Users className="h-3 w-3" /> Riders
        </Label>
        <Input
          id="riders"
          type="number"
          min={1}
          max={100}
          value={context.number_of_riders}
          onChange={(e) => updateContext({ number_of_riders: Math.min(100, Math.max(1, Number(e.target.value) || 1)) })}
          className="h-9"
        />
      </div>

      {/* Drivers Input */}
      <div className="space-y-2">
        <Label htmlFor="drivers" className="text-xs text-muted-foreground flex items-center gap-1">
          <Car className="h-3 w-3" /> Drivers
        </Label>
        <Input
          id="drivers"
          type="number"
          min={1}
          max={100}
          value={context.number_of_drivers}
          onChange={(e) => updateContext({ number_of_drivers: Math.min(100, Math.max(1, Number(e.target.value) || 1)) })}
          className="h-9"
        />
      </div>

      {/* Ratio Display */}
      <div className={`rounded-md p-2 ${ratioInfo.bg}`}>
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">Supply/Demand Ratio</span>
          <span className={`text-sm font-semibold ${ratioInfo.color}`}>
            {ratio.toFixed(2)}x
          </span>
        </div>
        <div className={`text-xs font-medium ${ratioInfo.color}`}>
          {ratioInfo.label}
        </div>
      </div>

      {/* Quick Adjust Slider */}
      <div className="space-y-2">
        <Label className="text-xs text-muted-foreground">Quick Adjust Ratio</Label>
        <Slider
          value={[ratio]}
          onValueChange={handleRatioSliderChange}
          min={0.5}
          max={4}
          step={0.1}
          className="py-2"
        />
        <div className="flex justify-between text-[10px] text-muted-foreground">
          <span>Low (0.5x)</span>
          <span>High (4x)</span>
        </div>
      </div>
    </div>
  );
};
