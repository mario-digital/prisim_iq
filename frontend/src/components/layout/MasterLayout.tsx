'use client';

import type { FC, ReactNode } from 'react';
import { Header } from './Header';
import { Footer } from './Footer';
import { LeftPanel } from './LeftPanel';
import { CenterPanel } from './CenterPanel';
import { RightPanel } from './RightPanel';

interface MasterLayoutProps {
  leftContent?: ReactNode;
  centerContent?: ReactNode;
  rightContent?: ReactNode;
}

export const MasterLayout: FC<MasterLayoutProps> = ({
  leftContent,
  centerContent,
  rightContent,
}) => {
  return (
    <div className="h-screen w-full overflow-hidden flex justify-center bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-200 via-slate-100 to-slate-50 dark:from-slate-800 dark:via-slate-900 dark:to-slate-950">
      <div className="h-full w-full max-w-[1920px] flex flex-col bg-background shadow-2xl shadow-black/10 dark:shadow-black/40 border-x border-border/30">
        <Header />
        <div className="flex-1 flex min-h-0">
          <LeftPanel>{leftContent}</LeftPanel>
          <CenterPanel>{centerContent}</CenterPanel>
          <RightPanel>{rightContent}</RightPanel>
        </div>
        <Footer />
      </div>
    </div>
  );
};

