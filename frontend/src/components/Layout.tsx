import React, { useState } from 'react';
import { NavLink, useLocation, Link } from 'react-router-dom';
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
  User,
  ChevronRight,
  Menu,
  X,
  CreditCard,
  Settings2,
  HelpCircle,
  Bell,
  LogOut
} from 'lucide-react'
import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import { cn } from '../lib/utils'
import { Breadcrumbs } from './Breadcrumbs'
import { NotificationBell } from './notifications'
import OfflineStatus from './OfflineStatus'
import InstallPWA from './InstallPWA'
import { LanguageSwitcher } from './LanguageSwitcher'

interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const { t } = useTranslation()
  const { isRTL } = useLanguage()

  const navItems = [
    { name: 'Dashboard', icon: LayoutDashboard, path: '/' },
    { name: 'Policies', icon: ShieldCheck, path: '/policies' },
    { name: 'Archives', icon: Archive, path: '/archives' },
    { name: 'Blockchain', icon: Database, path: '/blockchain' },
    { name: 'Settings', icon: Settings, path: '/settings' },
    { name: 'Demo', icon: Settings2, path: '/demo' },
  ]

  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar */}
      <aside className={`fixed ${isRTL ? 'right-0' : 'left-0'} top-0 h-64 w-64 bg-card/80 backdrop-blur-xl border-r border-border/40 z-40 lg:h-screen`}>
        <div className="flex flex-col h-full">
          <div className="p-6 flex items-center gap-3">
            <div className="w-10 h-10 bg-primary/10 rounded-2xl flex items-center justify-center border border-primary/20 shadow-inner group">
              <Archive className="text-primary h-6 w-6 group-hover:scale-110 transition-transform" />
            </div>
            <div>
              <h1 className="font-bold text-lg tracking-tight bg-gradient-to-br from-foreground to-foreground/60 bg-clip-text text-transparent">TTL-Archival</h1>
              <p className="text-[10px] text-muted-foreground uppercase tracking-widest font-bold opacity-60">Service</p>
            </div>
          </div>

          <nav className="flex-1 px-4 py-8 space-y-1.5 mt-2">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path
              return (
                <Link
                  key={item.name}
                  to={item.path}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={cn(
                    "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 group relative overflow-hidden",
                    isActive 
                      ? "bg-primary text-primary-foreground shadow-2xl shadow-primary/20 transform scale-[1.02]" 
                      : "text-muted-foreground hover:bg-accent/50 hover:text-accent-foreground"
                  )}
                >
                  <item.icon className={cn("h-5 w-5 transition-transform duration-300", isActive ? "scale-110" : "group-hover:scale-110")} />
                  <span className="font-semibold text-sm">{item.name}</span>
                  {isActive ? (
                    <div className="ml-auto flex items-center">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary-foreground animate-pulse mr-2" />
                      <ChevronRight className="h-4 w-4 opacity-50" />
                    </div>
                  ) : (
                    <ChevronRight className="ml-auto h-4 w-4 opacity-0 group-hover:opacity-40 -translate-x-2 group-hover:translate-x-0 transition-all" />
                  )}
                </Link>
              )
            })}
          </nav>

          <div className="p-6 border-t border-border/30 mt-auto bg-accent/5">
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
        </div>
      </aside>

      {/* Main Content */}
      <div className={isRTL ? 'lg:pr-64 min-h-screen' : 'lg:pl-64 min-h-screen'}>
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

        {/* Page Content & Breadcrumbs */}
        <main className="flex-1 overflow-y-auto bg-dot-pattern scroll-smooth">
          <div className="p-6 lg:p-12 max-w-7xl mx-auto">
            {/* Breadcrumbs Integration */}
            <Breadcrumbs />
            
            <div className="animate-in fade-in slide-in-from-bottom-6 duration-700">
              {children}
            </div>
          </div>
        </main>
      </div>

      {/* Decorative Blur Overlays for premium feel */}
      <div className="fixed top-0 left-0 w-96 h-96 bg-primary/10 rounded-full blur-[120px] -z-10 pointer-events-none opacity-50 translate-x-1/2 -translate-y-1/2" />
      <div className="fixed bottom-0 right-0 w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-[150px] -z-10 pointer-events-none opacity-30 -translate-x-1/4 translate-y-1/4" />
      
      <OfflineStatus />
      <InstallPWA />
    </div>
  );
}
