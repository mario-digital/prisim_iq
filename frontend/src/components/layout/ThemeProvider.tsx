'use client';

import { ThemeProvider as NextThemesProvider } from 'next-themes';
import type { FC, ReactNode } from 'react';

interface ThemeProviderProps {
  children: ReactNode;
}

/**
 * Theme provider wrapper for next-themes.
 * Enables dark/light mode toggling across the application.
 */
export const ThemeProvider: FC<ThemeProviderProps> = ({ children }) => {
  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="dark"
      enableSystem={false}
      disableTransitionOnChange={false}
    >
      {children}
    </NextThemesProvider>
  );
};

