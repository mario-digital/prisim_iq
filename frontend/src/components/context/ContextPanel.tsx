'use client';

import type { FC } from 'react';
import { LocationSection } from './LocationSection';
import { TimeSection } from './TimeSection';
import { SupplyDemandSection } from './SupplyDemandSection';
import { CustomerSection } from './CustomerSection';
import { VehicleSection } from './VehicleSection';
import { ExternalFactorsSection } from './ExternalFactorsSection';
import { ScenarioManager } from './ScenarioManager';
import { ApplyChangesButton } from './ApplyChangesButton';
import { Separator } from '@/components/ui/separator';

export const ContextPanel: FC = () => {
    return (
        <div className="flex flex-col gap-4 p-4 h-full overflow-y-auto">
            {/* Market Context Header */}
            <div className="flex items-center gap-2">
                <h2 className="text-sm font-semibold text-foreground">Market Context</h2>
            </div>

            {/* Core Context Sections */}
            <LocationSection />
            <Separator />
            <TimeSection />
            <Separator />
            <SupplyDemandSection />
            <Separator />
            <CustomerSection />
            <Separator />
            <VehicleSection />

            <Separator className="my-2" />

            {/* External Factors from n8n */}
            <ExternalFactorsSection />

            <Separator className="my-2" />

            {/* Apply Changes */}
            <ApplyChangesButton />

            <Separator className="my-2" />

            {/* Scenario Management */}
            <ScenarioManager />
        </div>
    );
};
