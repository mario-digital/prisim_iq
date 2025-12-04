'use client';

import type { FC, ReactNode } from 'react';
import { User, Star, History, Award, Crown, Gem, Medal } from 'lucide-react';
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
import { cn } from '@/lib/utils';

interface LoyaltyOption {
  value: MarketContext['customer_loyalty_status'];
  label: string;
  description: string;
  icon: ReactNode;
  badgeColor: string;
}

const LOYALTY_OPTIONS: LoyaltyOption[] = [
  {
    value: 'Bronze',
    label: 'Bronze',
    description: 'New member',
    icon: <Medal className="h-4 w-4" />,
    badgeColor: 'bg-amber-700/10 text-amber-700 border-amber-700/20',
  },
  {
    value: 'Silver',
    label: 'Silver',
    description: 'Regular rider',
    icon: <Award className="h-4 w-4" />,
    badgeColor: 'bg-slate-400/10 text-slate-500 border-slate-400/20',
  },
  {
    value: 'Gold',
    label: 'Gold',
    description: 'Frequent rider',
    icon: <Crown className="h-4 w-4" />,
    badgeColor: 'bg-yellow-500/10 text-yellow-600 border-yellow-500/20',
  },
  {
    value: 'Platinum',
    label: 'Platinum',
    description: 'VIP member',
    icon: <Gem className="h-4 w-4" />,
    badgeColor: 'bg-cyan-500/10 text-cyan-600 border-cyan-500/20',
  },
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
            <SelectValue>
              {(() => {
                const selected = LOYALTY_OPTIONS.find(o => o.value === context.customer_loyalty_status);
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
            {LOYALTY_OPTIONS.map((option) => (
              <SelectItem key={option.value} value={option.value} className="py-2">
                <div className="flex items-center gap-3">
                  <span className={cn('flex items-center justify-center h-7 w-7 rounded-md border', option.badgeColor)}>
                    {option.icon}
                  </span>
                  <div className="flex flex-col">
                    <span className="font-medium text-sm">{option.label}</span>
                    <span className="text-xs text-muted-foreground">{option.description}</span>
                  </div>
                </div>
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
