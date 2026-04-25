import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  ShieldCheck, 
  Archive, 
  Database, 
  Settings, 
  LogOut,
  Search,
  User,
  ChevronRight,
  Menu,
  X,
  CreditCard,
  Settings2,
  HelpCircle,
} from 'lucide-react'
import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import { cn } from '../lib/utils'
import { Breadcrumbs } from './Breadcrumbs'
import { NotificationBell } from './notifications'

interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  const navItems = [
    { name: 'Dashboard', icon: LayoutDashboard, path: '/' },
    { name: 'Policies', icon: ShieldCheck, path: '/policies' },
    { name: 'Archives', icon: Archive, path: '/archives' },
    { name: 'Blockchain', icon: Database, path: '/blockchain' },
    { name: 'Settings', icon: Settings, path: '/settings' },
  ]

  const SidebarContent = () => (
    <div className="flex flex-col h-full bg-card/80 backdrop-blur-xl border-r border-border/40">
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
        <button className="flex items-center justify-between w-full px-4 py-3 text-sm font-bold text-muted-foreground hover:text-destructive hover:bg-destructive/5 rounded-xl transition-all group">
          <div className="flex items-center gap-3">
            <LogOut className="h-5 w-5 group-hover:-translate-x-1 transition-transform" />
            <span>Sign Out</span>
          </div>
          <div className="h-1.5 w-1.5 rounded-full bg-muted-foreground/30" />
        </button>
      </div>
    </div>
  )

  return (
    <div className="flex h-screen bg-background overflow-hidden relative selection:bg-primary/20">
      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex w-72 flex-col shrink-0">
        <SidebarContent />
      </aside>

      {/* Mobile Sidebar Overlay */}
      {isMobileMenuOpen && (
        <div 
          className="lg:hidden fixed inset-0 z-50 bg-background/60 backdrop-blur-md animate-in fade-in duration-300"
          onClick={() => setIsMobileMenuOpen(false)}
        >
          <div 
            className="w-72 h-full animate-in slide-in-from-left duration-500 ease-out"
            onClick={e => e.stopPropagation()}
          >
            <div className="flex justify-end p-4 absolute right-0 top-0 lg:hidden">
               <button 
                 onClick={() => setIsMobileMenuOpen(false)}
                 className="p-2 bg-accent rounded-full text-muted-foreground hover:text-foreground transition-colors"
               >
                 <X className="h-5 w-5" />
               </button>
            </div>
            <SidebarContent />
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden min-w-0">
        {/* Header */}
        <header className="h-20 border-b border-border/40 bg-card/40 backdrop-blur-xl flex items-center justify-between px-4 lg:px-10 sticky top-0 z-40">
          <div className="flex items-center gap-4 flex-1">
            {/* Hamburger Menu Toggle */}
            <button 
              onClick={() => setIsMobileMenuOpen(true)}
              className="lg:hidden p-2.5 bg-accent/50 rounded-xl text-muted-foreground hover:text-foreground hover:bg-accent transition-all ring-1 ring-border/50"
            >
              <Menu className="h-5 w-5" />
            </button>

            <div className="hidden sm:flex items-center gap-4 w-full max-w-md relative group ml-2 lg:ml-0">
              <Search className="absolute left-3.5 h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors pointer-events-none" />
              <input 
                placeholder="Global search catalog..."
                className="bg-accent/30 border border-transparent focus:border-primary/30 focus:bg-accent/60 transition-all rounded-2xl pl-11 pr-4 py-2.5 text-xs w-full outline-none font-medium placeholder:text-muted-foreground/60 tracking-tight"
              />
              <kbd className="absolute right-3 top-1/2 -translate-y-1/2 px-1.5 py-0.5 rounded border border-border bg-card text-[10px] text-muted-foreground font-mono hidden md:block">
                ⌘K
              </kbd>
            </div>
          </div>

          <div className="flex items-center gap-2 lg:gap-6 ml-4">
            <NotificationBell />
            
            <div className="h-10 w-px bg-border/40 mx-1 hidden sm:block" />

            {/* Profile Dropdown */}
            <DropdownMenu.Root>
              <DropdownMenu.Trigger asChild>
                <div className="flex items-center gap-3 pl-2 group cursor-pointer hover:bg-accent/40 px-3 py-2 rounded-2xl transition-all border border-transparent hover:border-border/40 ring-offset-background focus-visible:outline-none">
                  <div className="text-right hidden sm:block">
                    <p className="text-sm font-bold leading-none mb-1">David Akoro</p>
                    <p className="text-[10px] text-muted-foreground font-bold uppercase tracking-wider opacity-60">Admin</p>
                  </div>
                  <div className="relative">
                    <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-primary/20 to-indigo-500/20 flex items-center justify-center border border-primary/20 shadow-inner group-hover:scale-105 transition-transform overflow-hidden ring-2 ring-transparent group-hover:ring-primary/20">
                      <User className="h-5 w-5 text-primary" />
                    </div>
                    <div className="absolute bottom-0 right-0 w-3 h-3 bg-emerald-500 rounded-full border-2 border-card ring-1 ring-emerald-500/20" />
                  </div>
                </div>
              </DropdownMenu.Trigger>

              <DropdownMenu.Portal>
                <DropdownMenu.Content 
                  className="min-w-[240px] bg-card/95 backdrop-blur-xl rounded-2xl p-2 shadow-2xl border border-border/40 animate-in fade-in zoom-in-95 data-[side=top]:slide-in-from-bottom-2 data-[side=bottom]:slide-in-from-top-2 duration-200 z-[100]"
                  sideOffset={8}
                  align="end"
                >
                  <div className="px-3 py-4 mb-2 border-b border-border/30">
                    <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-1">Signed in as</p>
                    <p className="font-bold text-sm truncate">david@example.com</p>
                  </div>
                  
                  <DropdownMenu.Item className="flex items-center gap-3 px-3 py-2.5 text-sm font-semibold rounded-xl cursor-pointer outline-none hover:bg-primary hover:text-primary-foreground focus:bg-primary focus:text-primary-foreground transition-colors group">
                    <User className="h-4 w-4 opacity-70 group-hover:opacity-100" />
                    Profile
                    <DropdownMenu.Shortcut className="ml-auto text-xs opacity-50">⌘P</DropdownMenu.Shortcut>
                  </DropdownMenu.Item>

                  <DropdownMenu.Item className="flex items-center gap-3 px-3 py-2.5 text-sm font-semibold rounded-xl cursor-pointer outline-none hover:bg-primary hover:text-primary-foreground focus:bg-primary focus:text-primary-foreground transition-colors group">
                    <CreditCard className="h-4 w-4 opacity-70 group-hover:opacity-100" />
                    Subscription
                  </DropdownMenu.Item>

                  <DropdownMenu.Item className="flex items-center gap-3 px-3 py-2.5 text-sm font-semibold rounded-xl cursor-pointer outline-none hover:bg-primary hover:text-primary-foreground focus:bg-primary focus:text-primary-foreground transition-colors group">
                    <Settings2 className="h-4 w-4 opacity-70 group-hover:opacity-100" />
                    Workspace Settings
                  </DropdownMenu.Item>

                  <DropdownMenu.Separator className="h-px bg-border/40 my-2 mx-1" />
                  
                  <DropdownMenu.Item className="flex items-center gap-3 px-3 py-2.5 text-sm font-semibold rounded-xl cursor-pointer outline-none hover:bg-accent transition-colors group">
                    <HelpCircle className="h-4 w-4 opacity-70" />
                    Support Docs
                  </DropdownMenu.Item>
                  
                  <DropdownMenu.Item className="flex items-center gap-3 px-3 py-2.5 text-sm font-semibold rounded-xl cursor-pointer outline-none hover:bg-destructive/10 hover:text-destructive transition-colors group mt-1">
                    <LogOut className="h-4 w-4 opacity-70" />
                    Sign Out
                  </DropdownMenu.Item>
                </DropdownMenu.Content>
              </DropdownMenu.Portal>
            </DropdownMenu.Root>
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
    </div>
  )
}
