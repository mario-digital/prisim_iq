'use client';

import { useEffect, type FC } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, FileBarChart, FlaskConical } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useLayoutStore, type ActiveTab } from '@/stores/layoutStore';

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
 * Uses explicit matching to support extensibility.
 * Defaults to 'workspace' with dev warning for unmatched routes.
 */
function getActiveTabFromPath(pathname: string): ActiveTab {
  // Find matching tab by checking if pathname starts with tab href
  const matchedTab = tabs.find((tab) => pathname.startsWith(tab.href));

  if (matchedTab) {
    return matchedTab.id;
  }

  // Warn in development if route doesn't match any tab (except root redirect)
  if (process.env.NODE_ENV === 'development' && pathname !== '/') {
    console.warn(
      `[TabNavigation] No tab matches pathname "${pathname}". Defaulting to "workspace". ` +
        `Add a new tab entry if this route should be highlighted.`
    );
  }

  return 'workspace';
}

export const TabNavigation: FC = () => {
  const pathname = usePathname();
  const setActiveTab = useLayoutStore((state) => state.setActiveTab);

  const activeTab = getActiveTabFromPath(pathname);

  // Sync URL pathname with Zustand store
  useEffect(() => {
    setActiveTab(activeTab);
  }, [activeTab, setActiveTab]);

  return (
    <nav className="border-b border-border bg-card">
      <div className="flex h-12 items-center gap-1 px-4">
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
      </div>
    </nav>
  );
};

