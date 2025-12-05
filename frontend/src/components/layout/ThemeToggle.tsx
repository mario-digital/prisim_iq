'use client';

import type { FC } from 'react';
import { useTheme } from 'next-themes';
import { Moon, Sun } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { useEffect, useState } from 'react';

/**
 * Theme toggle button with smooth animation.
 * Switches between light and dark modes.
 */
export const ThemeToggle: FC = () => {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Avoid hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <Button
        variant="ghost"
        size="sm"
        className="h-8 w-8 p-0"
        disabled
      >
        <Sun className="h-4 w-4" />
      </Button>
    );
  }

  const isDark = theme === 'dark';

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={() => setTheme(isDark ? 'light' : 'dark')}
      className={cn(
        'relative h-8 w-8 p-0 overflow-hidden transition-all duration-300',
        isDark
          ? 'text-amber-400 hover:bg-amber-400/10'
          : 'text-cyan-600 hover:bg-cyan-600/10'
      )}
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      {/* Sun icon */}
      <Sun
        className={cn(
          'h-4 w-4 absolute transition-all duration-300 ease-in-out',
          isDark
            ? 'rotate-0 scale-100 opacity-100'
            : 'rotate-90 scale-0 opacity-0'
        )}
      />
      {/* Moon icon */}
      <Moon
        className={cn(
          'h-4 w-4 absolute transition-all duration-300 ease-in-out',
          isDark
            ? '-rotate-90 scale-0 opacity-0'
            : 'rotate-0 scale-100 opacity-100'
        )}
      />
    </Button>
  );
};

