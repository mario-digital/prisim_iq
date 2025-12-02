import { MasterLayout } from '@/components/layout';

export default function EvidencePage() {
  return (
    <MasterLayout
      centerContent={
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center space-y-2">
            <h1 className="text-2xl font-semibold">Evidence & Methods</h1>
            <p className="text-muted-foreground">
              Model documentation and methodology details
            </p>
            <p className="text-xs text-muted-foreground">
              Content will be implemented in Story 4.6
            </p>
          </div>
        </div>
      }
    />
  );
}

