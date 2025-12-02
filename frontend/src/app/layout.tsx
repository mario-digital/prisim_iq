import type { Metadata } from 'next';
import { TabNavigation } from '@/components/layout';
import './globals.css';

export const metadata: Metadata = {
  title: 'PrismIQ - Dynamic Pricing Copilot',
  description: 'AI-powered dynamic pricing assistant with explainable recommendations',
  keywords: ['pricing', 'AI', 'machine learning', 'dynamic pricing', 'copilot'],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-background font-sans antialiased">
        <TabNavigation />
        {children}
      </body>
    </html>
  );
}
