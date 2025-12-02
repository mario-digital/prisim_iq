import { MasterLayout } from '@/components/layout';

export default function ExecutivePage() {
  return (
    <MasterLayout
      centerContent={
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center space-y-2">
            <h1 className="text-2xl font-semibold">Executive Summary</h1>
            <p className="text-muted-foreground">
              High-level pricing insights and recommendations
            </p>
            <p className="text-xs text-muted-foreground">
              Content will be implemented in Story 4.5
            </p>
          </div>
        </div>
      }
    />
  );
}

