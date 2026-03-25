import React from 'react'
import { 
  Activity, 
  ShieldCheck, 
  Archive, 
  Database, 
  TrendingUp, 
  Clock, 
  Download, 
  RefreshCw,
  ArrowUpRight,
  AlertCircle
} from 'lucide-react'
import { StorageUsageChart } from '../components/charts/StorageUsageChart'
import { ArchiveTrendsChart } from '../components/charts/ArchiveTrendsChart'
import { cn } from '../utils/cn'
import { useDashboardStats } from '../hooks/useDashboardStats'
import { MetricCard } from '../components/Dashboard/MetricCard'
import { RecentActivity } from '../components/Dashboard/RecentActivity'

export function Dashboard() {
  const { 
    stats, 
    recentArchives, 
    isLoading, 
    isRefreshing, 
    error, 
    refresh 
  } = useDashboardStats()

  const handleExport = () => {
    if (!stats) return
    const csvContent = "data:text/csv;charset=utf-8," 
      + "Metric,Value\n"
      + `Total Archives,${stats.total_records}\n`
      + `Active Policies,${stats.active_policies}\n`
      + `Storage Usage,${stats.storage_usage_formatted}\n`
      + `Blockchain Status,${stats.blockchain_status}\n`
      + `Verification Rate,${stats.verification_rate}%`;
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `ttl_audit_report_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-center p-8 bg-destructive/5 rounded-3xl border border-destructive/20 animate-in zoom-in-95">
        <AlertCircle className="h-12 w-12 text-destructive mb-4" />
        <h3 className="text-xl font-bold mb-2">Failed to load dashboard data</h3>
        <p className="text-muted-foreground mb-6 max-w-md">{error}</p>
        <button 
          onClick={() => refresh()}
          className="flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground font-bold rounded-2xl shadow-lg hover:scale-105 transition-all"
        >
          <RefreshCw className="h-5 w-5" />
          Retry Connection
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <header className="flex items-center justify-between">
        <div className="flex flex-col gap-2">
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">Dashboard Overview</h2>
          <p className="text-muted-foreground flex items-center gap-2">
            <Activity className={cn("h-4 w-4 text-emerald-500", (isLoading || isRefreshing) && "animate-pulse")} />
            {isLoading || isRefreshing ? "Refreshing system metrics..." : "System is performing within optimal parameters."}
          </p>
        </div>
        <div className="flex gap-4">
          <button 
            disabled={isLoading || isRefreshing}
            onClick={() => refresh()}
            className="p-3 bg-secondary text-secondary-foreground rounded-2xl border border-border shadow-sm hover:bg-accent transition-colors group disabled:opacity-50"
          >
            <RefreshCw className={cn("h-5 w-5", (isLoading || isRefreshing) && "animate-spin")} />
          </button>
          <button 
            disabled={!stats}
            onClick={handleExport}
            className="flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground font-bold text-sm rounded-2xl shadow-lg shadow-primary/20 hover:scale-[1.02] transition-all group disabled:opacity-50"
          >
            <Download className="h-5 w-5 group-hover:scale-110 transition-transform" />
            Export Audit Data
          </button>
        </div>
      </header>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {isLoading && !stats ? (
          Array(4).fill(0).map((_, i) => (
            <div key={i} className="h-[148px] rounded-3xl bg-accent/20 animate-pulse border border-border/50" />
          ))
        ) : (
          <>
            <MetricCard 
              label="Total Archives" 
              value={stats?.total_records || '0'} 
              change="+12%" // Typically this would also come from API stats if possible
              icon={Archive} 
              color="text-blue-500" 
              bg="bg-blue-500/10" 
            />
            <MetricCard 
              label="Active Policies" 
              value={stats?.active_policies || '0'} 
              change="+2" 
              icon={ShieldCheck} 
              color="text-emerald-500" 
              bg="bg-emerald-500/10" 
            />
            <MetricCard 
              label="Storage Usage" 
              value={stats?.storage_usage_formatted || '0 MB'} 
              change="+520 MB" 
              icon={Database} 
              color="text-purple-500" 
              bg="bg-purple-500/10" 
            />
            <MetricCard 
              label="Blockchain Status" 
              value={stats?.blockchain_status || 'Checking...'} 
              change={stats?.verification_rate ? `${stats.verification_rate}%` : 'Stable'} 
              icon={Database} 
              color="text-amber-500" 
              bg="bg-amber-500/10" 
            />
          </>
        )}
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

      {/* Recent Activity Section */}
      <div className="p-8 rounded-3xl bg-card border border-border/50 shadow-sm relative overflow-hidden group mb-8">
        <h3 className="font-bold text-lg mb-6 flex items-center gap-3 relative z-10">
          <Clock className="h-5 w-5 text-amber-500" />
          Recently Expired
        </h3>
        <RecentActivity 
          activities={recentArchives} 
          loading={isLoading && recentArchives.length === 0} 
        />
        <button className="w-full mt-8 py-2.5 text-xs font-bold text-primary hover:text-primary/80 transition-colors relative z-10 hover:underline">
          Manage All Expired Records
        </button>
      </div>
    </div>
  )
}
