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
  Plane,
  Wrench,
  Clock,
  ShieldCheck,
  Factory,
  Warehouse,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface MappingRow {
  ride_sharing_concept: string;
  honeywell_equivalent: string;
  rationale: string;
  icon_left?: string;
  icon_right?: string;
}

export interface HoneywellMappingData {
  title: string;
  description: string;
  context: string;
  mappings: MappingRow[];
  compliance_notes: string[];
  business_value: string[];
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
  'Time of Day': Clock,
  'Real-time Demand': Users,
  'Service Provider Availability': Car,
  'Dynamic Price Multiplier': TrendingUp,
  'Customer Segmentation': Award,
  'Geographic Market': Globe,
  'Service Tier': Layers,
  'Demand Sensitivity': BarChart3,
  'Peak vs Off-Peak': Clock,
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
  'Peak/Off-Peak Scheduling': Clock,
  'Aftermarket Part Demand (AOG, Scheduled MRO)': Plane,
  'MRO Shop Capacity & Inventory': Warehouse,
  'Expedite Fees & Premium Pricing': DollarSign,
  'Airline Tier (Major, Regional, Charter)': Plane,
  'Regional Market (Americas, EMEA, APAC)': Globe,
  'Part Criticality (AOG, Rotable, Consumable)': Wrench,
  'Price Sensitivity by Part Category': BarChart3,
  'Scheduled vs Unscheduled Maintenance': Clock,
};

// Fallback data with Honeywell Aerospace context
export const fallbackMapping: HoneywellMappingData = {
  title: 'PrismIQ to Honeywell Aerospace Mapping',
  description:
    'How ride-sharing dynamic pricing translates to aerospace aftermarket pricing',
  context: `Honeywell Aerospace serves commercial airlines (Emirates, Delta, Southwest), regional carriers, 
and general aviation through their aftermarket business. Key customers include MRO (Maintenance, Repair, Overhaul) 
shops and airline operators directly. The catalog pricing system supports complex B2B relationships across 
Americas, EMEA, and APAC regions with channel partners in UAE, India, China, and more.`,
  mappings: [
    {
      ride_sharing_concept: 'Real-time Demand',
      honeywell_equivalent: 'Aftermarket Part Demand (AOG, Scheduled MRO)',
      rationale:
        'Just as ride-sharing tracks rider requests, Honeywell tracks Aircraft on Ground (AOG) urgent requests and scheduled MRO demand. AOG situations require immediate parts with premium pricing, similar to surge pricing during high demand.',
    },
    {
      ride_sharing_concept: 'Service Provider Availability',
      honeywell_equivalent: 'MRO Shop Capacity & Inventory',
      rationale:
        'Driver availability maps to MRO shop capacity and parts inventory levels. When inventory is low or MRO shops are at capacity, pricing reflects scarcity—just like fewer available drivers triggers surge pricing.',
    },
    {
      ride_sharing_concept: 'Dynamic Price Multiplier',
      honeywell_equivalent: 'Expedite Fees & Premium Pricing',
      rationale:
        'Surge pricing directly translates to expedite fees for rush orders and AOG situations. Airlines pay premium prices for immediate parts availability, similar to riders paying more during peak demand.',
    },
    {
      ride_sharing_concept: 'Customer Segmentation',
      honeywell_equivalent: 'Airline Tier (Major, Regional, Charter)',
      rationale:
        'Loyalty tiers map to airline customer segments. Major carriers like Emirates and Delta receive different pricing than regional operators or charter services, based on volume commitments and strategic partnerships.',
    },
    {
      ride_sharing_concept: 'Geographic Market',
      honeywell_equivalent: 'Regional Market (Americas, EMEA, APAC)',
      rationale:
        'Location-based pricing applies to regional markets. Channel partners in UAE, India, and China have region-specific pricing that accounts for local competition, logistics costs, and regulatory requirements.',
    },
    {
      ride_sharing_concept: 'Service Tier',
      honeywell_equivalent: 'Part Criticality (AOG, Rotable, Consumable)',
      rationale:
        'Vehicle types (Economy, Premium, Luxury) map to part criticality levels. AOG-critical parts command premium prices, while routine consumables have standard catalog pricing.',
    },
    {
      ride_sharing_concept: 'Demand Sensitivity',
      honeywell_equivalent: 'Price Sensitivity by Part Category',
      rationale:
        'Price elasticity varies by part category. Airlines are less price-sensitive for safety-critical components but more sensitive for commodity parts—similar to how riders accept surge for urgent trips.',
    },
    {
      ride_sharing_concept: 'Peak vs Off-Peak',
      honeywell_equivalent: 'Scheduled vs Unscheduled Maintenance',
      rationale:
        'Time-based pricing applies to maintenance scheduling. Unscheduled maintenance (like peak hours) commands premium pricing, while planned MRO events (off-peak) receive favorable rates.',
    },
  ],
  compliance_notes: [
    'All pricing algorithms comply with aerospace industry regulations (FAA, EASA)',
    'Model decisions are fully auditable for airline customer transparency',
    'Customer segmentation respects contractual obligations and volume agreements',
    'Dynamic pricing bounds prevent excessive price volatility for critical safety parts',
    'Channel partner pricing maintains margin consistency across regions',
  ],
  business_value: [
    'Optimize revenue across $2B+ aerospace aftermarket business',
    'Reduce AOG response time with intelligent pricing signals',
    'Improve inventory allocation through demand prediction',
    'Enhance channel partner relationships with fair, explainable pricing',
    'Support strategic accounts (Emirates, Delta, Southwest) with tailored pricing',
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

  useEffect(() => {
    const fetchMapping = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/v1/honeywell_mapping`);
        if (!response.ok) {
          throw new Error('Failed to fetch mapping');
        }
        const data = await response.json();
        // Transform API response to our expected format, but use our richer fallback content
        const apiMappings = Object.entries(data.mapping || {});
        if (apiMappings.length > 0) {
          // Merge API data with our detailed rationales
          setMapping({
            ...fallbackMapping,
            mappings: fallbackMapping.mappings.map((m, i) => ({
              ...m,
              // Override with API data if available
              ...(apiMappings[i] ? {
                ride_sharing_concept: apiMappings[i][0],
                honeywell_equivalent: String(apiMappings[i][1]),
              } : {}),
            })),
            compliance_notes: data.compliance_notes || fallbackMapping.compliance_notes,
          });
        } else {
          setMapping(fallbackMapping);
        }
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

  if (!mapping) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Context Section */}
      <div className="rounded-lg border border-primary/20 bg-primary/5 p-4">
        <h4 className="text-sm font-semibold mb-2 flex items-center gap-2">
          <Plane className="h-4 w-4 text-primary" />
          Honeywell Aerospace Context
        </h4>
        <p className="text-sm text-muted-foreground leading-relaxed">
          {mapping.context}
        </p>
      </div>

      {/* Mapping Table */}
      <div className="rounded-xl border border-border overflow-hidden bg-card shadow-sm">
        <table className="w-full">
          <thead>
            <tr className="bg-gradient-to-r from-muted/80 to-muted/40">
              <th className="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground w-[25%]">
                <div className="flex items-center gap-2">
                  <Car className="h-3.5 w-3.5" />
                  Ride-Sharing Concept
                </div>
              </th>
              <th className="px-2 py-3.5 text-center w-[5%]">
                <ArrowRight className="h-4 w-4 mx-auto text-primary" />
              </th>
              <th className="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground w-[28%]">
                <div className="flex items-center gap-2">
                  <Factory className="h-3.5 w-3.5" />
                  Honeywell Aerospace
                </div>
              </th>
              <th className="px-4 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground w-[42%]">
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
                      <div className="h-8 w-8 rounded-lg bg-cyan-500/10 flex items-center justify-center flex-shrink-0">
                        <RideSharingIcon className="h-4 w-4 text-cyan-500" />
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
                          className="max-w-[350px]"
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

      {/* Business Value Section */}
      {mapping.business_value && mapping.business_value.length > 0 && (
        <div className="rounded-lg border border-green-500/20 bg-green-500/5 p-4">
          <h4 className="text-sm font-semibold mb-2 flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-green-600 dark:text-green-400" />
            Business Value for Honeywell
          </h4>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {mapping.business_value.map((value, i) => (
              <li
                key={i}
                className="text-xs text-muted-foreground flex items-start gap-2"
              >
                <span className="text-green-600 dark:text-green-400 mt-0.5">●</span>
                {value}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Compliance Notes */}
      {mapping.compliance_notes && mapping.compliance_notes.length > 0 && (
        <div className="rounded-lg border border-border/50 bg-muted/30 p-4">
          <h4 className="text-sm font-semibold mb-2 flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-primary" />
            Compliance & Governance
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
