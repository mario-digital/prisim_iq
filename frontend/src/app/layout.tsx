import type { Metadata } from 'next';
import { ToastContainer } from '@/components/ui/toast';
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
    // suppressHydrationWarning on html: prevents mismatch warnings from browser extensions
    // that modify the DOM (e.g., dark mode, translation, accessibility tools)
    <html lang="en" dir="ltr" suppressHydrationWarning>
      <body className="min-h-screen bg-background font-sans antialiased" suppressHydrationWarning>
        {children}
        <ToastContainer />
      </body>
    </html>
  );
}
