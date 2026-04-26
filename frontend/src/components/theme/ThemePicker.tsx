import React from 'react';
import { motion } from 'framer-motion';
import { useTheme, ThemeMode, ThemeColor, Typography } from '../../context/ThemeContext';
import { Sun, Moon, Monitor, Type, Layout, Download, Upload } from 'lucide-react';

export const ThemePicker: React.FC = () => {
  const { theme, setTheme, exportTheme, importTheme } = useTheme();

  const handleExport = () => {
    const config = exportTheme();
    const blob = new Blob([config], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'ttl-theme-config.json';
    a.click();
  };

  const handleImport = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const content = event.target?.result as string;
        importTheme(content);
      };
      reader.readAsText(file);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6 bg-white dark:bg-gray-900 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-800"
    >
      <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white flex items-center gap-2">
        <Layout className="w-6 h-6 text-primary" />
        Appearance Settings
      </h2>

      {/* Mode Selection */}
      <div className="mb-8">
        <label className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3 block">Theme Mode</label>
        <div className="grid grid-cols-3 gap-3">
          {(['light', 'dark', 'system'] as ThemeMode[]).map((mode) => (
            <button
              key={mode}
              onClick={() => setTheme({ mode })}
              className={`flex flex-col items-center justify-center p-3 rounded-xl border-2 transition-all ${
                theme.mode === mode 
                  ? 'border-primary bg-primary/5 text-primary' 
                  : 'border-gray-100 dark:border-gray-800 hover:border-gray-300 dark:hover:border-gray-700'
              }`}
            >
              {mode === 'light' && <Sun className="w-5 h-5 mb-2" />}
              {mode === 'dark' && <Moon className="w-5 h-5 mb-2" />}
              {mode === 'system' && <Monitor className="w-5 h-5 mb-2" />}
              <span className="text-xs capitalize">{mode}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Primary Color */}
      <div className="mb-8">
        <label className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3 block">Brand Color</label>
        <div className="flex gap-3">
          {['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'].map((color) => (
            <button
              key={color}
              onClick={() => setTheme({ primaryColor: color })}
              className={`w-10 h-10 rounded-full transition-transform hover:scale-110 ${
                theme.primaryColor === color ? 'ring-2 ring-offset-2 ring-primary scale-110' : ''
              }`}
              style={{ backgroundColor: color }}
            />
          ))}
          <input 
            type="color" 
            value={theme.primaryColor}
            onChange={(e) => setTheme({ primaryColor: e.target.value })}
            className="w-10 h-10 rounded-full cursor-pointer bg-transparent border-0 p-0"
          />
        </div>
      </div>

      {/* Typography */}
      <div className="mb-8">
        <label className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3 block">Typography</label>
        <div className="grid grid-cols-3 gap-3">
          {(['inter', 'roboto', 'outfit'] as Typography[]).map((font) => (
            <button
              key={font}
              onClick={() => setTheme({ typography: font })}
              className={`p-3 rounded-xl border-2 transition-all flex items-center gap-2 ${
                theme.typography === font 
                  ? 'border-primary bg-primary/5 text-primary' 
                  : 'border-gray-100 dark:border-gray-800 hover:border-gray-300 dark:hover:border-gray-700'
              }`}
            >
              <Type className="w-4 h-4" />
              <span className="text-xs capitalize">{font}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Export / Import */}
      <div className="flex gap-4 pt-4 border-t border-gray-100 dark:border-gray-800">
        <button
          onClick={handleExport}
          className="flex-1 flex items-center justify-center gap-2 p-2.5 rounded-xl bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
        >
          <Download className="w-4 h-4" />
          Export
        </button>
        <label className="flex-1 flex items-center justify-center gap-2 p-2.5 rounded-xl bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors cursor-pointer">
          <Upload className="w-4 h-4" />
          Import
          <input type="file" accept=".json" onChange={handleImport} className="hidden" />
        </label>
      </div>
    </motion.div>
  );
};
