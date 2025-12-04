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
    <div className="h-screen w-full bg-muted/30 overflow-hidden flex justify-center">
      <div className="h-full w-full max-w-[1920px] flex flex-col bg-background shadow-xl">
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

