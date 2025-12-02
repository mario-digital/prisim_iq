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

export const TabNavigation: FC = () => {
  const pathname = usePathname();
  const setActiveTab = useLayoutStore((state) => state.setActiveTab);

  const getActiveTab = (): ActiveTab => {
    if (pathname.startsWith('/executive')) return 'executive';
    if (pathname.startsWith('/evidence')) return 'evidence';
    return 'workspace';
  };

  const activeTab = getActiveTab();

  // Sync URL pathname with Zustand store (fixes ARCH-001)
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

