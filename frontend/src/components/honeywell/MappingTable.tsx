'use client';

import { useEffect, useState, type FC } from 'react';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  Users,
  Car,
  TrendingUp,
  Award,
  MapPin,
  Truck,
  BarChart3,
  Package,
  DollarSign,
  Building2,
  Globe,
  Layers,
  ArrowRight,
  HelpCircle,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface MappingRow {
  ride_sharing_concept: string;
  honeywell_equivalent: string;
  rationale: string;
}

export interface HoneywellMappingData {
  title: string;
  description: string;
  mappings: MappingRow[];
  compliance_notes: string[];
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Icons for ride-sharing concepts
const rideSharingIcons: Record<string, typeof Users> = {
  'Number of Riders (Demand)': Users,
  'Number of Drivers (Supply)': Car,
  'Surge Pricing': TrendingUp,
  'Customer Loyalty Tier': Award,
  'Location Category': MapPin,
  'Vehicle Type': Truck,
  'Price Elasticity': BarChart3,
  'Time of Day': Globe,
};

// Icons for Honeywell equivalents
const honeywellIcons: Record<string, typeof Building2> = {
  'Product Demand Forecast': BarChart3,
  'Inventory/Capacity Levels': Package,
  'Dynamic Pricing / Premium Pricing': DollarSign,
  'Customer Segmentation': Building2,
  'Market/Region Segmentation': Globe,
  'Product Tier / SKU': Layers,
  'Demand Elasticity Modeling': TrendingUp,
  'Peak/Off-Peak Scheduling': Globe,
};

// Fallback data for when API is unavailable
const fallbackMapping: HoneywellMappingData = {
  title: 'Ride-Sharing to Honeywell Enterprise Mapping',
  description:
    'How dynamic pricing concepts translate to enterprise applications',
  mappings: [
    {
      ride_sharing_concept: 'Number of Riders (Demand)',
      honeywell_equivalent: 'Product Demand Forecast',
      rationale:
        'Both represent customer demand signals that drive pricing decisions. In manufacturing, this translates to order backlog and market demand indicators.',
    },
    {
      ride_sharing_concept: 'Number of Drivers (Supply)',
      honeywell_equivalent: 'Inventory/Capacity Levels',
      rationale:
        'Available supply constrains pricing flexibility. Factory capacity, raw material inventory, and workforce availability mirror driver availability.',
    },
    {
      ride_sharing_concept: 'Surge Pricing',
      honeywell_equivalent: 'Dynamic Pricing / Premium Pricing',
      rationale:
        'Price adjustment based on supply-demand imbalance. Enterprise applications include expedited shipping fees, rush order premiums, and peak season pricing.',
    },
    {
      ride_sharing_concept: 'Customer Loyalty Tier',
      honeywell_equivalent: 'Customer Segmentation',
      rationale:
        'Different customer segments have different price sensitivity. Key accounts, long-term contracts, and strategic partners receive differentiated pricing.',
    },
    {
      ride_sharing_concept: 'Location Category',
      honeywell_equivalent: 'Market/Region Segmentation',
      rationale:
        'Geographic factors affect pricing due to competition, logistics costs, and regional regulations. Manufacturing considers shipping zones and local market conditions.',
    },
    {
      ride_sharing_concept: 'Vehicle Type',
      honeywell_equivalent: 'Product Tier / SKU',
      rationale:
        'Different product tiers command different prices. Standard vs. premium products, basic vs. enhanced service levels mirror economy vs. luxury vehicles.',
    },
    {
      ride_sharing_concept: 'Price Elasticity',
      honeywell_equivalent: 'Demand Elasticity Modeling',
      rationale:
        'Understanding how price changes affect demand volume. Critical for optimizing revenue across product lines and market segments.',
    },
    {
      ride_sharing_concept: 'Time of Day',
      honeywell_equivalent: 'Peak/Off-Peak Scheduling',
      rationale:
        'Temporal demand patterns influence pricing. Manufacturing considers shift schedules, delivery windows, and seasonal cycles.',
    },
  ],
  compliance_notes: [
    'All pricing algorithms comply with enterprise governance requirements',
    'Model decisions are fully auditable and explainable',
    'Customer segmentation respects anti-discrimination guidelines',
    'Dynamic pricing bounds prevent excessive price volatility',
  ],
};

function TableSkeleton() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-12 w-full" />
      {[...Array(6)].map((_, i) => (
        <Skeleton key={i} className="h-20 w-full" />
      ))}
    </div>
  );
}

export const MappingTable: FC = () => {
  const [mapping, setMapping] = useState<HoneywellMappingData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMapping = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/v1/honeywell_mapping`);
        if (!response.ok) {
          throw new Error('Failed to fetch mapping');
        }
        const data = await response.json();
        // Transform API response to our expected format
        setMapping({
          title: 'Ride-Sharing to Honeywell Enterprise Mapping',
          description:
            'How dynamic pricing concepts translate to enterprise applications',
          mappings: Object.entries(data.mapping || {}).map(([key, value]) => ({
            ride_sharing_concept: key,
            honeywell_equivalent: String(value),
            rationale:
              fallbackMapping.mappings.find(
                (m) => m.ride_sharing_concept === key
              )?.rationale || 'Enterprise application of the concept.',
          })),
          compliance_notes: data.compliance_notes || fallbackMapping.compliance_notes,
        });
      } catch {
        console.warn('Using fallback mapping data');
        setMapping(fallbackMapping);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMapping();
  }, []);

  if (isLoading) {
    return <TableSkeleton />;
  }

  if (error) {
    return (
      <div className="text-center py-8 text-destructive">
        <p>{error}</p>
      </div>
    );
  }

  if (!mapping) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Mapping Table */}
      <div className="rounded-xl border border-border overflow-hidden bg-card shadow-sm">
        <table className="w-full">
          <thead>
            <tr className="bg-gradient-to-r from-muted/80 to-muted/40">
              <th className="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground w-[28%]">
                Ride-Sharing Concept
              </th>
              <th className="px-2 py-3.5 text-center w-[6%]">
                <ArrowRight className="h-4 w-4 mx-auto text-primary" />
              </th>
              <th className="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground w-[28%]">
                Honeywell Equivalent
              </th>
              <th className="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground w-[38%]">
                Business Rationale
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/50">
            {mapping.mappings.map((row, i) => {
              const RideSharingIcon =
                rideSharingIcons[row.ride_sharing_concept] || Users;
              const HoneywellIcon =
                honeywellIcons[row.honeywell_equivalent] || Building2;

              return (
                <tr
                  key={i}
                  className={cn(
                    'hover:bg-primary/5 transition-colors duration-150',
                    i % 2 === 0 ? 'bg-transparent' : 'bg-muted/20'
                  )}
                >
                  <td className="px-4 py-4">
                    <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded-lg bg-blue-500/10 flex items-center justify-center flex-shrink-0">
                        <RideSharingIcon className="h-4 w-4 text-blue-500" />
                      </div>
                      <span className="font-medium text-sm">
                        {row.ride_sharing_concept}
                      </span>
                    </div>
                  </td>
                  <td className="px-2 py-4 text-center">
                    <ArrowRight className="h-4 w-4 mx-auto text-muted-foreground" />
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded-lg bg-orange-500/10 flex items-center justify-center flex-shrink-0">
                        <HoneywellIcon className="h-4 w-4 text-orange-500" />
                      </div>
                      <span className="font-medium text-sm">
                        {row.honeywell_equivalent}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <TooltipProvider delayDuration={200}>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <div className="flex items-start gap-2 cursor-help">
                            <p className="text-sm text-muted-foreground line-clamp-2">
                              {row.rationale}
                            </p>
                            <HelpCircle className="h-3 w-3 text-muted-foreground/50 flex-shrink-0 mt-1" />
                          </div>
                        </TooltipTrigger>
                        <TooltipContent
                          side="left"
                          className="max-w-[300px]"
                        >
                          <p className="text-xs">{row.rationale}</p>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Compliance Notes */}
      {mapping.compliance_notes && mapping.compliance_notes.length > 0 && (
        <div className="rounded-lg border border-border/50 bg-muted/30 p-4">
          <h4 className="text-sm font-semibold mb-2 flex items-center gap-2">
            <Award className="h-4 w-4 text-primary" />
            Compliance & Governance Notes
          </h4>
          <ul className="space-y-1">
            {mapping.compliance_notes.map((note, i) => (
              <li
                key={i}
                className="text-xs text-muted-foreground flex items-start gap-2"
              >
                <span className="text-primary mt-0.5">✓</span>
                {note}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

// Export mapping data for PDF generation
export { fallbackMapping };

