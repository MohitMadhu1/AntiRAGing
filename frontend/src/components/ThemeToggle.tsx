'use client';

import * as React from 'react';
import { useTheme } from 'next-themes';
import { Sun, Moon } from 'lucide-react';
import SketchButton from './SketchButton';

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);

  // Ensure component is mounted to avoid hydration mismatch
  React.useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <SketchButton>
        <div style={{ width: 24, height: 24 }} />
      </SketchButton>
    );
  }

  const toggleTheme = () => {
    if (theme === 'dark') {
      setTheme('light');
    } else {
      setTheme('dark');
    }
  };

  return (
    <SketchButton onClick={toggleTheme}>
      {theme === 'dark' ? <Sun size={24} /> : <Moon size={24} />}
    </SketchButton>
  );
}
