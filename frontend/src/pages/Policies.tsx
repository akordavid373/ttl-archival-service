import React from 'react'
import { ShieldCheck, Plus, Search, MoreHorizontal, Clock, ArrowUpRight, Zap } from 'lucide-react'

export function Policies() {
  const policies = [
    { name: 'User Data TTL', ttl: '30 Days', status: 'Active', storage: 'S3 Standard', archive_count: 124, color: 'text-primary' },
    { name: 'System Logs', ttl: '7 Days', status: 'Active', storage: 'Glacier Deep', archive_count: 850, color: 'text-amber-500' },
    { name: 'Marketing Assets', ttl: '365 Days', status: 'Inactive', storage: 'S3 Standard-IA', archive_count: 54, color: 'text-rose-500' },
  ]

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <header className="flex items-end justify-between">
        <div className="space-y-2">
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">Archival Policies</h2>
          <p className="text-muted-foreground">Manage rules, TTL settings, and automated archival workflows.</p>
        </div>
        <button className="flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground font-bold text-sm rounded-xl shadow-lg shadow-primary/20 hover:scale-[1.02] transition-all duration-300 group">
          <Plus className="h-5 w-5 group-hover:rotate-90 transition-transform duration-300" />
          Create New Policy
        </button>
      </header>

      <div className="flex items-center gap-4 bg-card/40 backdrop-blur-md p-4 mt-6 rounded-2xl border border-border/50">
        <div className="flex-1 relative group">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
          <input className="w-full pl-10 pr-4 py-2 bg-transparent text-sm focus:outline-none placeholder:text-muted-foreground" placeholder="Search policies..." />
        </div>
        <div className="h-6 w-px bg-border"></div>
        <select className="bg-transparent text-xs font-semibold px-4 cursor-pointer focus:outline-none">
          <option>All Status</option>
          <option>Active</option>
          <option>Inactive</option>
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {policies.map((p, i) => (
          <div key={i} className="group p-8 rounded-3xl bg-card border border-border/50 hover:border-primary/20 hover:shadow-2xl hover:shadow-primary/5 transition-all duration-300 relative overflow-hidden">
            <div className={`absolute top-0 left-0 w-1 h-full ${i === 0 ? 'bg-primary' : i === 1 ? 'bg-amber-500' : 'bg-rose-500'}`}></div>
            <div className="flex justify-between items-start mb-6">
              <div className={`p-3 rounded-2xl bg-accent text-primary group-hover:scale-110 transition-transform`}>
                <ShieldCheck className={`h-6 w-6 ${p.color}`} />
              </div>
              <button className="p-2 text-muted-foreground hover:bg-accent rounded-xl transition-colors">
                <MoreHorizontal className="h-5 w-5" />
              </button>
            </div>
            <h3 className="text-xl font-bold mb-2 group-hover:text-primary transition-colors">{p.name}</h3>
            <div className="grid grid-cols-2 gap-y-4 gap-x-2 mt-6">
               <div className="space-y-1">
                 <p className="text-[10px] uppercase tracking-widest text-muted-foreground font-bold">Retention</p>
                 <p className="text-sm font-semibold flex items-center gap-2">
                   <Clock className="h-3 w-3" />
                   {p.ttl}
                 </p>
               </div>
               <div className="space-y-1">
                 <p className="text-[10px] uppercase tracking-widest text-muted-foreground font-bold">Archives</p>
                 <p className="text-sm font-semibold flex items-center gap-2">
                   <Zap className="h-3 w-3 text-amber-500" />
                   {p.archive_count} records
                 </p>
               </div>
               <div className="space-y-1 col-span-2 mt-2">
                 <p className="text-[10px] uppercase tracking-widest text-muted-foreground font-bold">Storage Provider</p>
                 <p className="text-sm font-semibold text-primary/80">{p.storage}</p>
               </div>
            </div>
            <div className="mt-8 flex items-center justify-between pt-6 border-t border-border/30">
              <span className={`text-[10px] font-bold px-3 py-1 rounded-full ${p.status === 'Active' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-muted text-muted-foreground'}`}>{p.status}</span>
              <button className="text-[10px] font-bold text-primary flex items-center gap-1 hover:underline">
                View Reports
                <ArrowUpRight className="h-3 w-3" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
