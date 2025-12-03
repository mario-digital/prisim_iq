'use client';

import type { FC } from 'react';
import { MapPin } from 'lucide-react';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { useContextStore, type MarketContext } from '@/stores/contextStore';

const LOCATION_OPTIONS: MarketContext['location_category'][] = [
    'Urban',
    'Suburban',
    'Rural',
];

export const LocationSection: FC = () => {
    const { context, updateContext } = useContextStore();

    return (
        <div className="space-y-3">
            <div className="flex items-center gap-2">
                <MapPin className="h-4 w-4 text-muted-foreground" />
                <h3 className="text-sm font-semibold">Location</h3>
            </div>
            <div className="space-y-2">
                <Label htmlFor="location-category" className="text-xs text-muted-foreground">
                    Area Type
                </Label>
                <Select
                    value={context.location_category}
                    onValueChange={(v) =>
                        updateContext({ location_category: v as MarketContext['location_category'] })
                    }
                >
                    <SelectTrigger id="location-category" className="h-9">
                        <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                        {LOCATION_OPTIONS.map((option) => (
                            <SelectItem key={option} value={option}>
                                {option}
                            </SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            </div>
        </div>
    );
};

