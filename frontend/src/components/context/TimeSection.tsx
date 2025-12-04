'use client';

import type { FC, ReactNode } from 'react';
import { Clock, Sunrise, Sun, Sunset, Moon } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { useContextStore, type MarketContext } from '@/stores/contextStore';
import { cn } from '@/lib/utils';

interface TimeOption {
  value: MarketContext['time_of_booking'];
  label: string;
  timeRange: string;
  icon: ReactNode;
  badgeColor: string;
}

const TIME_OPTIONS: TimeOption[] = [
  {
    value: 'Morning',
    label: 'Morning',
    timeRange: '6am - 12pm',
    icon: <Sunrise className="h-4 w-4" />,
    badgeColor: 'bg-orange-500/10 text-orange-600 border-orange-500/20',
  },
  {
    value: 'Afternoon',
    label: 'Afternoon',
    timeRange: '12pm - 5pm',
    icon: <Sun className="h-4 w-4" />,
    badgeColor: 'bg-yellow-500/10 text-yellow-600 border-yellow-500/20',
  },
  {
    value: 'Evening',
    label: 'Evening',
    timeRange: '5pm - 9pm',
    icon: <Sunset className="h-4 w-4" />,
    badgeColor: 'bg-purple-500/10 text-purple-600 border-purple-500/20',
  },
  {
    value: 'Night',
    label: 'Night',
    timeRange: '9pm - 6am',
    icon: <Moon className="h-4 w-4" />,
    badgeColor: 'bg-indigo-500/10 text-indigo-600 border-indigo-500/20',
  },
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
            <SelectValue>
              {(() => {
                const selected = TIME_OPTIONS.find(o => o.value === context.time_of_booking);
                if (!selected) return null;
                return (
                  <span className="flex items-center gap-2">
                    <span className={cn('flex items-center justify-center h-5 w-5 rounded border', selected.badgeColor)}>
                      {selected.icon}
                    </span>
                    <span>{selected.label}</span>
                  </span>
                );
              })()}
            </SelectValue>
          </SelectTrigger>
          <SelectContent>
            {TIME_OPTIONS.map((option) => (
              <SelectItem key={option.value} value={option.value} className="py-2">
                <div className="flex items-center gap-3">
                  <span className={cn('flex items-center justify-center h-7 w-7 rounded-md border', option.badgeColor)}>
                    {option.icon}
                  </span>
                  <div className="flex flex-col">
                    <span className="font-medium text-sm">{option.label}</span>
                    <span className="text-xs text-muted-foreground">{option.timeRange}</span>
                  </div>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
};
