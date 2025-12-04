'use client';

import { useEffect, type FC } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, FileBarChart, FlaskConical } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useLayoutStore, type ActiveTab } from '@/stores/layoutStore';
import { Brand } from './Brand';
import { PipelineStatus } from './PipelineStatus';
import { SystemStatus } from './SystemStatus';
import { HoneywellToggle } from './HoneywellToggle';

interface Tab {
  id: ActiveTab;
  label: string;
  href: string;
  icon: typeof LayoutDashboard;
}

const tabs: Tab[] = [
  {
    id: 'workspace',
    label: 'Analyst Workspace',
    href: '/workspace',
    icon: LayoutDashboard,
  },
  {
    id: 'executive',
    label: 'Executive Summary',
    href: '/executive',
    icon: FileBarChart,
  },
  {
    id: 'evidence',
    label: 'Evidence & Methods',
    href: '/evidence',
    icon: FlaskConical,
  },
];

/**
 * Determine active tab from pathname.
 */
function getActiveTabFromPath(pathname: string): ActiveTab {
  const matchedTab = tabs.find((tab) => pathname.startsWith(tab.href));
  return matchedTab?.id ?? 'workspace';
}

/**
 * Main header component for PrismIQ application.
 * Per PRD Master Layout Structure, header contains two rows:
 * - Top row: Brand, Pipeline Status, System Status
 * - Bottom row: Tab Navigation, Honeywell Toggle
 */
export const Header: FC = () => {
  const pathname = usePathname();
  const setActiveTab = useLayoutStore((state) => state.setActiveTab);
  const activeTab = getActiveTabFromPath(pathname);

  // Sync URL pathname with Zustand store
  useEffect(() => {
    setActiveTab(activeTab);
  }, [activeTab, setActiveTab]);

  return (
    <header className="border-b border-border bg-card">
      {/* Top row: Brand, Pipeline Status, System Status */}
      <div className="h-14 px-4 flex items-center justify-between">
        {/* Left: Brand */}
        <Brand />

        {/* Center: Pipeline Status */}
        <div className="flex items-center">
          <PipelineStatus />
        </div>

        {/* Right: System Status */}
        <SystemStatus />
      </div>

      {/* Bottom row: Tab Navigation + Honeywell Toggle */}
      <div className="h-12 px-4 flex items-center justify-between border-t border-border/50">
        {/* Tabs */}
        <nav className="flex items-center gap-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;

            return (
              <Link
                key={tab.id}
                href={tab.href}
                className={cn(
                  'flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-colors',
                  isActive
                    ? 'bg-primary/10 text-primary'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                )}
              >
                <Icon className="h-4 w-4" />
                {tab.label}
              </Link>
            );
          })}
        </nav>

        {/* Honeywell Toggle at end of tab row */}
        <HoneywellToggle />
      </div>
    </header>
  );
};
