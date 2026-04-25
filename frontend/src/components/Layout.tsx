import React from 'react';
import { NavLink } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { useLanguage } from '../context/LanguageContext';
import { 
  LayoutDashboard, 
  ShieldCheck, 
  Archive, 
  Database, 
  Settings, 
  Search,
  Bell,
  User
} from 'lucide-react';
import { SEO } from './common/SEO';
import { ShortcutModal } from './shortcuts/ShortcutModal';
import { LanguageSwitcher } from './LanguageSwitcher';

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/policies', icon: ShieldCheck, label: 'Policies' },
  { path: '/archives', icon: Archive, label: 'Archives' },
  { path: '/blockchain', icon: Database, label: 'Blockchain' },
  { path: '/settings', icon: Settings, label: 'Settings' },
];

export const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { t } = useTranslation()
  const { isRTL } = useLanguage()

  const navItems = [
    { path: '/', icon: LayoutDashboard, label: t('navigation.dashboard') },
    { path: '/policies', icon: ShieldCheck, label: t('navigation.policies') },
    { path: '/archives', icon: Archive, label: t('navigation.archives') },
    { path: '/blockchain', icon: Database, label: t('navigation.blockchain') },
    { path: '/settings', icon: Settings, label: t('navigation.settings') },
  ];

  return (
    <div className={`min-h-screen bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100 transition-colors duration-300 ${isRTL ? 'rtl' : 'ltr'}`}>
      <SEO />
      <ShortcutModal />
      
      {/* Sidebar */}
      <aside className={`fixed ${isRTL ? 'right-0' : 'left-0'} top-0 bottom-0 w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 z-40 hidden lg:block`}>
        <div className="p-6">
          <div className="flex items-center gap-3 mb-10">
            <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-primary/20">
              T
            </div>
            <h1 className="text-xl font-bold tracking-tight">TTL Archival</h1>
          </div>

          <nav className="space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) => `
                  flex items-center gap-3 px-4 py-3 rounded-xl transition-all group
                  ${isActive 
                    ? 'bg-primary/10 text-primary font-semibold' 
                    : 'text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100'}
                `}
              >
                <item.icon className="w-5 h-5" />
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>

        <div className={`absolute bottom-0 ${isRTL ? 'right-0' : 'left-0'} left-0 right-0 p-6 border-t border-gray-100 dark:border-gray-800">
          <div className="space-y-4">
            <LanguageSwitcher />
            <div className="flex items-center gap-3 p-2 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors cursor-pointer group">
              <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-primary to-accent flex items-center justify-center text-white font-medium">
                JD
              </div>
              <div className="flex-1 overflow-hidden">
                <p className="text-sm font-semibold truncate">John Doe</p>
                <p className="text-xs text-gray-500 truncate">Premium Plan</p>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className={isRTL ? 'lg:pr-64 min-h-screen' : 'lg:pl-64 min-h-screen'}>
        {/* Header */}
        <header className="h-20 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-800 sticky top-0 z-30 flex items-center justify-between px-8">
          <div className="relative max-w-md w-full">
            <Search className={`absolute ${isRTL ? 'right-3' : 'left-3'} top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400`} />
            <input 
              type="text" 
              placeholder={t('archives.searchArchives') + '... (Ctrl+K)'}
              className={`w-full bg-gray-100 dark:bg-gray-800 border-none rounded-xl py-2 ${isRTL ? 'pr-10 pl-4' : 'pl-10 pr-4'} text-sm focus:ring-2 focus:ring-primary transition-all`}
            />
          </div>

          <div className="flex items-center gap-4">
            <button className="p-2.5 rounded-xl bg-gray-100 dark:bg-gray-800 text-gray-500 hover:text-primary transition-all relative">
              <Bell className="w-5 h-5" />
              <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white dark:border-gray-800"></span>
            </button>
            <button className="hidden sm:flex items-center gap-2 bg-primary text-white px-5 py-2.5 rounded-xl font-medium hover:opacity-90 transition-opacity shadow-lg shadow-primary/20">
              <Archive className="w-4 h-4" />
              {t('common.add')} {t('archives.title')}
            </button>
          </div>
        </header>

        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="p-8"
        >
          {children}
        </motion.div>
      </main>
    </div>
  );
};
