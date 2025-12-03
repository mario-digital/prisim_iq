'use client';

import type { FC } from 'react';
import { User, Star, History } from 'lucide-react';
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

const LOYALTY_OPTIONS: { value: MarketContext['customer_loyalty_status']; label: string; color: string }[] = [
  { value: 'Bronze', label: 'Bronze', color: 'text-amber-600' },
  { value: 'Silver', label: 'Silver', color: 'text-slate-400' },
  { value: 'Gold', label: 'Gold', color: 'text-yellow-500' },
  { value: 'Platinum', label: 'Platinum', color: 'text-cyan-400' },
];

export const CustomerSection: FC = () => {
  const { context, updateContext } = useContextStore();

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <User className="h-4 w-4 text-muted-foreground" />
        <h3 className="text-sm font-semibold">Customer</h3>
      </div>

      {/* Loyalty Status */}
      <div className="space-y-2">
        <Label htmlFor="loyalty-status" className="text-xs text-muted-foreground">
          Loyalty Status
        </Label>
        <Select
          value={context.customer_loyalty_status}
          onValueChange={(v) =>
            updateContext({ customer_loyalty_status: v as MarketContext['customer_loyalty_status'] })
          }
        >
          <SelectTrigger id="loyalty-status" className="h-9">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {LOYALTY_OPTIONS.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                <span className={option.color}>{option.label}</span>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Past Rides */}
      <div className="space-y-2">
        <Label htmlFor="past-rides" className="text-xs text-muted-foreground flex items-center gap-1">
          <History className="h-3 w-3" /> Past Rides
        </Label>
        <Input
          id="past-rides"
          type="number"
          min={0}
          max={1000}
          value={context.number_of_past_rides}
          onChange={(e) => updateContext({ number_of_past_rides: Number(e.target.value) || 0 })}
          className="h-9"
        />
      </div>

      {/* Average Ratings */}
      <div className="space-y-2">
        <Label htmlFor="avg-ratings" className="text-xs text-muted-foreground flex items-center gap-1">
          <Star className="h-3 w-3" /> Average Rating
        </Label>
        <Input
          id="avg-ratings"
          type="number"
          min={1}
          max={5}
          step={0.1}
          value={context.average_ratings}
          onChange={(e) => {
            const val = parseFloat(e.target.value);
            if (val >= 1 && val <= 5) {
              updateContext({ average_ratings: val });
            }
          }}
          className="h-9"
        />
        <div className="flex items-center gap-1">
          {[1, 2, 3, 4, 5].map((star) => (
            <Star
              key={star}
              className={`h-3 w-3 ${
                star <= Math.round(context.average_ratings)
                  ? 'fill-yellow-400 text-yellow-400'
                  : 'text-muted-foreground'
              }`}
            />
          ))}
          <span className="text-xs text-muted-foreground ml-1">
            ({context.average_ratings.toFixed(1)})
          </span>
        </div>
      </div>
    </div>
  );
};

