'use client';

import type { FC } from 'react';
import { Clock } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { useContextStore, type MarketContext } from '@/stores/contextStore';

const TIME_OPTIONS: { value: MarketContext['time_of_booking']; label: string; icon: string }[] = [
  { value: 'Morning', label: 'Morning (6am-12pm)', icon: '🌅' },
  { value: 'Afternoon', label: 'Afternoon (12pm-5pm)', icon: '☀️' },
  { value: 'Evening', label: 'Evening (5pm-9pm)', icon: '🌆' },
  { value: 'Night', label: 'Night (9pm-6am)', icon: '🌙' },
];

export const TimeSection: FC = () => {
  const { context, updateContext } = useContextStore();

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Clock className="h-4 w-4 text-muted-foreground" />
        <h3 className="text-sm font-semibold">Time</h3>
      </div>
      <div className="space-y-2">
        <Label htmlFor="time-of-booking" className="text-xs text-muted-foreground">
          Time of Booking
        </Label>
        <Select
          value={context.time_of_booking}
          onValueChange={(v) =>
            updateContext({ time_of_booking: v as MarketContext['time_of_booking'] })
          }
        >
          <SelectTrigger id="time-of-booking" className="h-9">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {TIME_OPTIONS.map((option) => (
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
    </div>
  );
};

