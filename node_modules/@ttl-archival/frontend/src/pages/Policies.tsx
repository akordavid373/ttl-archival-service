import React from 'react'
import { 
  ShieldCheck, 
  Clock, 
  Database, 
  Plus, 
  MoreVertical, 
  TrendingUp,
  Search,
  ArrowUpRight
} from 'lucide-react'
import { PolicyMetricsChart } from '../components/charts/PolicyMetricsChart'

export function Policies() {
  const policies = [
    { name: 'User Data TTL', ttl: '30 Days', status: 'Active', storage: 'S3 Standard', archives: 124, color: 'text-primary' },
    { name: 'System Logs', ttl: '7 Days', status: 'Active', storage: 'Glacier Deep', archives: 850, color: 'text-amber-500' },
    { name: 'Marketing Assets', ttl: '365 Days', status: 'Inactive', storage: 'S3 Standard-IA', archives: 54, color: 'text-rose-500' },
  ]

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <header className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div className="space-y-2">
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">Archival Policies</h2>
          <p className="text-muted-foreground">Manage rules, TTL settings, and automated archival workflows.</p>
        </div>
        <button className="flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground font-bold text-sm rounded-2xl shadow-lg shadow-primary/20 hover:scale-[1.02] transition-all duration-300 group whitespace-nowrap">
          <Plus className="h-5 w-5 group-hover:rotate-90 transition-transform duration-300" />
          Create New Policy
        </button>
      </header>

      <div className="flex flex-col md:flex-row items-stretch md:items-center gap-4 bg-card/40 backdrop-blur-md p-4 rounded-3xl border border-border/50">
        <div className="flex-1 relative group">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
          <input className="w-full pl-10 pr-4 py-2 bg-transparent text-sm focus:outline-none placeholder:text-muted-foreground" placeholder="Search policies..." />
        </div>
        <div className="hidden md:block h-6 w-px bg-border"></div>
        <select className="bg-transparent text-xs font-semibold px-4 py-2 md:py-0 cursor-pointer focus:outline-none border border-border/50 md:border-none rounded-xl">
          <option>All Status</option>
          <option>Active</option>
          <option>Inactive</option>
        </select>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1 p-8 rounded-3xl bg-card border border-border/50 shadow-sm relative group overflow-hidden">
          <div className="flex items-center justify-between mb-8">
            <h3 className="font-bold text-lg flex items-center gap-3">
              <TrendingUp className="h-5 w-5 text-indigo-500" />
              Effectiveness
            </h3>
            <span className="text-[10px] font-bold px-2 py-1 bg-indigo-500/10 text-indigo-500 rounded-full border border-indigo-500/20">Live Audit</span>
          </div>
          <PolicyMetricsChart />
          <div className="mt-8 space-y-3">
             <div className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground font-medium">Auto-Archival Rate</span>
                <span className="font-bold">94%</span>
             </div>
             <div className="w-full bg-accent/30 h-1.5 rounded-full overflow-hidden">
                <div className="w-[94%] bg-indigo-500 h-full rounded-full transition-all duration-1000"></div>
             </div>
          </div>
        </div>

        <div className="lg:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-6">
          {policies.map((p, i) => (
            <div key={i} className="p-6 rounded-3xl bg-card border border-border/50 hover:border-primary/20 hover:shadow-2xl hover:shadow-primary/5 transition-all duration-300 group cursor-pointer relative overflow-hidden flex flex-col">
              <div className="absolute top-0 right-0 p-4">
                <MoreVertical className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
              <div className="flex items-center gap-4 mb-6">
                <div className={`p-3 rounded-2xl bg-accent ${p.color} bg-opacity-10 group-hover:scale-110 transition-transform shadow-inner`}>
                  <ShieldCheck className="h-6 w-6" />
                </div>
                <div>
                  <h4 className="font-bold text-sm tracking-tight">{p.name}</h4>
                  <div className={`px-2 py-0.5 rounded-full text-[10px] font-bold mt-1 inline-block ${p.status === 'Active' ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20' : 'bg-muted text-muted-foreground border border-border/40'}`}>
                    {p.status}
                  </div>
                </div>
              </div>
              <div className="space-y-4 flex-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground font-medium flex items-center gap-2">
                    <Clock className="h-3.5 w-3.5" />
                    Retention Policy
                  </span>
                  <span className="font-bold">{p.ttl}</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground font-medium flex items-center gap-2">
                    <Database className="h-3.5 w-3.5" />
                    Active Archives
                  </span>
                  <span className="font-bold">{p.archives}</span>
                </div>
                <div className="pt-2">
                  <p className="text-[10px] uppercase tracking-widest text-muted-foreground font-bold mb-1">Storage Provider</p>
                  <p className="text-sm font-semibold text-primary/80">{p.storage}</p>
                </div>
              </div>
              <div className="mt-6 pt-6 border-t border-border/30 flex items-center justify-between">
                 <button className="text-xs font-bold text-primary hover:underline flex items-center gap-1">
                    Edit Rules
                    <ArrowUpRight className="h-3 w-3" />
                 </button>
                 <span className="text-[10px] text-muted-foreground font-medium italic">Updated 2h ago</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
