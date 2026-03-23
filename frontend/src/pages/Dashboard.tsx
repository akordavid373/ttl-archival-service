import React, { useState } from 'react'
import { 
  Activity, 
  ShieldCheck, 
  Archive, 
  Database, 
  TrendingUp, 
  Clock, 
  AlertTriangle, 
  Trash2, 
  Download, 
  RefreshCw,
  ArrowUpRight
} from 'lucide-react'
import { StorageUsageChart } from '../components/charts/StorageUsageChart'
import { ArchiveTrendsChart } from '../components/charts/ArchiveTrendsChart'
import { cn } from '../lib/utils'

export function Dashboard() {
  const [isRefreshing, setIsRefreshing] = useState(false)

  const stats = [
    { label: 'Total Archives', value: '1,284', change: '+12%', icon: Archive, color: 'text-blue-500', bg: 'bg-blue-500/10' },
    { label: 'Active Policies', value: '24', change: '+2', icon: ShieldCheck, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
    { label: 'Blockchain Sync', value: '99.9%', change: 'Stable', icon: Database, color: 'text-purple-500', bg: 'bg-purple-500/10' },
    { label: 'Pending Deletions', value: '42', change: '-5', icon: Trash2, color: 'text-amber-500', bg: 'bg-amber-500/10' },
  ]

  const handleRefresh = () => {
    setIsRefreshing(true)
    setTimeout(() => setIsRefreshing(false), 2000)
  }

  const handleExport = () => {
    const csvContent = "data:text/csv;charset=utf-8," 
      + "Metric,Value,Change\n"
      + "Total Archives,1284,+12%\n"
      + "Active Policies,24,+2\n"
      + "Blockchain Sync,99.9%,Stable\n"
      + "Pending Deletions,42,-5";
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `ttl_audit_report_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <header className="flex items-center justify-between">
        <div className="flex flex-col gap-2">
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">Dashboard Overview</h2>
          <p className="text-muted-foreground flex items-center gap-2">
            <Activity className={cn("h-4 w-4 text-emerald-500", isRefreshing && "animate-pulse")} />
            {isRefreshing ? "Refreshing system metrics..." : "System is performing within optimal parameters."}
          </p>
        </div>
        <div className="flex gap-4">
          <button 
            onClick={handleRefresh}
            className="p-3 bg-secondary text-secondary-foreground rounded-2xl border border-border shadow-sm hover:bg-accent transition-colors group"
          >
            <RefreshCw className={cn("h-5 w-5", isRefreshing && "animate-spin")} />
          </button>
          <button 
            onClick={handleExport}
            className="flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground font-bold text-sm rounded-2xl shadow-lg shadow-primary/20 hover:scale-[1.02] transition-all group"
          >
            <Download className="h-5 w-5 group-hover:scale-110 transition-transform" />
            Export Audit Data
          </button>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, i) => (
          <div key={i} className="group p-6 rounded-3xl bg-card border border-border/50 hover:border-primary/20 hover:shadow-2xl hover:shadow-primary/5 transition-all duration-300">
            <div className="flex items-center justify-between mb-4">
              <div className={`p-3 rounded-2xl ${stat.bg} ${stat.color} group-hover:scale-110 transition-transform shadow-inner`}>
                {React.createElement(stat.icon, { className: "h-6 w-6" })}
              </div>
              <span className={`text-[10px] font-bold px-3 py-1 rounded-full ${stat.change.startsWith('+') ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20' : 'bg-muted text-muted-foreground border border-border/40'}`}>
                {stat.change}
              </span>
            </div>
            <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest leading-relaxed">{stat.label}</p>
            <p className="text-2xl font-bold tracking-tight mt-1">{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="p-8 rounded-3xl bg-card border border-border/50 shadow-sm relative group overflow-hidden">
          <div className="flex items-center justify-between mb-8">
            <h3 className="font-bold text-xl flex items-center gap-3">
              <Database className="h-6 w-6 text-primary" />
              Storage Usage
            </h3>
            <div className="flex gap-2">
              <button className="px-4 py-1.5 text-xs font-bold rounded-xl bg-primary text-primary-foreground">Monthly</button>
              <button className="px-4 py-1.5 text-xs font-bold rounded-xl hover:bg-accent transition-colors">Daily</button>
            </div>
          </div>
          <StorageUsageChart />
        </div>

        <div className="p-8 rounded-3xl bg-card border border-border/50 shadow-sm relative group overflow-hidden">
          <div className="flex items-center justify-between mb-8">
            <h3 className="font-bold text-xl flex items-center gap-3">
              <TrendingUp className="h-6 w-6 text-blue-500" />
              Archiving Trends
            </h3>
            <button className="text-xs font-bold text-primary flex items-center gap-1 hover:underline">
              View Detailed Analytics
              <ArrowUpRight className="h-3 w-3" />
            </button>
          </div>
          <ArchiveTrendsChart />
        </div>
      </div>

      <div className="p-8 rounded-3xl bg-card border border-border/50 shadow-sm relative overflow-hidden group">
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
  )
}
