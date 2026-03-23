import React, { useState } from 'react'
import { 
  Archive as ArchiveIcon, 
  Search, 
  Filter, 
  Download, 
  MoreVertical, 
  FileText, 
  Database, 
  Shield, 
  Trash2, 
  ExternalLink,
  Plus,
  RefreshCw,
  X
} from 'lucide-react'
import { FileUpload } from '../components/FileUpload'
import { cn } from '../lib/utils'

export function Archives() {
  const [isUploadOpen, setIsUploadOpen] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)

  const archives = [
    { id: 'arc-1024', name: 'user_logs_2024_03.sql', bytes: '14.2 MB', policy: 'System Logs', status: 'Active', color: 'text-blue-500', date: '3 hours ago' },
    { id: 'arc-1025', name: 'customer_backup_v2.tar.gz', bytes: '1.2 GB', policy: 'User Data TTL', status: 'Active', color: 'text-emerald-500', date: '5 hours ago' },
    { id: 'arc-1026', name: 'marketing_assets_final.zip', bytes: '450.5 MB', policy: 'Marketing Assets', status: 'Archived', color: 'text-rose-500', date: 'Yesterday' },
    { id: 'arc-1027', name: 'access_logs_debug.txt', bytes: '2.1 MB', policy: 'System Logs', status: 'Active', color: 'text-blue-500', date: '2 days ago' },
  ]

  const handleRefresh = () => {
    setIsRefreshing(true)
    setTimeout(() => setIsRefreshing(false), 1500)
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500 relative">
      {/* Header section with refined aesthetics */}
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">Archive Management</h2>
          <p className="text-muted-foreground flex items-center gap-2">
            <ArchiveIcon className="h-4 w-4" />
            Managing global data retention and chain-anchored storage.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button 
             onClick={handleRefresh}
             className="p-3 bg-secondary text-secondary-foreground rounded-2xl border border-border shadow-sm hover:bg-accent transition-all group"
          >
            <RefreshCw className={cn("h-5 w-5", isRefreshing && "animate-spin")} />
          </button>
          <button 
            onClick={() => setIsUploadOpen(true)}
            className="flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground font-bold text-sm rounded-2xl shadow-lg shadow-primary/20 hover:scale-[1.02] active:scale-[0.98] transition-all group"
          >
            <Plus className="h-5 w-5 group-hover:rotate-90 transition-transform duration-300" />
            Create New Archive
          </button>
        </div>
      </header>

      {/* Upload Overlay with premium transition */}
      {isUploadOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-background/80 backdrop-blur-xl animate-in fade-in duration-300 overflow-y-auto">
          <div className="bg-card w-full max-w-2xl rounded-[2.5rem] border border-border/50 shadow-2xl overflow-hidden relative animate-in zoom-in-95 duration-300 my-8">
             <div className="p-8 border-b border-border/40 flex items-center justify-between bg-accent/20">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-primary text-primary-foreground rounded-2xl">
                    <ArchiveIcon className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold tracking-tight leading-none">Initialize Archival Pack</h3>
                    <p className="text-xs text-muted-foreground mt-2 font-medium">Upload datasets for chain validation and retention.</p>
                  </div>
                </div>
                <button 
                  onClick={() => setIsUploadOpen(false)}
                  className="p-2 hover:bg-card/50 rounded-xl text-muted-foreground hover:text-foreground transition-all border border-transparent hover:border-border/60"
                >
                  <X className="h-6 w-6" />
                </button>
             </div>
             
             <div className="p-8">
               <FileUpload onUploadComplete={() => {
                 // Simulated logic
                 setTimeout(() => setIsUploadOpen(false), 1000)
               }} />
             </div>

             <div className="p-8 bg-accent/10 border-t border-border/30 flex justify-end gap-3">
               <button 
                  onClick={() => setIsUploadOpen(false)}
                  className="px-6 py-3 text-sm font-bold hover:bg-accent rounded-2xl transition-colors"
                >
                  Cancel & Dismiss
               </button>
               <button className="px-8 py-3 bg-primary text-primary-foreground font-bold text-sm rounded-2xl shadow-lg hover:scale-[1.02] transition-all">
                  Proceed to Finalize
               </button>
             </div>
          </div>
        </div>
      )}

      {/* Main Filter and Search UI */}
      <div className="grid grid-cols-1 gap-6">
        <div className="bg-card/40 backdrop-blur-md border border-border/50 rounded-3xl overflow-hidden shadow-sm">
          <div className="p-8 border-b border-border/40 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-6">
             <div className="relative group max-w-md flex-1">
               <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
               <input className="w-full pl-10 pr-4 py-3 bg-accent/30 rounded-2xl text-sm focus:outline-none placeholder:text-muted-foreground border border-transparent focus:border-primary/20 transition-all font-medium" placeholder="Search archives by name or ID..." />
             </div>
             <div className="flex items-center gap-4">
               <button className="flex items-center gap-2 px-5 py-2.5 border border-border bg-card/60 rounded-xl font-bold text-xs hover:bg-accent transition-all">
                 <Filter className="h-4 w-4" />
                 Advanced Filtering
               </button>
               <div className="h-4 w-px bg-border mx-1"></div>
               <span className="text-xs text-muted-foreground font-bold uppercase tracking-widest leading-relaxed">Archives: <span className="text-foreground">1,240 Total</span></span>
             </div>
          </div>

          <table className="w-full text-left">
            <thead>
              <tr className="bg-muted/10 text-[10px] uppercase tracking-widest font-bold text-muted-foreground border-b border-border/40">
                <th className="px-8 py-6">Data Identity</th>
                <th className="px-8 py-6">Storage Policy</th>
                <th className="px-8 py-6">Footprint</th>
                <th className="px-8 py-6">Chain Status</th>
                <th className="px-8 py-6 text-right pr-12">Controls</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/20">
              {archives.map((a, i) => (
                <tr key={i} className="group hover:bg-accent/40 transition-colors cursor-pointer border-l-4 border-l-transparent hover:border-l-primary duration-300">
                  <td className="px-8 py-6">
                    <div className="flex items-center gap-5">
                      <div className={`p-3 rounded-2xl bg-accent ${a.color} group-hover:scale-110 transition-transform shadow-inner`}>
                        <FileText className="h-6 w-6" />
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
                  <td className="px-8 py-6">
                     <div className="flex items-center gap-3">
                       <Shield className="h-4 w-4 text-primary/60" />
                       <span className="text-xs font-bold text-foreground/80">{a.policy}</span>
                     </div>
                  </td>
                  <td className="px-8 py-6">
                     <div className="flex items-center gap-3">
                       <Database className="h-4 w-4 text-amber-500/60" />
                       <span className="text-xs font-bold text-foreground/80 leading-relaxed font-mono">{a.bytes}</span>
                     </div>
                  </td>
                  <td className="px-8 py-6">
                     <span className={`text-[10px] font-bold px-3 py-1.5 rounded-full ${a.status === 'Active' ? 'bg-emerald-500/10 text-emerald-500 ring-1 ring-emerald-500/20 shadow-[0_0_15px_-5px_theme(colors.emerald.400)]' : 'bg-rose-500/10 text-rose-500 ring-1 ring-rose-500/20 shadow-[0_0_15px_-5px_theme(colors.rose.400)]'}`}>
                       {a.status.toUpperCase()}
                     </span>
                  </td>
                  <td className="px-8 py-6 pr-12 text-right">
                     <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity translate-x-3 group-hover:translate-x-0 group-hover:transition-all duration-300">
                       <button className="p-2.5 text-primary hover:bg-primary/10 rounded-xl transition-all shadow-sm bg-card/80 border border-border/30 backdrop-blur-md">
                          <Download className="h-4 w-4" />
                       </button>
                       <button className="p-2.5 text-rose-500 hover:bg-rose-500/10 rounded-xl transition-all shadow-sm bg-card/80 border border-border/30 backdrop-blur-md">
                          <Trash2 className="h-4 w-4" />
                       </button>
                       <button className="p-2.5 text-muted-foreground hover:bg-accent rounded-xl transition-all shadow-sm bg-card/80 border border-border/30 backdrop-blur-md">
                          <MoreVertical className="h-4 w-4" />
                       </button>
                     </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="p-8 border-t border-border/20 bg-muted/5 flex items-center justify-between">
             <p className="text-xs text-muted-foreground font-medium italic pr-4 overflow-hidden">Showing partial dataset of optimized records archived on Stellar Ledger.</p>
             <button className="text-xs font-bold text-primary hover:underline whitespace-nowrap">View Detailed Audit Logs →</button>
          </div>
        </div>
      </div>
    </div>
  )
}
