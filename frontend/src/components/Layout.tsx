import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  ShieldCheck, 
  Archive, 
  Database, 
  Settings, 
  LogOut,
  Bell,
  Search,
  User,
  ChevronRight
} from 'lucide-react'
import { cn } from '../lib/utils'

interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  const location = useLocation()

  const navItems = [
    { name: 'Dashboard', icon: LayoutDashboard, path: '/' },
    { name: 'Policies', icon: ShieldCheck, path: '/policies' },
    { name: 'Archives', icon: Archive, path: '/archives' },
    { name: 'Blockchain', icon: Database, path: '/blockchain' },
    { name: 'Settings', icon: Settings, path: '/settings' },
  ]

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border bg-card/50 backdrop-blur-md flex flex-col">
        <div className="p-6 flex items-center gap-3">
          <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center border border-primary/20">
            <Archive className="text-primary h-6 w-6" />
          </div>
          <div>
            <h1 className="font-bold text-lg tracking-tight">TTL-Archival</h1>
            <p className="text-[10px] text-muted-foreground uppercase tracking-widest font-semibold">Service</p>
          </div>
        </div>

        <nav className="flex-1 px-4 py-6 space-y-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.name}
                to={item.path}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group relative",
                  isActive 
                    ? "bg-primary text-primary-foreground shadow-lg shadow-primary/20" 
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                )}
              >
                <item.icon className="h-5 w-5" />
                <span className="font-medium text-sm">{item.name}</span>
                {isActive && (
                  <div className="ml-auto">
                    <ChevronRight className="h-4 w-4 opacity-50" />
                  </div>
                )}
              </Link>
            )
          })}
        </nav>

        <div className="p-4 border-t border-border mt-auto">
          <button className="flex items-center gap-3 w-full px-3 py-2 text-sm text-muted-foreground hover:text-destructive hover:bg-destructive/5 rounded-lg transition-colors">
            <LogOut className="h-5 w-5" />
            <span className="font-medium">Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Header */}
        <header className="h-16 border-b border-border bg-card/30 backdrop-blur-md flex items-center justify-between px-8 sticky top-0 z-40">
          <div className="flex items-center gap-4 w-96 relative group">
            <Search className="absolute left-3 h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
            <input 
              placeholder="Search policies, archives..."
              className="bg-accent/50 border border-transparent focus:border-primary/30 focus:bg-accent/80 transition-all rounded-full pl-10 pr-4 py-1.5 text-xs w-full outline-none"
            />
          </div>

          <div className="flex items-center gap-4">
            <button className="relative p-2 text-muted-foreground hover:text-foreground transition-colors group">
              <Bell className="h-5 w-5" />
              <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-primary rounded-full ring-2 ring-background group-hover:scale-110 transition-transform"></span>
            </button>
            <div className="h-8 w-px bg-border mx-2"></div>
            <div className="flex items-center gap-3 pl-2 group cursor-pointer hover:bg-accent/30 py-1.5 pr-2 rounded-full transition-colors">
              <div className="text-right">
                <p className="text-xs font-semibold">David Akoro</p>
                <p className="text-[10px] text-muted-foreground">Administrator</p>
              </div>
              <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center border border-primary/20 shadow-inner group-hover:shadow-primary/10">
                <User className="h-4 w-4 text-primary" />
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto bg-dot-pattern scroll-smooth">
          <div className="p-10 max-w-7xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
