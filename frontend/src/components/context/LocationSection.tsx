'use client';

import type { FC, ReactNode } from 'react';
import { MapPin, Building2, Home, Trees } from 'lucide-react';
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

interface LocationOption {
    value: MarketContext['location_category'];
    label: string;
    description: string;
    icon: ReactNode;
    badgeColor: string;
}

const LOCATION_OPTIONS: LocationOption[] = [
    {
        value: 'Urban',
        label: 'Urban',
        description: 'City center',
        icon: <Building2 className="h-4 w-4" />,
        badgeColor: 'bg-blue-500/10 text-blue-600 border-blue-500/20',
    },
    {
        value: 'Suburban',
        label: 'Suburban',
        description: 'Residential area',
        icon: <Home className="h-4 w-4" />,
        badgeColor: 'bg-teal-500/10 text-teal-600 border-teal-500/20',
    },
    {
        value: 'Rural',
        label: 'Rural',
        description: 'Countryside',
        icon: <Trees className="h-4 w-4" />,
        badgeColor: 'bg-green-500/10 text-green-600 border-green-500/20',
    },
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
                        <SelectValue>
                            {(() => {
                                const selected = LOCATION_OPTIONS.find(o => o.value === context.location_category);
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
                        {LOCATION_OPTIONS.map((option) => (
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
        </div>
    );
};
