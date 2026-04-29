import React, { createContext, useContext, useEffect, useState } from 'react';

export type ThemeMode = 'light' | 'dark' | 'system';
export type ThemeColor = 'blue' | 'purple' | 'green' | 'orange' | 'custom';
export type Typography = 'inter' | 'roboto' | 'outfit';

interface ThemeConfig {
  mode: ThemeMode;
  primaryColor: string;
  accentColor: string;
  typography: Typography;
  spacing: 'compact' | 'normal' | 'relaxed';
}

interface ThemeContextType {
  theme: ThemeConfig;
  setTheme: (theme: Partial<ThemeConfig>) => void;
  exportTheme: () => string;
  importTheme: (config: string) => void;
  isDark: boolean;
}

const defaultTheme: ThemeConfig = {
  mode: 'system',
  primaryColor: '#3b82f6',
  accentColor: '#8b5cf6',
  typography: 'outfit',
  spacing: 'normal',
};

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = useState<ThemeConfig>(() => {
    const saved = localStorage.getItem('theme-config');
    return saved ? JSON.parse(saved) : defaultTheme;
  });

  const [isDark, setIsDark] = useState(false);

  const setTheme = (newTheme: Partial<ThemeConfig>) => {
    setThemeState((prev) => {
      const updated = { ...prev, ...newTheme };
      localStorage.setItem('theme-config', JSON.stringify(updated));
      return updated;
    });
  };

  const exportTheme = () => JSON.stringify(theme, null, 2);

  const importTheme = (config: string) => {
    try {
      const parsed = JSON.parse(config);
      setTheme(parsed);
    } catch (e) {
      console.error('Invalid theme config', e);
    }
  };

  // Handle system theme preference changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleChange = (e: MediaQueryListEvent) => {
      if (theme.mode === 'system') {
        setIsDark(e.matches);
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme.mode]);

  useEffect(() => {
    const root = window.document.documentElement;
    
    // Determine if dark mode should be active
    let shouldBeDark = false;
    if (theme.mode === 'dark') {
      shouldBeDark = true;
    } else if (theme.mode === 'system') {
      shouldBeDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    }

    setIsDark(shouldBeDark);

    // Apply dark mode class with smooth transition
    if (shouldBeDark) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }

    // Colors
    root.style.setProperty('--primary', theme.primaryColor);
    root.style.setProperty('--accent', theme.accentColor);
    
    // Typography
    root.style.setProperty('--font-family', theme.typography === 'outfit' ? "'Outfit', sans-serif" : theme.typography === 'inter' ? "'Inter', sans-serif" : "'Roboto', sans-serif");

    // Spacing
    const spacingMultiplier = theme.spacing === 'compact' ? '0.8' : theme.spacing === 'relaxed' ? '1.2' : '1';
    root.style.setProperty('--spacing-scale', spacingMultiplier);

  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme, exportTheme, importTheme, isDark }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within ThemeProvider');
  return context;
};
