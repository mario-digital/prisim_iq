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
    <div className="min-h-screen flex flex-col bg-background">
      <Header />
      <div className="flex-1 flex overflow-hidden">
        <LeftPanel>{leftContent}</LeftPanel>
        <CenterPanel>{centerContent}</CenterPanel>
        <RightPanel>{rightContent}</RightPanel>
      </div>
      <Footer />
    </div>
  );
};

