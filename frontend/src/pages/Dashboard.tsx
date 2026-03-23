import React from 'react'
import { Activity, ShieldCheck, Archive, Database, TrendingUp, Clock, AlertTriangle } from 'lucide-react'

export function Dashboard() {
  const stats = [
    { label: 'Total Archives', value: '1,284', change: '+12%', icon: Archive, color: 'text-blue-500', bg: 'bg-blue-500/10' },
    { label: 'Active Policies', value: '24', change: '+2', icon: ShieldCheck, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
    { label: 'Blockchain Sync', value: '99.9%', change: 'Stable', icon: Database, color: 'text-purple-500', bg: 'bg-purple-500/10' },
    { label: 'Pending Deletions', value: '42', change: '-5', icon: Trash2, color: 'text-amber-500', bg: 'bg-amber-500/10' },
  ]

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <header className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">Dashboard Overview</h2>
        <p className="text-muted-foreground flex items-center gap-2">
          <Activity className="h-4 w-4 text-emerald-500" />
          System is performing within optimal parameters.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, i) => (
          <div key={i} className="group p-6 rounded-2xl bg-card border border-border/50 hover:border-primary/20 hover:shadow-2xl hover:shadow-primary/5 transition-all duration-300">
            <div className="flex items-center justify-between mb-4">
              <div className={`p-2 rounded-xl ${stat.bg} ${stat.color} group-hover:scale-110 transition-transform`}>
                {React.createElement(stat.icon, { className: "h-5 w-5" })}
              </div>
              <span className={`text-[10px] font-bold px-2 py-1 rounded-full ${stat.change.startsWith('+') ? 'bg-emerald-500/10 text-emerald-500' : 'bg-muted text-muted-foreground'}`}>
                {stat.change}
              </span>
            </div>
            <p className="text-sm font-medium text-muted-foreground">{stat.label}</p>
            <p className="text-2xl font-bold tracking-tight">{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 p-8 rounded-2xl bg-card border border-border/50 shadow-sm overflow-hidden relative group">
          <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full -translate-y-1/2 translate-x-1/2 blur-3xl group-hover:bg-primary/10 transition-colors"></div>
          <div className="flex items-center justify-between mb-8 relative z-10">
            <h3 className="font-bold text-lg flex items-center gap-3">
              <TrendingUp className="h-5 w-5 text-primary" />
              Archival Activity
            </h3>
            <div className="flex gap-2">
              <button className="px-3 py-1 text-xs font-semibold rounded-full bg-primary text-primary-foreground shadow-lg shadow-primary/20">7d</button>
              <button className="px-3 py-1 text-xs font-semibold rounded-full hover:bg-accent transition-colors">30d</button>
            </div>
          </div>
          <div className="h-[280px] w-full bg-accent/20 rounded-xl flex items-center justify-center border border-dashed border-border/60 relative z-10">
             <div className="flex flex-col items-center gap-2 group-hover:scale-105 transition-transform duration-500">
               <Database className="h-10 w-10 text-muted-foreground/30 animate-pulse" />
               <p className="text-sm text-muted-foreground/60 font-medium">Visualization Engine Ready</p>
               <div className="flex gap-1 h-3 mt-2">
                 {[40, 60, 80, 50, 90, 70, 85].map((h, i) => (
                   <div key={i} className="w-1 bg-primary/30 rounded-full h-full transform transition-all hover:bg-primary" style={{ height: `${h}%` }}></div>
                 ))}
               </div>
             </div>
          </div>
        </div>

        <div className="p-8 rounded-2xl bg-card border border-border/50 shadow-sm relative overflow-hidden group">
          <h3 className="font-bold text-lg mb-6 flex items-center gap-3 relative z-10">
            <Clock className="h-5 w-5 text-amber-500" />
            Recently Expired
          </h3>
          <div className="space-y-4 relative z-10">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="flex items-center gap-4 p-3 rounded-xl hover:bg-accent/50 transition-colors cursor-pointer border border-transparent hover:border-border/40">
                <div className="w-10 h-10 rounded-lg bg-accent flex items-center justify-center text-amber-500 shrink-0">
                  <AlertTriangle className="h-5 w-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold truncate group-hover:text-primary transition-colors">user_logs_2024_03_2{i}.sql</p>
                  <p className="text-[10px] text-muted-foreground flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    2 hours ago · 14.2 MB
                  </p>
                </div>
              </div>
            ))}
          </div>
          <button className="w-full mt-8 py-2.5 text-xs font-bold text-primary hover:text-primary/80 transition-colors relative z-10 hover:underline">
            Manage All Expired Records
          </button>
        </div>
      </div>
    </div>
  )
}

// Fixed import Trash2
import { Trash2 } from 'lucide-react'
