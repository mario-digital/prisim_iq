import { Skeleton } from '@/components/ui/skeleton';

export default function Loading() {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      {/* Header skeleton */}
      <div className="h-14 border-b border-border bg-card px-4 flex items-center">
        <Skeleton className="h-8 w-32" />
      </div>

      {/* Main content skeleton */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left panel skeleton */}
        <aside className="w-1/4 min-w-[280px] border-r border-border p-4 space-y-4">
          <Skeleton className="h-6 w-3/4" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
        </aside>

        {/* Center panel skeleton */}
        <main className="flex-1 p-4 space-y-4">
          <Skeleton className="h-8 w-1/3" />
          <Skeleton className="h-64 w-full" />
        </main>

        {/* Right panel skeleton */}
        <aside className="w-1/4 min-w-[280px] border-l border-border p-4 space-y-4">
          <Skeleton className="h-6 w-3/4" />
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-32 w-full" />
        </aside>
      </div>

      {/* Footer skeleton */}
      <div className="h-10 border-t border-border bg-card px-4 flex items-center">
        <Skeleton className="h-4 w-48" />
      </div>
    </div>
  );
}

