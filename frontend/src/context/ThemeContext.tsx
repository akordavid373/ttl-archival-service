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
}

const defaultTheme: ThemeConfig = {
  mode: 'dark',
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

  useEffect(() => {
    const root = window.document.documentElement;
    
    // Mode
    if (theme.mode === 'dark' || (theme.mode === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
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
    <ThemeContext.Provider value={{ theme, setTheme, exportTheme, importTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within ThemeProvider');
  return context;
};
