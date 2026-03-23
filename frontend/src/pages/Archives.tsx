import React from 'react'
import { Archive, Search, Filter, Download, MoreVertical, FileText, Database, Shield, Trash2, ExternalLink } from 'lucide-react'

export function Archives() {
  const archives = [
    { id: 'arc-1024', name: 'user_logs_2024_03.sql', bytes: '14.2 MB', policy: 'System Logs', status: 'Active', color: 'text-blue-500', date: '3 hours ago' },
    { id: 'arc-1025', name: 'customer_backup_v2.tar.gz', bytes: '1.2 GB', policy: 'User Data TTL', status: 'Active', color: 'text-emerald-500', date: '5 hours ago' },
    { id: 'arc-1026', name: 'marketing_assets_final.zip', bytes: '450.5 MB', policy: 'Marketing Assets', status: 'Archived', color: 'text-rose-500', date: 'Yesterday' },
    { id: 'arc-1027', name: 'access_logs_debug.txt', bytes: '2.1 MB', policy: 'System Logs', status: 'Active', color: 'text-blue-500', date: '2 days ago' },
  ]

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <header className="flex items-end justify-between">
        <div className="space-y-2">
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">Archive Management</h2>
          <p className="text-muted-foreground">Monitor and managing all archived data across storage providers.</p>
        </div>
        <div className="flex gap-4">
          <button className="flex items-center gap-2 px-6 py-3 border border-border bg-card/50 backdrop-blur-md rounded-xl font-bold text-sm hover:bg-accent transition-all duration-300">
            <Filter className="h-4 w-4" />
            Advanced Filter
          </button>
          <button className="flex items-center gap-2 px-6 py-3 bg-secondary text-secondary-foreground font-bold text-sm rounded-xl shadow-lg border border-border hover:scale-[1.02] transition-all duration-300">
            <Download className="h-4 w-4" />
            Export Audit Log
          </button>
        </div>
      </header>

      <div className="bg-card/40 backdrop-blur-md border border-border/50 rounded-2xl overflow-hidden shadow-sm">
        <div className="p-6 border-b border-border/40 flex items-center justify-between">
           <div className="relative group max-w-sm flex-1">
             <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
             <input className="w-full pl-10 pr-4 py-2 bg-transparent text-sm focus:outline-none" placeholder="Search archives by name or ID..." />
           </div>
           <div className="flex items-center gap-3">
             <span className="text-xs text-muted-foreground font-medium">85 records found</span>
             <div className="h-6 w-px bg-border mx-2"></div>
             <div className="flex bg-accent/30 rounded-lg p-1">
               <button className="px-3 py-1.5 text-xs font-bold rounded-md bg-card shadow-sm">List</button>
               <button className="px-3 py-1.5 text-xs font-bold text-muted-foreground hover:bg-card/50 rounded-md">Grid</button>
             </div>
           </div>
        </div>

        <table className="w-full text-left">
          <thead>
            <tr className="bg-muted/10 text-[10px] uppercase tracking-widest font-bold text-muted-foreground border-b border-border/40">
              <th className="px-8 py-4">Data Identity</th>
              <th className="px-8 py-4">Policy</th>
              <th className="px-8 py-4">Size</th>
              <th className="px-8 py-4">Status</th>
              <th className="px-8 py-4 text-right pr-12">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/30">
            {archives.map((a, i) => (
              <tr key={i} className="group hover:bg-accent/40 transition-colors cursor-pointer">
                <td className="px-8 py-5">
                  <div className="flex items-center gap-4">
                    <div className={`p-2 rounded-xl bg-accent ${a.color} group-hover:scale-110 transition-transform`}>
                      <FileText className="h-5 w-5" />
                    </div>
                    <div>
                      <p className="text-sm font-bold group-hover:text-primary transition-colors flex items-center gap-2">
                        {a.name}
                        <ExternalLink className="h-3 w-3 opacity-0 group-hover:opacity-40 transition-opacity" />
                      </p>
                      <p className="text-[10px] text-muted-foreground font-medium mt-1 uppercase tracking-tighter">ID: {a.id} • Created {a.date}</p>
                    </div>
                  </div>
                </td>
                <td className="px-8 py-5">
                   <div className="flex items-center gap-2">
                     <Shield className="h-4 w-4 text-primary/60" />
                     <span className="text-sm font-medium">{a.policy}</span>
                   </div>
                </td>
                <td className="px-8 py-5">
                   <div className="flex items-center gap-2">
                     <Database className="h-4 w-4 text-amber-500/60" />
                     <span className="text-sm font-semibold">{a.bytes}</span>
                   </div>
                </td>
                <td className="px-8 py-5">
                   <span className={`text-[10px] font-bold px-3 py-1 rounded-full ${a.status === 'Active' ? 'bg-emerald-500/10 text-emerald-500 ring-1 ring-emerald-500/20' : 'bg-rose-500/10 text-rose-500 ring-1 ring-rose-500/20'}`}>
                     {a.status}
                   </span>
                </td>
                <td className="px-8 py-5 pr-12 text-right">
                   <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity translate-x-2 group-hover:translate-x-0 transition-transform duration-300">
                     <button className="p-2 text-primary hover:bg-primary/10 rounded-lg transition-colors shadow-sm bg-card/80 border border-border/30 backdrop-blur-md">
                        <Download className="h-4 w-4" />
                     </button>
                     <button className="p-2 text-rose-500 hover:bg-rose-500/10 rounded-lg transition-colors shadow-sm bg-card/80 border border-border/30 backdrop-blur-md">
                        <Trash2 className="h-4 w-4" />
                     </button>
                     <button className="p-2 text-muted-foreground hover:bg-accent rounded-lg transition-colors shadow-sm bg-card/80 border border-border/30 backdrop-blur-md">
                        <MoreVertical className="h-4 w-4" />
                     </button>
                   </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
