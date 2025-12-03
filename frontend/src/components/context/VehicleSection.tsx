'use client';

import type { FC } from 'react';
import { Car, Clock, DollarSign } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useContextStore, type MarketContext } from '@/stores/contextStore';

const VEHICLE_OPTIONS: { value: MarketContext['vehicle_type']; label: string; icon: string }[] = [
  { value: 'Economy', label: 'Economy', icon: '🚗' },
  { value: 'Premium', label: 'Premium', icon: '🚙' },
];

export const VehicleSection: FC = () => {
  const { context, updateContext } = useContextStore();

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Car className="h-4 w-4 text-muted-foreground" />
        <h3 className="text-sm font-semibold">Vehicle</h3>
      </div>

      {/* Vehicle Type */}
      <div className="space-y-2">
        <Label htmlFor="vehicle-type" className="text-xs text-muted-foreground">
          Vehicle Type
        </Label>
        <Select
          value={context.vehicle_type}
          onValueChange={(v) =>
            updateContext({ vehicle_type: v as MarketContext['vehicle_type'] })
          }
        >
          <SelectTrigger id="vehicle-type" className="h-9">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {VEHICLE_OPTIONS.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                <span className="flex items-center gap-2">
                  <span>{option.icon}</span>
                  <span>{option.label}</span>
                </span>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Expected Duration */}
      <div className="space-y-2">
        <Label htmlFor="ride-duration" className="text-xs text-muted-foreground flex items-center gap-1">
          <Clock className="h-3 w-3" /> Expected Duration (min)
        </Label>
        <Input
          id="ride-duration"
          type="number"
          min={5}
          max={180}
          value={context.expected_ride_duration}
          onChange={(e) => updateContext({ expected_ride_duration: Number(e.target.value) || 5 })}
          className="h-9"
        />
      </div>

      {/* Historical Cost */}
      <div className="space-y-2">
        <Label htmlFor="historical-cost" className="text-xs text-muted-foreground flex items-center gap-1">
          <DollarSign className="h-3 w-3" /> Historical Cost ($)
        </Label>
        <Input
          id="historical-cost"
          type="number"
          min={5}
          max={500}
          step={0.5}
          value={context.historical_cost_of_ride}
          onChange={(e) => updateContext({ historical_cost_of_ride: Number(e.target.value) || 5 })}
          className="h-9"
        />
      </div>
    </div>
  );
};

