import { MasterLayout } from '@/components/layout';

export default function WorkspacePage() {
  return (
    <MasterLayout
      centerContent={
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center space-y-2">
            <h1 className="text-2xl font-semibold">Analyst Workspace</h1>
            <p className="text-muted-foreground">
              Chat interface and pricing analysis tools
            </p>
            <p className="text-xs text-muted-foreground">
              Content will be implemented in Stories 4.2, 4.3, 4.4
            </p>
          </div>
        </div>
      }
    />
  );
}

