import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useShortcuts } from '../../context/ShortcutContext';
import { X, Keyboard } from 'lucide-react';

export const ShortcutModal: React.FC = () => {
  const { shortcuts, isHelpOpen, setHelpOpen } = useShortcuts();

  if (!isHelpOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="w-full max-w-2xl bg-white dark:bg-gray-900 rounded-2xl shadow-2xl overflow-hidden"
        >
          <div className="flex items-center justify-between p-6 border-b border-gray-100 dark:border-gray-800">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <Keyboard className="w-6 h-6 text-primary" />
              Keyboard Shortcuts
            </h3>
            <button 
              onClick={() => setHelpOpen(false)}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="p-6 max-h-[60vh] overflow-y-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {['Navigation', 'Actions', 'View'].map((category) => (
                <div key={category}>
                  <h4 className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-4">
                    {category}
                  </h4>
                  <div className="space-y-4">
                    {shortcuts
                      .filter((s) => s.category === category)
                      .map((shortcut) => (
                        <div key={shortcut.key} className="flex items-center justify-between">
                          <span className="text-sm text-gray-600 dark:text-gray-400">{shortcut.description}</span>
                          <div className="flex gap-1">
                            {shortcut.key.split(' ').map((part, i) => (
                              <React.Fragment key={i}>
                                {i > 0 && <span className="text-gray-400 text-xs self-center">then</span>}
                                <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded text-xs font-mono text-gray-900 dark:text-gray-200 shadow-sm">
                                  {part}
                                </kbd>
                              </React.Fragment>
                            ))}
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="p-6 bg-gray-50 dark:bg-gray-800/50 border-t border-gray-100 dark:border-gray-800 text-center">
            <p className="text-xs text-gray-500">
              Press <kbd className="px-1.5 py-0.5 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded">?</kbd> anytime to toggle this menu
            </p>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
