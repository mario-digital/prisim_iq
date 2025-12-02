import type { Metadata } from 'next';
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
    <html lang="en">
      <body className="min-h-screen bg-background font-sans antialiased">
        {children}
      </body>
    </html>
  );
}

