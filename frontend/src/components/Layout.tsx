import React, { useState, useEffect, useRef } from 'react';
import { NavLink, useLocation, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { useLanguage } from '../context/LanguageContext';
import { useTheme } from '../context/ThemeContext';
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
import { ThemeToggle } from './theme/ThemeToggle'

interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [isDesktop, setIsDesktop] = useState(window.innerWidth >= 1024)
  const menuRef = useRef<HTMLDivElement>(null)
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

  // Handle responsive behavior
  useEffect(() => {
    const handleResize = () => {
      const isNowDesktop = window.innerWidth >= 1024
      setIsDesktop(isNowDesktop)
      // Close mobile menu when resizing to desktop
      if (isNowDesktop && isMobileMenuOpen) {
        setIsMobileMenuOpen(false)
      }
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [isMobileMenuOpen])

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Close menu on Escape key
      if (e.key === 'Escape' && isMobileMenuOpen) {
        setIsMobileMenuOpen(false)
      }
      // Open menu on Alt+M
      if (e.altKey && e.key === 'm') {
        e.preventDefault()
        setIsMobileMenuOpen(!isMobileMenuOpen)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isMobileMenuOpen])

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setIsMobileMenuOpen(false)
      }
    }

    if (isMobileMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isMobileMenuOpen])

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile Menu Button */}
      <div className="lg:hidden fixed top-0 left-0 right-0 h-20 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-800 z-50 flex items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center border border-primary/20">
            <Archive className="text-primary h-5 w-5" />
          </div>
          <h1 className="font-bold text-sm tracking-tight">TTL-Archival</h1>
        </div>
        <button
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          aria-label="Toggle menu"
          aria-expanded={isMobileMenuOpen}
        >
          {isMobileMenuOpen ? (
            <X className="w-6 h-6" />
          ) : (
            <Menu className="w-6 h-6" />
          )}
        </button>
      </div>

      {/* Sidebar - Desktop */}
      <aside className={`hidden lg:flex fixed ${isRTL ? 'right-0' : 'left-0'} top-0 h-screen w-64 bg-card/80 backdrop-blur-xl border-r border-border/40 z-40 flex-col`}>
        <div className="p-6 flex items-center gap-3">
          <div className="w-10 h-10 bg-primary/10 rounded-2xl flex items-center justify-center border border-primary/20 shadow-inner group">
            <Archive className="text-primary h-6 w-6 group-hover:scale-110 transition-transform" />
          </div>
          <div>
            <h1 className="font-bold text-lg tracking-tight bg-gradient-to-br from-foreground to-foreground/60 bg-clip-text text-transparent">TTL-Archival</h1>
            <p className="text-[10px] text-muted-foreground uppercase tracking-widest font-bold opacity-60">Service</p>
          </div>
        </div>

        <nav className="flex-1 px-4 py-8 space-y-1.5 mt-2 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.name}
                to={item.path}
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
            <div className="flex items-center gap-2">
              <LanguageSwitcher />
              <ThemeToggle />
            </div>
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

      {/* Mobile Menu - Animated Slide-in */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <>
            {/* Overlay */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="fixed inset-0 bg-black/50 z-30 lg:hidden"
              onClick={() => setIsMobileMenuOpen(false)}
            />
            
            {/* Mobile Menu */}
            <motion.div
              ref={menuRef}
              initial={{ x: isRTL ? 300 : -300, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: isRTL ? 300 : -300, opacity: 0 }}
              transition={{ type: 'spring', damping: 20, stiffness: 300 }}
              className={`fixed top-20 ${isRTL ? 'right-0' : 'left-0'} bottom-0 w-64 bg-card/95 backdrop-blur-xl border-r border-border/40 z-40 flex flex-col overflow-y-auto`}
            >
              <nav className="flex-1 px-4 py-6 space-y-1.5">
                {navItems.map((item, index) => {
                  const isActive = location.pathname === item.path
                  return (
                    <motion.div
                      key={item.name}
                      initial={{ opacity: 0, x: isRTL ? 20 : -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <Link
                        to={item.path}
                        onClick={() => setIsMobileMenuOpen(false)}
                        className={cn(
                          "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 group relative overflow-hidden",
                          isActive 
                            ? "bg-primary text-primary-foreground shadow-2xl shadow-primary/20" 
                            : "text-muted-foreground hover:bg-accent/50 hover:text-accent-foreground"
                        )}
                      >
                        <item.icon className={cn("h-5 w-5 transition-transform duration-300", isActive ? "scale-110" : "group-hover:scale-110")} />
                        <span className="font-semibold text-sm">{item.name}</span>
                        {isActive && (
                          <ChevronRight className="ml-auto h-4 w-4" />
                        )}
                      </Link>
                    </motion.div>
                  )
                })}
              </nav>

              <div className="p-6 border-t border-border/30 bg-accent/5">
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <LanguageSwitcher />
                    <ThemeToggle />
                  </div>
                  <div className="flex items-center gap-3 p-2 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors cursor-pointer">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-primary to-accent flex items-center justify-center text-white font-medium text-sm">
                      JD
                    </div>
                    <div className="flex-1 overflow-hidden">
                      <p className="text-sm font-semibold truncate">John Doe</p>
                      <p className="text-xs text-gray-500 truncate">Premium Plan</p>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className={`${isDesktop ? (isRTL ? 'lg:pr-64' : 'lg:pl-64') : ''} min-h-screen lg:pt-0 pt-20`}>
        {/* Header */}
        <header className="h-20 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-800 sticky top-0 z-30 flex items-center justify-between px-4 lg:px-8">
          <div className="relative max-w-md w-full hidden sm:block">
            <Search className={`absolute ${isRTL ? 'right-3' : 'left-3'} top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400`} />
            <input 
              type="text" 
              placeholder={t('archives.searchArchives') + '... (Ctrl+K)'}
              className={`w-full bg-gray-100 dark:bg-gray-800 border-none rounded-xl py-2 ${isRTL ? 'pr-10 pl-4' : 'pl-10 pr-4'} text-sm focus:ring-2 focus:ring-primary transition-all`}
            />
          </div>

          <div className="flex items-center gap-2 lg:gap-4 ml-auto">
            <button className="p-2.5 rounded-xl bg-gray-100 dark:bg-gray-800 text-gray-500 hover:text-primary transition-all relative" aria-label="Notifications">
              <Bell className="w-5 h-5" />
              <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white dark:border-gray-800"></span>
            </button>
            <button className="hidden sm:flex items-center gap-2 bg-primary text-white px-5 py-2.5 rounded-xl font-medium hover:opacity-90 transition-opacity shadow-lg shadow-primary/20">
              <Archive className="w-4 h-4" />
              <span className="hidden md:inline">{t('common.add')} {t('archives.title')}</span>
              <span className="md:hidden">{t('common.add')}</span>
            </button>
          </div>
        </header>

        {/* Page Content & Breadcrumbs */}
        <main className="flex-1 overflow-y-auto bg-dot-pattern scroll-smooth">
          <div className="p-4 lg:p-12 max-w-7xl mx-auto">
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
